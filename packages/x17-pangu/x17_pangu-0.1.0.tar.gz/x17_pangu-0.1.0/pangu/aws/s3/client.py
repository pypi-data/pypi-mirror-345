import boto3
import re
import json
from typing import Optional, Dict, Union, Any, List
from botocore.exceptions import ClientError

from pangu.aws.base.aws_client import AwsClient
from pangu.particle.log.log_group import LogGroup
from pangu.particle.log.log_stream import LogStream
from pangu.aws.session import AwsSession


class S3Client(AwsClient):
    def __init__(
        self,
        account_id: Optional[str] = None,
        service: Optional[str] = "s3",
        region: Optional[str] = None,
        plugin: Optional[Dict[str, Any]] = None,
        log_group: Optional[LogGroup] = None,
        max_paginate: Optional[int] = 100,
        session: Optional[AwsSession] = None,
        **kwargs: Optional[Dict[str, Any]],
    ):
        super().__init__(
            account_id=account_id,
            service=service,
            region=region,
            plugin=plugin,
            log_group=log_group,
            max_paginate=max_paginate,
            **kwargs,
        )
        if session:
            self.client = session.client(service_name=service)
        else:
            self.client = boto3.client(service_name=service)

        try:
            self.resource = boto3.resource("s3")
        except Exception as e:
            self.resource = None
        
        try:
            self.paginator = self.client.get_paginator("list_objects_v2")
        except Exception as e:
            self.paginator = None

    @staticmethod
    def bucket_of(uri: str) -> str | None:
        """
        Extracts the bucket name from the S3 URI.
        
        """
        match = re.match(r"^(?:s3://)?([^/]+)", uri)
        return match.group(1) if match else None

    @staticmethod
    def prefix_of(uri: str) -> str | None:
        """
        Extracts the prefix from the S3 URI.
        
        """
        match = re.match(r"^(?:s3://)?[^/]+/(.+)", uri)
        return match.group(1) if match else None

    def parse_uri(self, uri: str) -> tuple[str, str]:
        """
        Parses the S3 URI and returns the bucket name and prefix.
        The URI format is expected to be "s3://bucket-name/prefix" or "bucket-name/prefix".

        """
        return self.bucket_of(uri), self.prefix_of(uri)

    def list_objects(
        self,
        uri: str,
        suffix: Optional[str] = None,
        prefix: Optional[str] = "",
    ):
        """
        Lists all files in the bucket with the given suffix.
        Optionally filtering by key prefix and file suffix.
        Suffix suggestion = [0-9a-zA-Z]+

        """
        metas = []
        for page in self.paginator.paginate(
            Bucket=self.bucket_of(uri),
            Prefix=self.prefix_of(uri),
        ):
            for content in page.get("Contents", []):
                is_suffix = re.match(f".*\\.{suffix}$", content.get("Key", ""))
                is_prefix = re.match(f"^{prefix}.*", content.get("Key", ""))

                if is_suffix and is_prefix:
                    metas.append(
                        {
                            "bucket": content.get("Bucket"),
                            "key": content.get("Key"),
                            "size": content.get("Size"),
                            "last_modified": content.get("LastModified"),
                            "etag": content.get("ETag"),
                        }
                    )
        return metas

    def check_exist(self, uri: str) -> bool:
        """
        Check if the object exists at the given S3 URI.
        
        """
        try:
            bucket, key = self.parse_uri(uri)
            self.client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as error:
            return False if error.response["Error"]["Code"] == "404" else True
        except Exception as error:
            self.log_stream.warn(f"check exist failed for {uri}: {error}")
            return False

    def get_object(self, bucket: str, key: str) -> dict:
        """
        Get an S3 object.

        """
        return self.client.get_object(Bucket=bucket, Key=key)


    def delete_object(self, bucket: str, key: str):
        """
        Delete an S3 object.
        
        """
        self.client.delete_object(Bucket=bucket, Key=key)


    def put_object(self, bucket: str, key: str, data: Union[str, bytes]):
        """
        Upload object to S3.
        
        """
        self.client.put_object(Bucket=bucket, Key=key, Body=data)


    def put_json_object(self, bucket: str, key: str, data: Optional[dict] = None):
        """
        Put a Python dict as JSON to S3.
        
        """
        self.put_object(bucket, key, json.dumps(data or {}))


    def get_json_object(self, bucket: str, key: str) -> dict:
        """
        Get an S3 object and parse it as JSON.
        
        """
        try:
            content = self.get_object(bucket, key)["Body"].read().decode("utf-8")
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in object s3://{bucket}/{key}") from e

    def get_txt_object(self, bucket: str, key: str) -> str:
        """
        Get an S3 object and parse it as text.

        """
        return self.get_object(bucket, key)["Body"].read().decode("utf-8")

    def put_txt_object(self, bucket: str, key: str, data: str):
        """
        Put a string as text to S3.
        
        """
        self.put_object(bucket, key, data)