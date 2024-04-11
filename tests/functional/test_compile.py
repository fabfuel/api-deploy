import os
from pytest import fixture

from api_deploy.config import Config
from api_deploy.converters import ProcessManager
from api_deploy.schema import Schema

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'api.yml')
config = Config.from_file(filename)


@fixture
def simple_source_file():
    filename = os.path.join(dirname, '../openapi/simple_source.yml')
    return Schema.from_file(filename)


@fixture
def simple_target_file():
    filename = os.path.join(dirname, '../openapi/simple_target.yml')
    return Schema.from_file(filename)


@fixture
def complex_source_file():
    filename = os.path.join(dirname, '../openapi/complex_source.yml')
    return Schema.from_file(filename)


@fixture
def complex_target_file():
    filename = os.path.join(dirname, '../openapi/complex_target.yml')
    return Schema.from_file(filename)


@fixture
def external_ref_source_file():
    filename = os.path.join(dirname, '../openapi/external_ref_source.yml')
    return Schema.from_file(filename)


@fixture
def external_ref_target_file():
    filename = os.path.join(dirname, '../openapi/external_ref_target.yml')
    return Schema.from_file(filename)


@fixture
def one_of_source_file():
    filename = os.path.join(dirname, '../openapi/one_of_source.yml')
    return Schema.from_file(filename)


@fixture
def one_of_target_file():
    filename = os.path.join(dirname, '../openapi/one_of_target.yml')
    return Schema.from_file(filename)

def test_compile_simple(simple_source_file, simple_target_file):
    manager = ProcessManager.default(config)
    processed = manager.process(simple_source_file)
    assert processed.dump(True) == simple_target_file.dump(True)


def test_compile_complex(complex_source_file, complex_target_file):
    manager = ProcessManager.default(config)
    processed = manager.process(complex_source_file)
    assert processed.dump(True) == complex_target_file.dump(True)


def test_compile_external_ref(external_ref_source_file, external_ref_target_file):
    manager = ProcessManager.default(config)
    processed = manager.process(external_ref_source_file)
    assert processed.dump(True) == external_ref_target_file.dump(True)


def test_compile_one_of(one_of_source_file, one_of_target_file):
    manager = ProcessManager.default(config)
    processed = manager.process(one_of_source_file)
    assert processed.dump(True) == one_of_target_file.dump(True)
