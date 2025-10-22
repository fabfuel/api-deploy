from typing import Dict
import io
import ruyaml

_yaml = ruyaml.YAML(typ='safe')
# avoid YAML aliases/anchors in output
_yaml.representer.ignore_aliases = lambda *args: True


def _dump_to_string(data, sort_keys=False):
    # Optional key sorting to mimic previous behavior when requested
    def _sort(obj):
        if isinstance(obj, dict):
            # sort by key, recursively
            return {k: _sort(obj[k]) for k in sorted(obj.keys())}
        if isinstance(obj, list):
            return [
                _sort(i) for i in obj
            ]
        return obj

    if sort_keys:
        data = _sort(data)
    stream = io.StringIO()
    _yaml.dump(data, stream)
    return stream.getvalue()


class YamlDict(Dict):
    def __init__(self, schema) -> None:
        # ruyaml.YAML.load accepts str, bytes, and file-like objects
        content = _yaml.load(schema) or {}
        super().__init__(content)

    @classmethod
    def from_file(cls, file_path):
        with open(file_path, 'r') as schema_file:
            return cls(schema_file)

    def to_file(self, file_path):
        with open(file_path, 'w') as target:
            target.write(self.dump())

    def dump(self, sort_keys=False):
        return _dump_to_string(self, sort_keys=sort_keys)


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
        return _dump_to_string(data, sort_keys=sort_keys)
