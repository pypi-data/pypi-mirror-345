import boto3
import pytest
from moto import mock_aws

from pangu.aws.session import AwsSession


@mock_aws
def test_get_credentials_with_moto():
    session = AwsSession()
    creds = session.get_credentials()
    assert isinstance(creds, dict)
    assert "access_key" in creds
    assert "secret_key" in creds
    assert "token" in creds
    assert creds["access_key"]
    assert creds["secret_key"]


@mock_aws
def test_list_regions_with_moto():
    session = AwsSession()
    regions = session.list_regions(service_name="ec2")
    assert isinstance(regions, list)
    assert "us-east-1" in regions or len(regions) > 0


@mock_aws
def test_list_partitions_with_moto():
    session = AwsSession()
    partitions = session.list_partitions()
    assert isinstance(partitions, list)
    assert "aws" in partitions


@mock_aws
def test_list_services_with_moto():
    session = AwsSession()
    services = session.list_services()
    assert isinstance(services, list)
    assert "ec2" in services or len(services) > 0


@pytest.fixture
def basic_session():
    return AwsSession(
        access_key="AKIA_TEST_KEY",
        secret_key="TEST_SECRET",
        session_token="TEST_TOKEN",
        region_name="us-east-1",
        aws_account_id="123456789012",
    )


@mock_aws
def test_client_creation_default(basic_session):
    client = basic_session.client("s3")
    assert client.meta.service_model.service_name == "s3"
    response = client.list_buckets()
    assert "Buckets" in response


@mock_aws
def test_client_creation_with_override(basic_session):
    # Override region and credentials
    client = basic_session.client(
        "ec2",
        region_name="us-west-2",
        aws_access_key_id="CUSTOM_KEY",
        aws_secret_access_key="CUSTOM_SECRET",
        aws_session_token="CUSTOM_TOKEN",
    )
    assert client.meta.region_name == "us-west-2"


@mock_aws
def test_fallback_to_session_credentials(basic_session):
    client = basic_session.client("s3")
    creds = basic_session.session.get_credentials()
    assert creds.access_key == "AKIA_TEST_KEY"
    assert creds.secret_key == "TEST_SECRET"
    assert creds.token == "TEST_TOKEN"


@mock_aws
def test_client_can_call_methods(basic_session):
    client = basic_session.client("s3")
    response = client.list_buckets()
    assert isinstance(response, dict)
    assert "Buckets" in response
