import pytest
from pangu.aws.base.aws_resource import AwsResource  # 根据你项目路径调整
from pangu.particle.log.log_group import LogGroup
from pangu.particle.log.log_stream import LogStream

class DummyPlugin:
    def __init__(self, name):
        self.name = name

@pytest.fixture
def resource():
    return AwsResource(
        resource_id="test-resource",
        account_id="123456789012",
        region="us-west-2",
        raw={"name": "MyResource", "status": "ready"}
    )

def test_initialization_basic(resource):
    assert resource.resource_id == "test-resource"
    assert resource.account_id == "123456789012"
    assert resource.region == "us-west-2"
    assert resource.name == "MyResource"
    assert resource.status == "ready"
    assert isinstance(resource.log_stream, LogStream)
    assert resource.log_group is None

def test_from_dict():
    raw_data = {"type": "Lambda", "status": "active"}
    obj = AwsResource.from_dict(raw_data, resource_id="lambda-001", region="ap-southeast-2")
    assert obj.resource_id == "lambda-001"
    assert obj.region == "ap-southeast-2"
    assert obj.status == "active"
    assert obj.type == "Lambda"

def test_repr_str(resource):
    assert str(resource) == repr(resource)
    assert "AwsResource" in repr(resource)

def test_log_stream_with_log_group():
    group = LogGroup(name="TestGroup")
    resource = AwsResource(
        resource_id="res-1",
        region="ap-southeast-2",
        log_group=group,
        raw={"key": "value"}
    )
    assert isinstance(resource.log_stream, LogStream)
    assert resource.log_group is group
    assert resource.log_stream.group is group
    assert "TestGroup" in resource.log_stream.name or resource.log_stream.group.name

def test_plugin_registration(resource):
    plugin = DummyPlugin("myplugin")
    name, p = resource.register_plugin("custom", plugin)
    assert name == "custom"
    assert resource.plugin["custom"] is plugin

    with pytest.raises(ValueError):
        resource.register_plugin("custom", DummyPlugin("another"))

def test_log_behavior(resource):
    resource.log("hello world", level="DEBUG")
    assert resource.log_stream.name.startswith("AwsResource:")

def test_dict_output(resource):
    d = resource.dict
    assert isinstance(d, dict)
    assert d["account_id"] == "123456789012"
    assert d["region"] == "us-west-2"
    assert d["log_stream"].startswith("AwsResource:")
    assert "log_group" in d
