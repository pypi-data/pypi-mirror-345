import pytest
from unittest.mock import patch, MagicMock
from moto import mock_aws
import boto3
from pangu.aws.ec2.client import Ec2Client

REGION = "us-east-1"

@pytest.fixture
def ec2_with_mock_client():
    ec2 = Ec2Client(region="us-east-1")
    ec2.client = MagicMock()
    return ec2

@mock_aws
def test_list_and_get_vpcs():
    ec2 = boto3.client("ec2", region_name=REGION)
    vpc = ec2.create_vpc(CidrBlock="10.0.0.0/16")["Vpc"]
    client = Ec2Client(region=REGION)

    vpcs = client.list_vpcs()
    assert any(v["VpcId"] == vpc["VpcId"] for v in vpcs)

    vpc_info = client.get_vpc(vpc_id=vpc["VpcId"])
    assert vpc_info["VpcId"] == vpc["VpcId"]

@mock_aws
def test_get_default_vpc_none():
    client = Ec2Client(region=REGION)
    default_vpc = client.get_default_vpc()
    assert default_vpc 
    assert default_vpc["VpcId"] is not None
    assert default_vpc["IsDefault"] is True

@patch("pangu.aws.ec2.client.Ec2Client.get_security_group_by_name")
def test_exists_security_group_by_name(mock_get_sg):
    mock_get_sg.return_value = {"GroupId": "sg-123"}
    client = Ec2Client(region=REGION)
    assert client.exists_security_group_by_name("test-sg", "vpc-123") is True

@patch("pangu.aws.ec2.client.Ec2Client.get_security_group")
def test_get_security_group_by_name_and_id(mock_get_sg):
    mock_get_sg.return_value = {"GroupId": "sg-abc"}
    client = Ec2Client(region=REGION)
    by_name = client.get_security_group_by_name("test", "vpc-1")
    by_id = client.get_security_group_by_id("sg-abc", "vpc-1")
    assert by_name["GroupId"] == "sg-abc"
    assert by_id["GroupId"] == "sg-abc"

def test_list_security_groups(ec2_with_mock_client):
    ec2 = ec2_with_mock_client
    ec2.client.describe_security_groups.return_value = {
        "SecurityGroups": [{"GroupId": "sg-123"}]
    }
    result = ec2.list_security_groups()
    assert result == [{"GroupId": "sg-123"}]

def test_authorize_ingress_from_cidr(ec2_with_mock_client):
    ec2 = ec2_with_mock_client
    ec2.client.authorize_security_group_ingress.return_value = {
        "SecurityGroupRules": [{"RuleId": "rule-123"}]
    }
    result = ec2.authorise_ingress_from_cidr_ips(
        group_id="sg-123",
        cidr_ips_configs=[
            {
                "cidr_ip": "0.0.0.0/0",
                "ip_protocol": "tcp",
                "from_port": 80,
                "to_port": 80
            }
        ]
    )
    assert result[0][0]["RuleId"] == "rule-123"

def test_delete_security_group_with_wait(ec2_with_mock_client):
    ec2 = ec2_with_mock_client
    ec2.client.describe_security_groups.side_effect = [
        {"SecurityGroups": [{"GroupId": "sg-123"}]},
        {},
    ]
    ec2.client.delete_security_group.return_value = {
        "ResponseMetadata": {"HTTPStatusCode": 200}
    }
    result = ec2.delete_security_group(group_id="sg-123", wait=True)
    assert result == {}


