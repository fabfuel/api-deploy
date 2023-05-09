import os
from api_deploy.schema import Schema


def test_schema_from_string():
    schema = Schema('''
        lorem: ipsum
        info:
          title: API Deployment
    ''')
    assert schema['lorem'] == 'ipsum'
    assert schema['info']['title'] == 'API Deployment'


def test_schema_from_file():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, '../openapi/simple_source.yml')
    print(filename)
    schema = Schema.from_file(filename)
    assert schema['info']['title'] == 'Test'
