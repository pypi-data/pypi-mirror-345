import pytest
from pangu.aws.base.aws_client import AwsClient

@pytest.fixture
def aws_client():
    return AwsClient(
        account_id="123456789012",
        service="test-service",
        region="us-east-1"
    )

def test_default_init():
    client = AwsClient()
    assert client.account_id is None
    assert client.region == AwsClient.REGION_NAME
    assert client.service is None
    assert isinstance(client.plugin, dict)

def test_client_initialization(aws_client):
    assert aws_client.account_id == "123456789012"
    assert aws_client.region == "us-east-1"
    assert aws_client.service == "test-service"
    assert aws_client.max_paginate == AwsClient.MAX_PAGINATE
    assert "test-service" in str(aws_client)

def test_str_and_repr(aws_client):
    assert str(aws_client) == repr(aws_client)
    assert "AwsClient" in repr(aws_client)

def test_plugin_registration(aws_client):
    name, plugin = aws_client.register_plugin("logger", {"key": "value"})
    assert name == "logger"
    assert plugin == {"key": "value"}
    assert "logger" in aws_client.plugin

    with pytest.raises(ValueError):
        aws_client.register_plugin("logger", {"another": "plugin"})

def test_pop_list():
    client = AwsClient()
    data = [{"a": 1}, {"b": 2}]
    popped = client.pop_list(data, 0)
    assert popped == {"a": 1}
    assert len(data) == 1

    assert client.pop_list([], 0, default="fallback") == "fallback"
    assert client.pop_list(data, 5, default=None) is None

def test_slice_list():
    client = AwsClient()
    data = list(range(10))
    sliced = client.slice_list(data, 2, 5)
    assert sliced == [2, 3, 4]

def test_strip_params():
    client = AwsClient()
    stripped = client.strip_params(a=None, b="value", c=0)
    assert stripped == {"b": "value", "c": 0}

def test_dict_property(aws_client):
    d = aws_client.dict
    assert d["account_id"] == "123456789012"
    assert d["region"] == "us-east-1"
    assert d["service"] == "test-service"
    assert "log_stream" in d
    assert isinstance(d["plugin"], dict)

def test_logging(aws_client, capsys):
    aws_client.log("Hello World", level="INFO")
    assert "AwsClient" in aws_client.log_stream.name
    # Optional: Capture console output if log_stream is printing
    # captured = capsys.readouterr()
    # assert "Hello World" in captured.out