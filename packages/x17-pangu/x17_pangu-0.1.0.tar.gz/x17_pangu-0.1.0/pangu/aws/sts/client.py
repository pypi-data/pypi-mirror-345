import boto3
from typing import Optional, Dict

from pangu.particle.log.log_group import LogGroup
from pangu.particle.log.log_stream import LogStream
from pangu.aws.base.aws_client import AwsClient
from pangu.particle.duration import Duration
from pangu.aws.session import AwsSession

class StsClient(AwsClient):
    """
    AWS STS (Security Token Service) client.
    This class provides a common interface for interacting with STS, including logging, account info caching,
    and assuming roles. It extends the AwsClient base class for unified AWS logging and utilities.
    
    """
    def __init__(
        self,
        account_id: Optional[str] = None,
        region: Optional[str] = None,
        session: Optional[AwsSession] = None,
        **kwargs
    ):
        super().__init__(
            account_id=account_id,
            service="sts",
            region=region,
            **kwargs
        )
        if session:
            self.session = session
        else:
            self.session = AwsSession(
                region_name=self.region,
                aws_account_id=self.account_id,
            )
        self.client = self.session.client("sts")
        self._load()

    def _load(self):
        """
        Load account information from STS.
        This method caches the account ID, user ARN, and user ID for later use.
        
        """
        info = self.describe_caller()
        self.account_id = info.get("account_id")
        self.user_arn = info.get("user_arn")
        self.user_id = info.get("user_id")

    def describe_caller(self) -> Dict[str, str]:
        """
        Describe the caller identity.
        This method retrieves the account ID, user ARN, and user ID from STS.
        
        """
        response = self.client.get_caller_identity()
        return {
            "account_id": response.get("Account"),
            "user_arn": response.get("Arn"),
            "user_id": response.get("UserId"),
        }

    def get_account_id(self) -> Optional[str]:
        """
        Get the account ID.
        
        """
        return self.account_id

    def get_region(self) -> Optional[str]:
        """
        Get the region.
        
        """
        return self.region

    def get_user_arn(self) -> Optional[str]:
        """
        Get the user ARN.
        
        """
        return self.user_arn

    def get_user_id(self) -> Optional[str]:
        """
        Get the user ID.
        
        """
        return self.user_id

    def get_cred_from_assume_role(
        self,
        role_arn: str,
        role_session_name: str = "DefaultSession",
        duration: Duration = Duration(minute=60),
    ) -> dict:
        """
        Get temporary credentials by assuming a role.
        
        """
        response = self.client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=role_session_name,
            DurationSeconds=duration.base,
        )
        return response.get("Credentials", {})
