from typing import TextIO, Dict
import yaml

from api_deploy.schema import YamlDict


class ConfigFile(YamlDict):
    ...


class Config(Dict):
    def __init__(self, config_file: ConfigFile) -> None:
        default_config = {
            'headers': {
                'request': {},
                'response': {},
            },
            'gateway': {},
            'cors': {},
        }
        default_config['headers']['request'] = config_file.get('headers', {}).get('request', [])
        default_config['headers']['response'] = config_file.get('headers', {}).get('response', [])

        default_config['gateway'].setdefault('integration_host', config_file.get('gateway', {}).get('integrationHost', ''))
        default_config['gateway'].setdefault('connection_id', config_file.get('gateway', {}).get('connectionId', ''))

        default_config['cors'].setdefault('allow_origin', config_file.get('cors', {}).get('origin', '*'))

        super().__init__(default_config)

    @classmethod
    def from_file(cls, file_path):
        config_file = ConfigFile.from_file(file_path)
        return cls(config_file)
