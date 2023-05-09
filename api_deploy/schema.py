from typing import TextIO, Dict
import yaml

yaml.Dumper.ignore_aliases = lambda *args: True


class Schema(Dict):
    def __init__(self, schema: str | TextIO) -> None:
        schema = yaml.load(schema, yaml.Loader)
        super().__init__(schema)

    @staticmethod
    def from_file(file_path):
        with open(file_path, 'r') as schema_file:
            return Schema(schema_file)

    def to_file(self, file_path):
        with open(file_path, 'w') as target:
            target.write(self.dump())

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

    def __repr__(self):
        return self.dump()
