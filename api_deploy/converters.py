from abc import ABC, abstractmethod
from copy import deepcopy
from mergedeep import merge

from api_deploy.config import Config
from api_deploy.schema import Schema


class AbstractProcessor(ABC):

    @abstractmethod
    def __init__(self, **kwargs):
        ...

    @abstractmethod
    def process(self, schema: Schema) -> Schema:
        ...


class ProcessManager:
    def __init__(self) -> None:
        super().__init__()
        self.__processors: [AbstractProcessor] = []

    @classmethod
    def default(cls, config: Config):
        default_manager = cls()
        default_manager.register(StaticFileProcessor(**config['static']))
        default_manager.register(PassthroughProcessor(**config['headers']))
        default_manager.register(FlattenProcessor())
        default_manager.register(ApiGatewayProcessor(**config['gateway']))
        default_manager.register(CorsProcessor(headers=config['headers'], **config['cors']))
        return default_manager

    def register(self, processor: AbstractProcessor):
        self.__processors.append(processor)

    def process(self, original_schema: Schema) -> Schema:
        processed_schema = deepcopy(original_schema)
        for processor in self.__processors:
            processed_schema = processor.process(processed_schema)
            if not isinstance(processed_schema, Schema):
                raise NotImplementedError('Processor did not return processed schema')
        return processed_schema


class FlattenProcessor(AbstractProcessor):

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.used_refs = set()

    def process(self, source: Schema) -> Schema:
        target = deepcopy(source)
        target['servers'] = [source['servers'][0]]

        # Enforce replacement of all $refs from parameters
        self.replace_refs_dict(target['components'].get('parameters', {}), target, True, True)

        # Replace $refs in all components – run twice to catch all nesting
        self.replace_refs_dict(target['components'], target)
        self.replace_refs_dict(target['components'], target)

        # Replace $refs in paths
        self.replace_refs_dict(target['paths'], target)

        try:
            del target['components']['parameters']
        except KeyError:
            ...
        try:
            del target['components']['responses']
        except KeyError:
            ...

        target['components']['schemas'] = self.get_to_used_schemas(target['components']['schemas'], self.used_refs)

        return target

    def replace_refs_dict(self, node, schema, replace_ref=True, enforce_replace=False):
        if self.is_ref(node) and (replace_ref or enforce_replace):
            return self.lookup_ref(node, schema)
        elif self.is_ref(node):
            self.used_refs.add(self.get_ref_model_name(node['$ref']))
        if self.is_all_of(node):
            return self.merge_all_of(node, schema)
        for key in node.keys():
            if type(node[key]) is dict:
                # Do not replace main level refs (response models)
                replace_ref = key != 'schema'
                node[key] = self.replace_refs_dict(node[key], schema, replace_ref, enforce_replace)
            if type(node[key]) is list:
                node[key] = self.replace_refs_list(node[key], schema)
        return node

    @staticmethod
    def get_to_used_schemas(schemas: dict, used_refs: set):
        used_schemas = {}
        for model in schemas:
            if model in used_refs:
                used_schemas[model] = schemas[model]
        return used_schemas

    @staticmethod
    def get_ref_model_name(ref):
        return ref.split('/')[-1]

    @staticmethod
    def lookup_ref(ref: dict, schema: Schema):
        name = ref['$ref']
        components, component_type, model = name.split('/')[1:]
        return schema[components][component_type].get(model)

    @staticmethod
    def first_key(node):
        try:
            return list(node.keys())[0]
        except (IndexError, AttributeError):
            return None

    def is_ref(self, node):
        return self.first_key(node) == '$ref'

    def is_all_of(self, node):
        return self.first_key(node) == 'allOf'

    def replace_refs_list(self, node, schema: Schema):
        new_list = []
        for el in node:
            if self.is_ref(el):
                el = self.lookup_ref(el, schema)
                new_list.append(el)
            else:
                new_list.append(el)
        return new_list

    def merge_all_of(self, node, schema: Schema):
        to_merge = []
        for sub_node in node['allOf']:
            if self.is_ref(sub_node):
                to_merge.append(self.lookup_ref(deepcopy(sub_node), deepcopy(schema)))
            else:
                to_merge.append(sub_node)
        return merge(*to_merge)


