import logging

import pytest  # type: ignore

import lippu.cli as cli
import lippu.api as api
from lippu import APP_ENV


def test_main_nok_too_many_arguments():
    message = r'main\(\) takes from 0 to 1 positional arguments but 2 were given'
    with pytest.raises(TypeError, match=message):
        cli.main(1, 2)


def test_main_ok_smvp(capsys):
    with pytest.raises(SystemExit, match='0'):
        cli.main(['-h'])
    out, err = capsys.readouterr()
    assert not err
    assert 'show this help message and exit' in out
    assert 'output folder path for recording' in out


def test_main(caplog):
    api.TOKEN = ''
    assert 2 == cli.main(['-p', 'XYZ', '-T', ''])
    message = f'No secret token or pass phrase given, please set {APP_ENV}_TOKEN accordingly'
    assert caplog.record_tuples == [(APP_ENV, logging.ERROR, message)]


def test_parse_request():
    assert cli.parse_request([])


def test_parse_request_project():
    options = cli.parse_request(['-p', 'project'])
    assert options
    assert options.target_project == 'project'


def test_parse_request_mode():
    options = cli.parse_request(['--is-cloud'])
    assert options
    assert options.is_cloud
