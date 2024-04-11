from api_deploy.config import Config
from api_deploy.processors.abstract_processor import AbstractProcessor
from api_deploy.schema import Schema
from copy import deepcopy


class StrictProcessor(AbstractProcessor):

    def __init__(self, config: Config, enabled: bool, blocklist: list, overwrite_required: bool, **kwargs) -> None:
        self.enabled = enabled
        self.overwrite_required = overwrite_required
        self.blocklist = blocklist

    def process(self, schema: Schema) -> Schema:
        if not self.enabled:
            return schema

        schemas_to_patch = []
        for path in schema['paths']:
            for method in schema['paths'][path]:
                if method.lower() != 'patch':
                    continue
                endpoint = schema['paths'][path][method]
                schema_name = endpoint['requestBody']['content']['application/json']['schema']['$ref'].split('/')[-1]
                schemas_to_patch.append(schema_name)

        schemas = schema['components']['schemas']
        patch_models = {}

        for name in schemas:
            model = schemas[name]

            if name in schemas_to_patch:
                model_patch_name = name + 'Patch'
                model_patch = deepcopy(schemas[name])
                patch_models[model_patch_name] = model_patch
                self.enable_strictness(model_patch, False, True)

            self.enable_strictness(model, True)

        schemas.update(patch_models)

        # Use patch models instead of original models for PATCH endpoints
        for path in schema['paths']:
            for method in schema['paths'][path]:
                if method.lower() != 'patch':
                    continue

                # Ensure PATCH endpoint is an independent copy of the original endpoint
                schema['paths'][path][method] = deepcopy(schema['paths'][path][method])

                endpoint = schema['paths'][path][method]
                endpoint_schema = endpoint['requestBody']['content']['application/json']['schema']
                endpoint_schema['$ref'] = endpoint_schema['$ref'] + 'Patch'

        return schema

    def enable_strictness(self, model, add_required, remove_required=False):
        if 'oneOf' in model:
            for one_of_model in model['oneOf']:
                self.enable_strictness(one_of_model, True)

        if 'allOf' in model:
            for all_of_model in model['allOf']:
                self.enable_strictness(all_of_model, True)

        if model.get('type') != 'object':
            return model

        if model.get('x-not-strict'):
            del model['x-not-strict']
            return model

        if model.get('x-not-required'):
            add_required = False
            del model['x-not-required']

        if 'required' in model and not self.overwrite_required:
            add_required = False

        required = []

        for property in model.get('properties', {}):
            required.append(property)

            if property in self.blocklist:
                add_required_deep = False
            else:
                add_required_deep = True

            if model['properties'][property].get('type') == 'array':
                model['properties'][property]['items'] = self.enable_strictness(model['properties'][property]['items'], add_required_deep, remove_required)

            model['properties'][property] = self.enable_strictness(model['properties'][property], add_required_deep, remove_required)

        if not model.get('additionalProperties'):
            model['additionalProperties'] = False

        if add_required and required:
            model['required'] = required

        if len(model.get('required', [])) == 0:
            remove_required = True

        if remove_required:
            model.pop('required', None)

        return model