class ApiGatewayProcessor(AbstractProcessor):
    def __init__(self, integration_host, connection_id, **kwargs) -> None:
        super().__init__()
        self.integration_host = integration_host
        self.connection_id = connection_id

    def process(self, schema: Schema) -> Schema:
        for path in schema['paths']:
            for method in schema['paths'][path]:
                endpoint = schema['paths'][path][method]
                endpoint['x-amazon-apigateway-integration'] = {
                    'type': 'http',
                    'connectionId': self.connection_id,
                    'httpMethod': str(method).upper(),
                    'uri': self.integration_host + path,
                    'passthroughBehavior': 'when_no_match',
                    'connectionType': 'VPC_LINK',
                    'responses': self._get_response_codes(schema, path, method),
                    'requestParameters': self._get_request_parameters(schema, path, method),
                }
        return schema

    def _get_response_codes(self, schema, path, method):
        responses = {
            'default': {
                'statusCode': '500'
            }
        }
        for response_code in schema['paths'][path][method]['responses']:
            if response_code == '500':
                continue
            responses[response_code] = {
                'statusCode': response_code
            }
            responses[response_code]['responseParameters'] = self._get_response_parameters(schema,
                                                                                           path,
                                                                                           method,
                                                                                           response_code)

        return responses

    def _get_response_parameters(self, schema, path, method, response_code):
        response_headers = schema['paths'][path][method]['responses'].get(response_code, {}).get('headers', {})
        response_parameters = {}
        for header in response_headers:
            response_parameters[f'method.response.header.{header}'] = f'integration.response.header.{header}'

        return response_parameters

    @staticmethod
    def _get_request_parameters(schema, path, method):
        parameters = {
            'integration.request.header.User-Agent': 'context.identity.userAgent',
            'integration.request.header.X-Forwarded-For': 'context.identity.sourceIp',
            'integration.request.header.X-Stage': 'context.stage',
        }

        for parameter in schema['paths'][path][method].get('parameters', []):
            source_integration = parameter.get('in')
            source_method = parameter.get('in')

            if parameter.get('in') == 'query':
                source_integration = 'querystring'
                if parameter.get('schema', {}).get('type') == 'array':
                    source_method = 'multivaluequerystring'
                else:
                    source_method = 'querystring'

            name = parameter.get('name')
            parameters[f'integration.request.{source_integration}.{name}'] = f'method.request.{source_method}.{name}'

        return parameters


