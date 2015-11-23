# coding: utf-8
from app.server import TcpClient
import pytest

messages_case = [
    ('Foo:: Bar', {'key': 'Foo', 'value': 'Bar'}),
    ('Привет:: Мир', {'key': 'Привет', 'value': 'Мир'}),
    ('Foo ::Bar', None),
    ('Foo::Bar', None),
    ('Foo::  Bar', {'key': 'Foo', 'value': ' Bar'}),
]


@pytest.mark.parametrize("case", messages_case)
def test_process_message(case):
    message, result = case

    client = TcpClient()
    response = client.process_line(message)

    if response:
        del response['id']
        del response['source']

    assert result == response


auth_case = [
    ('Auth:: Bar', {'login': True, 'auth': True, 'source_name': 'Bar'}),
    ('Foo:: Bar', {'login': False, 'auth': False, 'source_name': ''}),
    ('Auth :: Bar', {'login': False, 'auth': False, 'source_name': ''}),
    (' Auth ::Bar', {'login': False, 'auth': False, 'source_name': ''}),
]


@pytest.mark.parametrize("case", auth_case)
def test_auth(case):
    message, result = case

    client = TcpClient()
    response = client.process_auth(message)

    assert result['login'] == response
    assert result['auth'] == client.auth
    assert result['source_name'] == client.source_name


clean_case = [
    (b" Hello\r\n", u'Hello'),
    (b" Привет \r\n", u'Привет'),
]


@pytest.mark.parametrize("case", clean_case)
def test_clean(case):
    line, response = case

    client = TcpClient()
    result = client.clean_line(line)

    assert result == response
