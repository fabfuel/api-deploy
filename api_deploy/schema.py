from typing import Dict
import yaml

yaml.Dumper.ignore_aliases = lambda *args: True


class YamlDict(Dict):
    def __init__(self, schema) -> None:
        content = yaml.load(schema, yaml.Loader) or {}
        super().__init__(content)

    @classmethod
    def from_file(cls, file_path):
        with open(file_path, 'r') as schema_file:
            return cls(schema_file)

    def to_file(self, file_path):
        with open(file_path, 'w') as target:
            target.write(self.dump())

    def dump(self, sort_keys=False):
        return yaml.dump(self, sort_keys=sort_keys)


class Schema(YamlDict):
    def dump(self, sort_keys=False):
        data = {
            'openapi': self['openapi'],
            'info': self['info'],
            'servers': self['servers'],
            'tags': self['tags'],
            'paths': self['paths'],
            'components': self.get('components', {}),
            'x-amazon-apigateway-request-validators': self.get('x-amazon-apigateway-request-validators', {}),
        }
        return yaml.dump(data, sort_keys=sort_keys)