class CorsProcessor(AbstractProcessor):
    def __init__(self, headers, allow_origin, **kwargs) -> None:
        super().__init__()
        self.allow_headers = headers['request']
        self.allow_origin = allow_origin

    def process(self, schema: Schema) -> Schema:
        schema['tags'].append({
            'name': 'CORS',
            'description': 'CORS configuration endpoints',
        })

        allow_methods = 'OPTIONS'

        for path in schema['paths']:
            path_params = []
            path_param_names = []
            methods = list(schema['paths'][path].keys())
            methods.append('options')
            allow_headers = set(self.allow_headers)
            expose_headers = {}

            for method in schema['paths'][path]:
                allow_methods = ','.join([m.upper() for m in methods])

                endpoint = schema['paths'][path][method]

                for parameter in endpoint.get('parameters', []):
                    if parameter.get('in') == 'path' and parameter['name'] not in path_param_names:
                        path_params.append(parameter)
                        path_param_names.append(parameter['name'])

                for response_code in endpoint['responses']:
                    expose_headers[response_code] = set()

                    endpoint['responses'][response_code].setdefault('headers', {})

                    for response_header in endpoint['responses'][response_code]['headers']:
                        if response_header != 'Access-Control-Allow-Origin' and response_header != 'Access-Control-Expose-Headers':
                            expose_headers[response_code].add(response_header)
                    if expose_headers[response_code]:
                        endpoint['responses'][response_code]['headers']['Access-Control-Expose-Headers'] = {
                            'schema': {
                                'type': 'string',
                                'example': f'{",".join(expose_headers[response_code])}',
                            }
                        }

                    endpoint['responses'][response_code]['headers']['Access-Control-Allow-Origin'] = {
                        'schema': {
                            'type': 'string',
                            'example': f'{self.allow_origin}',
                        }
                    }

                gw_responses = endpoint['x-amazon-apigateway-integration']['responses']
                for status_code in gw_responses:
                    gw_responses[status_code].setdefault('responseParameters', {})
                    gw_responses[status_code]['responseParameters']['method.response.header.Access-Control-Allow-Origin'] = f'\'{self.allow_origin}\''

                    if expose_headers.get(status_code):
                        gw_responses[status_code]['responseParameters']['method.response.header.Access-Control-Expose-Headers'] = f'\'{",".join(expose_headers.get(status_code))}\''

            if 'options' in schema['paths'][path]:
                continue

            allow_headers = list(allow_headers)
            allow_headers.sort()

            options_method = {
                'operationId': path + 'CORS',
                'description': path + ' CORS',
                'tags': ['CORS'],
                'responses': {
                    '200': {
                        'description': '200',
                        'headers': {
                            'Access-Control-Allow-Origin': {
                                'schema': {
                                    'type': 'string',
                                    'example': f'{self.allow_origin}',
                                },
                            },
                            'Access-Control-Allow-Methods': {
                                'schema': {
                                    'type': 'string',
                                    'example': f'{allow_methods}',
                                },
                            },
                            'Access-Control-Allow-Headers': {
                                'schema': {
                                    'type': 'string',
                                    'example': f'{",".join(allow_headers)}',
                                },
                            },
                        },
                    },
                },
                'x-amazon-apigateway-integration': {
                    'responses': {
                        'default': {
                            'statusCode': '200',
                            'responseParameters': {
                                'method.response.header.Access-Control-Allow-Methods': f'\'{allow_methods}\'',
                                'method.response.header.Access-Control-Allow-Headers': f'\'{",".join(allow_headers)}\'',
                                'method.response.header.Access-Control-Allow-Origin': f'\'{self.allow_origin}\'',
                            }
                        }
                    },
                    'requestTemplates': {
                        'application/json': "{\"statusCode\": 200}"
                    },
                    'passthroughBehavior': "when_no_match",
                    'type': "mock",
                }
            }

            if path_params:
                options_method['parameters'] = path_params

            schema['paths'][path]['options'] = options_method
        return schema


class PassthroughProcessor(AbstractProcessor):
    def __init__(self, request, response, **kwargs) -> None:
        self.request_headers: [str] = request
        self.response_headers: [str] = response
        super().__init__()

    @staticmethod
    def add_parameter(params_list, name, location, description=None):
        param = {
            'name': name,
            'in': location,
            'required': False,
            'schema': {
                'type': 'string',
            }
        }
        if description:
            param['description'] = description
        params_list.append(param)

    def process(self, schema: Schema) -> Schema:
        for path in schema['paths']:
            for method in schema['paths'][path]:
                endpoint = schema['paths'][path][method]
                params = endpoint.setdefault('parameters', [])

                for header in self.request_headers:
                    self.add_parameter(params, header, 'header')

        return schema


class StaticFileProcessor(AbstractProcessor):

    def __init__(self, files: [str]) -> None:
        self.files = files
        super().__init__()

    def process(self, schema: Schema) -> Schema:
        if len(self.files) > 0:
            schema['tags'].append({
                'description': 'Static file content',
                'name': 'Static Files'
            })

        for file in self.files:
            schema['paths'][f'/{file}'] = {
                'get': {
                    'tags': ['Static Files'],
                    'responses': {
                        '200': {
                        'description': f'Static file {file}'


                        }
                    }
                }
            }

        return schema
