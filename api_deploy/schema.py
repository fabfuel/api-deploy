from typing import Dict
import yaml
import re

yaml.Dumper.ignore_aliases = lambda *args: True


# pyyaml interprets strings which are octals as int so we're overriding this behavior
def represent_str(self, data):
    """Custom string representer that forces quoting for strings with leading zeros"""
    # Only quote strings that look like numbers with leading zeros (but not just "0")
    if re.match(r'^0[0-9]+$', data):
        return self.represent_scalar('tag:yaml.org,2002:str', data, style="'")

    # Use the default behavior for all other strings
    return yaml.Dumper.represent_str(self, data)


# Attach custom representer to the default YAML dumper
yaml.add_representer(str, represent_str)


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
            'x-amazon-apigateway-minimum-compression-size': 0                                   ,
        }
        return yaml.dump(data, sort_keys=sort_keys)
