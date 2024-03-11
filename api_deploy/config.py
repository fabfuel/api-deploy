from typing import Dict
from api_deploy.schema import YamlDict


class ConfigFile(YamlDict):
    ...

class Config(Dict):
    def __init__(self, config_file: ConfigFile, file_path) -> None:
        self.file_path = file_path
        default_config = {
            'headers': {
                'request': [],
                'response': [],
            },
            'strict': {},
            'gateway': {},
            'cors': {},
            'static': {
                'files': []
            },
            'generator': {
                'output': None,
                'languages': []
            },
        }
        default_config['headers']['request'] = config_file.get('headers', {}).get('request', [])
        default_config['headers']['response'] = config_file.get('headers', {}).get('response', [])

        default_config['gateway'].setdefault('integration_host',
                                             config_file.get('gateway', {}).get('integrationHost', ''))
        default_config['gateway'].setdefault('connection_id', config_file.get('gateway', {}).get('connectionId', ''))
        default_config['gateway'].setdefault('remove_scopes', config_file.get('gateway', {}).get('removeScopes', False))

        default_config['cors'].setdefault('allow_origin', config_file.get('cors', {}).get('origin', '*'))

        default_config['static']['files'] = config_file.get('static', {}).get('files', [])

        default_config['generator']['output'] = config_file.get('generator', {}).get('output')
        default_config['generator']['languages'] = config_file.get('generator', {}).get('languages', [])

        default_config['strict']['enabled'] = config_file.get('strict', {}).get('enabled', False)
        default_config['strict']['overwrite_required'] = config_file.get('strict', {}).get('overwriteRequired', True)
        default_config['strict']['blocklist'] = config_file.get('strict', {}).get('blocklist', [])

        super().__init__(default_config)

    @classmethod
    def from_file(cls, file_path):
        config_file = ConfigFile.from_file(file_path)
        return cls(config_file, file_path)
