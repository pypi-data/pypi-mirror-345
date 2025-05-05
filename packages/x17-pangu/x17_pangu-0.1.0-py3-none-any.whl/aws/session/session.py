from typing import Any, Dict, Optional

import boto3

from pangu.particle.log.log_group import LogGroup
from pangu.particle.log.log_stream import LogStream


class AwsSession:
    """
    AWS Session class.
    This class provides a common interface for AWS sessions.
    Including logging and plugin registration.
    Can either support Ec2 instance runtime or local runtime.
    Normally set the log module to log group.

    """

    def __init__(
        self,
        access_key=None,
        secret_key=None,
        session_token=None,
        botocore_session=None,
        aws_account_id=None,
        profile_name=None,
        region_name=None,
        log_group: Optional[LogGroup] = None,
    ):
        params = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "aws_session_token": session_token,
            "botocore_session": botocore_session,
            "aws_account_id": aws_account_id,
            "profile_name": profile_name,
            "region_name": region_name,
        }
        params = {k: v for k, v in params.items() if v is not None}
        self.session = boto3.Session(
            **params,
        )
        self.plugin = {}
        self.account_id = aws_account_id
        self.region_name = region_name

        self.class_name = self.__class__.__name__.lower()
        self.log_stream = LogStream(
            name=f"{self.class_name}:{self.region_name}:{self.account_id}",
        )
        if log_group:
            self.log_group = log_group
            self.log_stream = self.log_group.register_stream(self.log_stream)
        else:
            self.log_group = None

    def client(
        self,
        service_name: str,
        region_name: Optional[str] = None,
        aws_account_id: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        api_version: Optional[str] = None,
        use_ssl: Optional[bool] = True,
        verify: Optional[bool] = None,
        endpoint_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Create a boto3 client for the given service.
        This is a wrapper for the boto3 session client method.

        """
        session_cred = self.session.get_credentials()
        params = {
            "service_name": service_name,
            "region_name": region_name,
            "aws_account_id": aws_account_id,
            "aws_access_key_id": aws_access_key_id or session_cred.access_key,
            "aws_secret_access_key": aws_secret_access_key or session_cred.secret_key,
            "aws_session_token": aws_session_token or session_cred.token,
            "api_version": api_version,
            "use_ssl": use_ssl,
            "verify": verify,
            "endpoint_url": endpoint_url,
            "config": config,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return self.session.client(
            **params,
        )

    def list_regions(
        self,
        service_name: Optional[str],
        partition_name: Optional[str] = "aws",
    ) -> list:
        """
        List all available regions for a given service and partition.

        """

        return self.session.get_available_regions(
            service_name=service_name,
            partition_name=partition_name,
        )

    def list_partitions(self) -> list:
        """
        List all available partitions.

        """
        return self.session.get_available_partitions()

    def list_services(self) -> list:
        """
        List all available services.

        """
        return self.session.get_available_services()

    def get_credentials(self):
        """
        Get the credentials for the session.
        This is a wrapper for the boto3 session get_credentials method.
        The credentials are returned as a dictionary.

        """
        credential = self.session.get_credentials()
        return {
            "access_key": credential.access_key,
            "secret_key": credential.secret_key,
            "token": credential.token,
        }
