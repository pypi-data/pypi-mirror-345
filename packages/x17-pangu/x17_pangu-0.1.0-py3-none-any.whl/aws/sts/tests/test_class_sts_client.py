import pytest
from moto import mock_aws
import boto3

from pangu.aws.sts.client import StsClient
from pangu.particle.duration import Duration


@mock_aws
def test_sts_client_initialization_and_identity():
    client = boto3.client("sts", region_name="ap-southeast-2")
    client.get_caller_identity()  # this triggers moto internal initialization

    sts = StsClient()
    
    # Identity should be auto-loaded
    assert isinstance(sts.get_account_id(), str)
    assert isinstance(sts.get_user_id(), str)
    assert isinstance(sts.get_user_arn(), str)
    assert isinstance(sts.get_region(), str)

    info = sts.describe_caller()
    assert info["account_id"] == sts.get_account_id()
    assert info["user_arn"] == sts.get_user_arn()
    assert info["user_id"] == sts.get_user_id()


@mock_aws
def test_sts_assume_role_creds():
    client = boto3.client("iam", region_name="ap-southeast-2")
    role_name = "test-role"
    role_arn = f"arn:aws:iam::123456789012:role/{role_name}"

    client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}',
    )

    sts = StsClient()
    creds = sts.get_cred_from_assume_role(role_arn)

    assert isinstance(creds, dict)
    assert "AccessKeyId" in creds
    assert "SecretAccessKey" in creds
    assert "SessionToken" in creds
    assert "Expiration" in creds


@mock_aws
def test_sts_assume_role_with_duration():
    role_name = "timed-role"
    role_arn = f"arn:aws:iam::123456789012:role/{role_name}"
    
    boto3.client("iam", region_name="ap-southeast-2").create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}',
    )

    sts = StsClient()
    duration = Duration(minute=15)
    creds = sts.get_cred_from_assume_role(role_arn=role_arn, duration=duration)

    assert isinstance(creds["AccessKeyId"], str)
    assert duration.base == 900  # 15 minutes in seconds