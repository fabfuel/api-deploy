from api_deploy.config import Config
from api_deploy.processors.abstract_processor import AbstractProcessor
from api_deploy.schema import Schema


class StrictProcessor(AbstractProcessor):

    def __init__(self, config: Config, enabled: bool, blocklist: list, **kwargs) -> None:
        self.enabled = enabled
        self.blocklist = blocklist

    def process(self, schema: Schema) -> Schema:
        if not self.enabled:
            return schema

        schemas = schema['components']['schemas']

        for name in schemas:
            model = schemas[name]
            self.enable_strictness(model, True)

        return schema

    def enable_strictness(self, model, add_required):
        if model.get('type') != 'object':
            return model

        required = []

        for property in model.get('properties', {}):
            required.append(property)

            if property in self.blocklist:
                add_required_deep = False
            else:
                add_required_deep = True

            if model['properties'][property].get('type') == 'array':
                model['properties'][property]['items'] = self.enable_strictness(model['properties'][property]['items'], add_required_deep)

            model['properties'][property] = self.enable_strictness(model['properties'][property], add_required_deep)

        if not model.get('additionalProperties'):
            model['additionalProperties'] = False

        if add_required and required:
            model['required'] = required

        return model