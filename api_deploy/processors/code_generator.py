import jinja2
import os

from api_deploy.config import Config
from api_deploy.processors.abstract_processor import AbstractProcessor
from api_deploy.schema import Schema


class CodeGenerator(AbstractProcessor):
    def __init__(self, config: Config, output: str, languages: list, **kwargs) -> None:
        self.config = config
        self.output_path = output
        self.languages = languages
        super().__init__(config)

    def process(self, schema: Schema) -> Schema:
        for language in self.languages:

            for path in schema['paths']:
                for method in schema['paths'][path]:
                    operation_id = schema['paths'][path][method].get('operationId')
                    if not operation_id:
                        continue

                    for response_code in schema['paths'][path][method]['responses']:
                        if not schema['paths'][path][method]['responses'][response_code].get('content'):
                            continue

                        if schema['paths'][path][method]['responses'][response_code]['content'].get('application/json'):
                            response_model_ref = schema['paths'][path][method]['responses'][response_code]['content']['application/json']['schema'].get('$ref')

                            if response_model_ref:
                                self.dump_model(language, schema, response_model_ref, operation_id, response_code)
                        else:
                            print(f'Warning, response {method.upper()} {path}@{response_code} has no response schema defined for content-type application/json')

                    request_body = schema['paths'][path][method].get('requestBody')
                    if request_body:
                        request_model_ref = request_body['content']['application/json']['schema'].get('$ref')
                        if request_model_ref:
                            self.dump_model(language, schema, request_model_ref, operation_id)
                        else:
                            self.dump_model(language, schema, None, operation_id, None, request_body['content']['application/json']['schema'])


        return schema

    def get_type_name(self, operation_id, response_code, submodel_name=None):
        type_name = f'{operation_id[0].upper()}{operation_id[1:]}'

        if response_code:
            type_name += f'{response_code}Response'
        else:
            type_name += 'Request'

        if submodel_name:
            type_name += submodel_name

        return type_name

    def dump_model(self, language, schema, model_ref, operation_id, response_code=None, model_schema=None):
        if not model_schema:
            components, component_type, model_name = model_ref.split('/')[1:]
            model_schema = schema[components][component_type].get(model_name)

        absolute_path = os.path.dirname(__file__)
        template_path = os.path.join(absolute_path, "templates")

        config_path = os.path.dirname(self.config.file_path)
        output_path = os.path.join(config_path, self.output_path)

        try:
            os.mkdir(output_path)
        except FileExistsError:
            ...

        environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
        template = environment.get_template(f"{language}.jinja2")

        if 'oneOf' in model_schema:
            code = ''

            submodels = []
            for one_of_model in model_schema['oneOf']:
                if '$ref' in one_of_model:
                    components, component_type, model_name = one_of_model['$ref'].split('/')[1:]
                    one_of_model_schema = schema[components][component_type].get(model_name)
                    properties = self.get_properties(one_of_model_schema, response_code is None)
                else:
                    properties = self.get_properties(one_of_model, response_code is None)

                models = [{
                    'properties': properties,
                    'discriminator_name': model_schema.get('discriminator', {}).get('propertyName') or None,
                    'discriminator_value': model_name,
                }]

                type_name = self.get_type_name(operation_id, response_code, model_name)

                code += template.render(
                    type_name=type_name,
                    response_code=response_code,
                    models=models,
                    description=model_schema.get('description', ''),
                    example=model_schema.get('example', ''),
                    discriminator_name=model_name,
                )

                submodels.append(self.get_type_name(operation_id, response_code, model_name))

            if submodels:
                compound_template = environment.get_template(f"{language}.compound.jinja2")

                code += compound_template.render(
                    type_name=self.get_type_name(operation_id, response_code),
                    submodels=submodels,
                )

        else:
            models = [{
                'properties': self.get_properties(model_schema, response_code is None),
                'discriminator_name': None,
                'discriminator_value': None,
            }]

            code = template.render(
                type_name=self.get_type_name(operation_id, response_code),
                response_code=response_code,
                models=models,
                description=model_schema.get('description', ''),
                example=model_schema.get('example', ''),
            )

        if response_code:
            file_path = f'{output_path}/{operation_id}.{response_code}.response.ts'
        else:
            file_path = f'{output_path}/{operation_id}.request.ts'

        with open(file_path, 'w') as f:
            f.write(code)

    def get_properties(self, schema, writeOnly=False):
        properties = []
        for property in schema.get('properties', []):
            property_schema = schema['properties'][property]
            property_type = property_schema.get('type', 'string')

            if writeOnly and property_schema.get('readOnly') is True:
                continue

            processed_enum = []
            if property_schema.get('enum'):
                raw_enum = property_schema['enum']
            elif property_schema.get('items', {}).get('enum'):
                raw_enum = property_schema['items']['enum']
            else:
                raw_enum = []

            if raw_enum:
                for enum in raw_enum:
                    if enum is None:
                        processed_enum.append(f"null")
                    elif isinstance(enum, str):
                        processed_enum.append(f"'{enum}'")
                    else:
                        processed_enum.append(enum)

            if property_type == 'integer':
                types = ['number']
                sub_properties = []
            elif property_type == 'array':
                types = [property_schema['items']['type']]
                if types == ['integer']:
                    types = ['number']
                sub_properties = self.get_properties(property_schema['items'], writeOnly)
            elif property_type == 'object':
                types = ['object']
                sub_properties = self.get_properties(property_schema, writeOnly)
            else:
                types = [property_type]
                sub_properties = []

            if property_schema.get('nullable') is True:
                types.append('null')

            properties.append({
                'name': property,
                'types': types,
                'required': property in schema.get('required', []),
                'description': property_schema.get('description', ''),
                'example': property_schema.get('example', ''),
                'is_array': property_type == 'array',
                'properties': sub_properties,
                'enum': processed_enum,
            })

        return properties
