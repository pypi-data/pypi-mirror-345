import json
import pytest
from moto import mock_aws
import boto3
from pangu.aws.s3.client import S3Client

TEST_BUCKET = "test-bucket"
TEST_KEY_TXT = "folder/test.txt"
TEST_KEY_JSON = "folder/data.json"
TEST_DATA = "Hello World"
TEST_JSON = {"msg": "hello"}

@pytest.fixture
def s3_setup():
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=TEST_BUCKET)
        s3.put_object(
            Bucket=TEST_BUCKET,
            Key=TEST_KEY_TXT,
            Body=TEST_DATA
        )
        yield s3

@pytest.fixture
def s3_client():
    return S3Client(region="us-east-1")

def test_put_and_get_txt(s3_setup, s3_client):
    s3_client.put_txt_object(TEST_BUCKET, TEST_KEY_TXT, TEST_DATA)
    assert s3_client.get_txt_object(TEST_BUCKET, TEST_KEY_TXT) == TEST_DATA

def test_put_and_get_json(s3_setup, s3_client):
    s3_client.put_json_object(TEST_BUCKET, TEST_KEY_JSON, TEST_JSON)
    assert s3_client.get_json_object(TEST_BUCKET, TEST_KEY_JSON) == TEST_JSON

def test_get_object(s3_setup, s3_client):
    s3_client.put_txt_object(TEST_BUCKET, TEST_KEY_TXT, TEST_DATA)
    obj = s3_client.get_object(TEST_BUCKET, TEST_KEY_TXT)
    assert obj["Body"].read().decode("utf-8") == TEST_DATA

@mock_aws
def test_check_exist_true():
    boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="test-bucket")

    client = S3Client(region="us-east-1")
    client.put_txt_object("test-bucket", "folder/test.txt", "data")

    uri = "s3://test-bucket/folder/test.txt"
    assert client.check_exist(uri) is True

def test_check_exist_false(s3_setup, s3_client):
    uri = f"s3://{TEST_BUCKET}/nonexistent.txt"
    assert s3_client.check_exist(uri) is False

def test_delete_object(s3_setup, s3_client):
    s3_client.put_txt_object(TEST_BUCKET, TEST_KEY_TXT, TEST_DATA)
    s3_client.delete_object(TEST_BUCKET, TEST_KEY_TXT)
    assert "Contents" not in s3_setup.list_objects_v2(Bucket=TEST_BUCKET)

def test_parse_uri_variants(s3_client):
    uri1 = f"s3://{TEST_BUCKET}/{TEST_KEY_TXT}"
    uri2 = f"{TEST_BUCKET}/{TEST_KEY_TXT}"
    assert s3_client.parse_uri(uri1) == (TEST_BUCKET, TEST_KEY_TXT)
    assert s3_client.parse_uri(uri2) == (TEST_BUCKET, TEST_KEY_TXT)

def test_bucket_and_prefix_helpers(s3_client):
    uri = f"s3://{TEST_BUCKET}/{TEST_KEY_TXT}"
    assert s3_client.bucket_of(uri) == TEST_BUCKET
    assert s3_client.prefix_of(uri) == TEST_KEY_TXT