import pytest
from unittest.mock import patch, MagicMock
from pangu.aws.redshift.serverless.client import RSSClient


@pytest.fixture
def mock_boto_client():
    with patch("boto3.client") as mock:
        yield mock

# ---------- No Wait Tests ----------

def test_create_namespace_no_wait(mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.create_namespace.return_value = {
        "namespace": {"namespaceName": "test-ns"}
    }

    rss = RSSClient(region="us-east-1")
    result = rss.create_namespace(namespace_name="test-ns", wait=False)

    assert result["namespaceName"] == "test-ns"
    mock_client.create_namespace.assert_called_once()

def test_create_workgroup_no_wait(mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.create_workgroup.return_value = {
        "workgroup": {"workgroupName": "test-wg"}
    }

    rss = RSSClient(region="us-east-1")
    result = rss.create_workgroup("test-ns", "test-wg", wait=False)

    assert result["workgroupName"] == "test-wg"
    mock_client.create_workgroup.assert_called_once()

def test_delete_namespace_no_wait(mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.delete_namespace.return_value = {
        "namespace": {"namespaceName": "test-ns"}
    }

    rss = RSSClient(region="us-east-1")
    result = rss.delete_namespace("test-ns", wait=False)

    assert result == {}
    mock_client.delete_namespace.assert_called_once()

def test_delete_workgroup_no_wait(mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.delete_workgroup.return_value = {
        "workgroup": {"workgroupName": "test-wg"}
    }

    rss = RSSClient(region="us-east-1")
    result = rss.delete_workgroup("test-wg", wait=False)

    assert result == {}
    mock_client.delete_workgroup.assert_called_once()

def test_update_namespace_no_wait(mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.update_namespace.return_value = {
        "namespace": {"namespaceName": "test-ns"}
    }

    rss = RSSClient(region="us-east-1")
    result = rss.update_namespace("test-ns", wait=False)

    assert result["namespaceName"] == "test-ns"
    mock_client.update_namespace.assert_called_once()

def test_update_workgroup_no_wait(mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.update_workgroup.return_value = {
        "workgroup": {"workgroupName": "test-wg"}
    }

    rss = RSSClient(region="us-east-1")
    result = rss.update_workgroup("test-ns", "test-wg", wait=False)

    assert result["workgroupName"] == "test-wg"
    mock_client.update_workgroup.assert_called_once()

# ---------- Wait Tests ----------

@patch.object(RSSClient, "get_namespace")
def test_create_namespace_with_wait(mock_get_namespace, mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.create_namespace.return_value = {"namespace": {"namespaceName": "test-ns"}}

    responses = [
        {"status": "CREATING"},
        {"status": "AVAILABLE"},
    ]
    mock_get_namespace.side_effect = lambda *args, **kwargs: responses.pop(0) if responses else {"status": "AVAILABLE"}

    rss = RSSClient(region="us-east-1")
    result = rss.create_namespace(namespace_name="test-ns", wait=True)

    assert result["status"] == "AVAILABLE"
    assert mock_get_namespace.call_count >= 2

@patch.object(RSSClient, "get_workgroup")
def test_create_workgroup_with_wait(mock_get_workgroup, mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.create_workgroup.return_value = {"workgroup": {"workgroupName": "test-wg"}}

    responses = [
        {"status": "CREATING"},
        {"status": "AVAILABLE"},
    ]
    mock_get_workgroup.side_effect = lambda *args, **kwargs: responses.pop(0) if responses else {"status": "AVAILABLE"}

    rss = RSSClient(region="us-east-1")
    result = rss.create_workgroup("test-ns", "test-wg", wait=True)

    assert result["status"] == "AVAILABLE"
    assert mock_get_workgroup.call_count >= 2

@patch.object(RSSClient, "get_namespace")
def test_update_namespace_with_wait(mock_get_namespace, mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.update_namespace.return_value = {"namespace": {"namespaceName": "test-ns"}}

    responses = [
        {"status": "UPDATING"},
        {"status": "AVAILABLE"},
    ]
    mock_get_namespace.side_effect = lambda *args, **kwargs: responses.pop(0) if responses else {"status": "AVAILABLE"}

    rss = RSSClient(region="us-east-1")
    result = rss.update_namespace("test-ns", wait=True)

    assert result["status"] == "AVAILABLE"
    assert mock_get_namespace.call_count >= 2

@patch.object(RSSClient, "get_workgroup")
def test_update_workgroup_with_wait(mock_get_workgroup, mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.update_workgroup.return_value = {"workgroup": {"workgroupName": "test-wg"}}

    responses = [
        {"status": "UPDATING"},
        {"status": "AVAILABLE"},
    ]
    mock_get_workgroup.side_effect = lambda *args, **kwargs: responses.pop(0) if responses else {"status": "AVAILABLE"}

    rss = RSSClient(region="us-east-1")
    result = rss.update_workgroup("test-ns", "test-wg", wait=True)

    assert result["status"] == "AVAILABLE"
    assert mock_get_workgroup.call_count >= 2

@patch.object(RSSClient, "get_namespace")
def test_delete_namespace_with_wait(mock_get_namespace, mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.delete_namespace.return_value = {}

    responses = [
        {"status": "DELETING"},
        {},
    ]
    mock_get_namespace.side_effect = lambda *args, **kwargs: responses.pop(0) if responses else {}

    rss = RSSClient(region="us-east-1")
    result = rss.delete_namespace("test-ns", wait=True)

    assert result == {}
    assert mock_get_namespace.call_count >= 2

@patch.object(RSSClient, "get_workgroup")
def test_delete_workgroup_with_wait(mock_get_workgroup, mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    mock_client.delete_workgroup.return_value = {}

    responses = [
        {"status": "DELETING"},
        {},
    ]
    mock_get_workgroup.side_effect = lambda *args, **kwargs: responses.pop(0) if responses else {}

    rss = RSSClient(region="us-east-1")
    result = rss.delete_workgroup("test-wg", wait=True)

    assert result == {}
    assert mock_get_workgroup.call_count >= 2

@patch.object(RSSClient, "get_namespace")
def test_timeout(mock_get, mock_boto_client):
    mock_boto_client.return_value = MagicMock()
    mock_get.return_value = {"status": "CREATING"}  # 一直不满足条件

    rss = RSSClient(region="us-east-1")

    with pytest.raises(TimeoutError):
        rss.wait_create_namespace("test-ns", timeout=0.3, interval=0.1)
