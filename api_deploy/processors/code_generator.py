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

                        response_model_ref = schema['paths'][path][method]['responses'][response_code]['content']['application/json']['schema'].get('$ref')

                        if response_model_ref:
                            self.dump_model(language, schema, response_model_ref, operation_id, response_code)

                    request_body = schema['paths'][path][method].get('requestBody')
                    if request_body:
                        request_model_ref = request_body['content']['application/json']['schema']['$ref']
                        if request_model_ref:
                            self.dump_model(language, schema, request_model_ref, operation_id)

        return schema

    def dump_model(self, language, schema, model_ref, operation_id, response_code=None):
        components, component_type, model = model_ref.split('/')[1:]
        model_schema = schema[components][component_type].get(model)

        if model_schema['type'] != 'object':
            return

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

        code = template.render(
            operation_id=operation_id,
            response_code=response_code,
            properties=self.get_properties(model_schema, response_code is None),
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

            if writeOnly and property_schema.get('readOnly') is True:
                continue

            processed_enum = []
            if property_schema.get('enum'):
                for enum in property_schema['enum']:
                    if enum is None:
                        processed_enum.append(f"null")
                    elif property_schema['type'] == 'string':
                        processed_enum.append(f"'{enum}'")

            if property_schema['type'] == 'integer':
                types = ['number']
                sub_properties = []
            elif property_schema['type'] == 'array':
                types = [property_schema['items']['type']]
                sub_properties = self.get_properties(property_schema['items'], writeOnly)
            elif property_schema['type'] == 'object':
                types = ['object']
                sub_properties = self.get_properties(property_schema, writeOnly)
            else:
                types = [property_schema['type']]
                sub_properties = []

            if property_schema.get('nullable') is True:
                types.append('null')

            properties.append({
                'name': property,
                'types': types,
                'required': property in schema.get('required', []),
                'description': property_schema.get('description', ''),
                'example': property_schema.get('example', ''),
                'is_array': property_schema['type'] == 'array',
                'properties': sub_properties,
                'enum': processed_enum,
            })

        return properties
