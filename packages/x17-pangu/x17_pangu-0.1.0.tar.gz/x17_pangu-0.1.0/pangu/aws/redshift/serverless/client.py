import boto3
import time
from typing import Optional, Dict, Union, Any, List

from pangu.particle.log.log_group import LogGroup
from pangu.particle.log.log_stream import LogStream
from pangu.aws.base.aws_client import AwsClient
from pangu.aws.session import AwsSession
from pangu.aws.waiter import Waiter

class RSSClient(AwsClient):
    """
    AWS Redshift Serverless client.
    This class provides a common interface for interacting with Redshift Serverless, including logging,
    account info caching, and assuming roles. It extends the AwsClient base class for unified AWS logging and utilities.
    It provides methods for listing, creating, updating, and deleting namespaces and workgroups.
    It also provides methods for waiting for the creation and deletion of namespaces and workgroups.
    The class uses the boto3 library to interact with AWS services.

    """
    
    def __init__(
        self, 
        account_id: Optional[str] = None,
        service: Optional[str] = "redshift-serverless",
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
            **kwargs
        )
        if session:
            self.client = session.client(service_name=service)
        else:
            self.client = boto3.client(service_name=service)
    
    def list_namespace(self) -> List[Dict[str, Any]]:
        """
        List all namespaces in the account.
        The namespaces are paginated, so this method will return all namespaces
    
        """
        namespaces = []
        next_token = None
        for _ in range(self.max_paginate):
            params = self.strip_params(
                maxResults=self.max_paginate,
                NextToken=next_token,
            )
            response = self.client.list_namespaces(**params)
            namespaces.extend(response["namespaces"])
            next_token = response.get("nextToken")
            if not next_token: break
        return namespaces

    def list_workgroup(self, owner_account: str=None) -> List[Dict[str, Any]]:
        """
        List all workgroups in the account.
        The owner account is optional and can be used to filter the workgroups by owner.

        """
        workgroups = []
        next_token = None
        for _ in range(self.max_paginate):
            params = self.strip_params(
                ownerAccount=owner_account,
                maxResults=self.max_paginate,
                NextToken=next_token,
            )
            response = self.client.list_workgroups(**params)
            workgroups.extend(response["workgroups"])
            next_token = response.get("nextToken")
            if not next_token: break
        return workgroups

    def get_namespace(self, namespace_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a namespace by name.
        
        """
        try:
            response = self.client.get_namespace(namespaceName=namespace_name)
            return response.get("namespace", {})
        except Exception as e:
            self.log(message=f"[get_namespace({namespace_name})] Error: {e}", level="ERROR")
            return {}
    
    def get_workgroup(self, workgroup_name: str) -> Union[Dict[str, Any], None]:
        """
        Get a workgroup by name.

        """
        try:
            response = self.client.get_workgroup(workgroupName=workgroup_name)
            return response.get("workgroup", {})
        except Exception as e:
            self.log(message=f"[get_workgroup({workgroup_name})] Error: {e}", level="ERROR")
            return {}

    def create_namespace(
        self, 
        namespace_name: str,
        admin_password_secret_kms_key_id: Optional[str] = None,
        admin_user_password: Optional[str] = None,
        admin_user_name: Optional[str] = None,
        db_name: Optional[str] = None,
        default_iam_role_arn: Optional[str] = None,
        iam_roles: Optional[List[str]] = None,
        kms_key_id: Optional[str] = None,
        log_exports: Optional[List[str]] = None,
        manage_admin_password: Optional[bool] = False,
        redshift_idc_application_arn: Optional[str] = None,
        tags: List[Dict[str, str]] = None,
        wait: Optional[bool] = True,
    ) -> Dict[str, Any]:
        """
        Create a namespace with the specified parameters.
        
        """
        log_exports = log_exports or [
            'useractivitylog',
            'userlog',
            'connectionlog',
        ]
        params = self.strip_params(
            adminPasswordSecretKmsKeyId=admin_password_secret_kms_key_id,
            adminUserPassword=admin_user_password,
            adminUsername=admin_user_name,
            dbName=db_name,
            defaultIamRoleArn=default_iam_role_arn,
            iamRoles=iam_roles,
            kmsKeyId=kms_key_id,
            logExports=log_exports,
            manageAdminPassword=manage_admin_password,
            namespaceName=namespace_name,
            redshiftIdcApplicationArn=redshift_idc_application_arn,
            tags=tags,
        )
        response = self.client.create_namespace(
            **params
        )
        if wait:
            self.wait_create_namespace(namespace_name)
            return self.get_namespace(namespace_name)
        return response.get("namespace", {})
        
    def create_workgroup(
        self, 
        namespace_name: str,
        workgroup_name: str,
        base_capacity: Optional[int] = 32,
        config_parameters: Optional[List[Dict[str, str]]] = None,
        enhanced_vpc_routing: Optional[bool] = False,
        max_capacity: Optional[int] = None,
        port: Optional[int] = None,
        price_performance_target: Optional[Dict[str, Union[int, str]]] = None,
        publicly_accessible: Optional[bool] = False,
        security_group_ids: Optional[List[str]] = None,
        subnet_ids: Optional[List[str]] = None,
        tags: Optional[List[Dict[str, str]]] = None,
        track_name: Optional[str] = None,
        wait: Optional[bool] = True,
    ):
        """
        Create a workgroup in the specified namespace.
        
        """
        params = self.strip_params(
            namespaceName=namespace_name,
            workgroupName=workgroup_name,
            baseCapacity=base_capacity,
            configParameters=config_parameters,
            enhancedVpcRouting=enhanced_vpc_routing,
            maxCapacity=max_capacity,
            port=port,
            pricePerformanceTarget=price_performance_target,
            publiclyAccessible=publicly_accessible,
            securityGroupIds=security_group_ids,
            subnetIds=subnet_ids,
            tags=tags,
            trackName=track_name,
        )
        response = self.client.create_workgroup(
            **params
        )
        if wait:
            self.wait_create_workgroup(workgroup_name)
            return self.get_workgroup(workgroup_name)
        return response.get("workgroup", {})

    def wait_create_namespace(
        self,
        namespace_name: str,
        timeout: Optional[int] = 900,
        interval: Optional[int] = 10,
    ) -> bool:
        """
        Wait until the namespace reaches AVAILABLE state.
        
        """
        self.log_stream.info(f"Waiting for namespace {namespace_name} to become AVAILABLE...")
        waiter = Waiter(
            getter=self.get_namespace,
            get_path="status",
            expected="AVAILABLE",
            params={"namespace_name": namespace_name},
            description=f"Wait for namespace {namespace_name} to become AVAILABLE",
            interval=interval,
            timeout=timeout,
            compare_mode="==",
            log_stream=self.log_stream,
        )
        return waiter.wait()
        
    def wait_create_workgroup(
        self, 
        workgroup_name: str, 
        timeout: Optional[int] = 900, 
        interval: Optional[int] = 10,
    ) -> bool:
        """
        Wait until the workgroup reaches AVAILABLE state.
        
        """
        self.log_stream.info(f"Waiting for workgroup {workgroup_name} to become AVAILABLE...")
        waiter = Waiter(
            getter=self.get_workgroup,
            get_path="status",
            expected="AVAILABLE",
            params={"workgroup_name": workgroup_name},
            description=f"Wait for workgroup {workgroup_name} to become AVAILABLE",
            interval=interval,
            timeout=timeout,
            compare_mode="==",
            log_stream=self.log_stream,
        )
        return waiter.wait()

    def delete_workgroup(
        self, 
        workgroup_name: str, 
        wait: Optional[bool] = True,
    ) -> Dict[str, Any]:
        """
        Delete a workgroup by name.
        This method will delete the workgroup and all associated resources.

        """
        self.client.delete_workgroup(
            workgroupName=workgroup_name,
        )
        if wait:
            self.wait_delete_workgroup(workgroup_name)
        return {}

    def delete_namespace(
        self, 
        namespace_name: str, 
        wait: Optional[bool] = True,
    ) -> Dict[str, Any]:
        """
        Delete a namespace by name.
        This method will delete the namespace and all associated resources.
        
        """
        self.client.delete_namespace(
            namespaceName=namespace_name,
        )
        if wait:
            self.wait_delete_namespace(namespace_name)
        return {}

    def wait_delete_workgroup(
        self,
        workgroup_name: str,
        timeout: Optional[int] = 900,
        interval: Optional[int] = 10,
    ) -> bool:
        """
        Wait until the workgroup is deleted.
        
        """
        self.log_stream.info(f"Waiting for workgroup {workgroup_name} to be deleted...")
        waiter = Waiter(
            getter=self.get_workgroup,
            get_path="status",
            expected=None,
            params={"workgroup_name": workgroup_name},
            description=f"Wait for deletion of workgroup {workgroup_name}",
            interval=interval,
            timeout=timeout,
            invert=True,
            compare_mode="exists",
            log_stream=self.log_stream,
        )
        return waiter.wait()

    def wait_delete_namespace(
        self,
        namespace_name: str,
        timeout: Optional[int] = 900,
        interval: Optional[int] = 10,
    ) -> bool:
        """
        Wait until the namespace is deleted.
        
        """
        self.log_stream.info(f"Waiting for namespace {namespace_name} to be deleted...")
        waiter = Waiter(
            getter=self.get_namespace,
            get_path="status",
            expected=None,
            params={"namespace_name": namespace_name},
            description=f"Wait for deletion of namespace {namespace_name}",
            interval=interval,
            timeout=timeout,
            invert=True,
            compare_mode="exists",
            log_stream=self.log_stream,
        )
        return waiter.wait()

    def update_namespace(
        self,
        namespace_name: str,
        admin_password_secret_kms_key_id: Optional[str] = None,
        admin_user_password: Optional[str] = None,
        admin_user_name: Optional[str] = None,
        default_iam_role_arn: Optional[str] = None,
        iam_roles: Optional[List[str]] = None,
        kms_key_id: Optional[str] = None,
        log_exports: Optional[List[str]] = None,
        manage_admin_password: Optional[bool] = False,
        wait: Optional[bool] = True,
    ) -> Dict[str, Any]:
        """
        Update the specified namespace with the given parameters.
        
        """
        log_exports = log_exports or [
            'useractivitylog',
            'userlog',
            'connectionlog',
        ]
        params = self.strip_params(
            adminPasswordSecretKmsKeyId=admin_password_secret_kms_key_id,
            adminUserPassword=admin_user_password,
            adminUsername=admin_user_name,
            defaultIamRoleArn=default_iam_role_arn,
            iamRoles=iam_roles,
            kmsKeyId=kms_key_id,
            logExports=log_exports,
            manageAdminPassword=manage_admin_password,
            namespaceName=namespace_name,
        )
        response = self.client.update_namespace(
            **params
        )
        if wait:
            self.wait_update_namespace(namespace_name)
            return self.get_namespace(namespace_name)
        return response.get("namespace", {})
    
    
    def update_workgroup(
        self,
        namespace_name: str,
        workgroup_name: str,
        base_capacity: Optional[int] = 32,
        config_parameters: Optional[List[Dict[str, str]]] = None,
        enhanced_vpc_routing: Optional[bool] = False,
        max_capacity: Optional[int] = None,
        port: Optional[int] = None,
        price_performance_target: Optional[Dict[str, Union[int, str]]] = None,
        publicly_accessible: Optional[bool] = False,
        security_group_ids: Optional[List[str]] = None,
        subnet_ids: Optional[List[str]] = None,
        tags: Optional[List[Dict[str, str]]] = None,
        wait: Optional[bool] = True,
    ):
        params = self.strip_params(
            namespaceName=namespace_name,
            workgroupName=workgroup_name,
            baseCapacity=base_capacity,
            configParameters=config_parameters,
            enhancedVpcRouting=enhanced_vpc_routing,
            maxCapacity=max_capacity,
            port=port,
            pricePerformanceTarget=price_performance_target,
            publiclyAccessible=publicly_accessible,
            securityGroupIds=security_group_ids,
            subnetIds=subnet_ids,
            tags=tags,
        )
        response = self.client.update_workgroup(
            **params
        )
        if wait:
            self.wait_update_workgroup(workgroup_name)
            return self.get_workgroup(workgroup_name)
        return response.get("workgroup", {})
    
    
    def wait_update_namespace(
        self,
        namespace_name: str,
        timeout: Optional[int] = 900,
        interval: Optional[int] = 10,
    ) -> bool:
        """
        Wait until the namespace reaches AVAILABLE state.
        
        """
        self.log_stream.info(f"Waiting for namespace {namespace_name} to be updated...")
        return self.wait_create_namespace(
            namespace_name=namespace_name,
            timeout=timeout,
            interval=interval,
        )
    
    def wait_update_workgroup(
        self, 
        workgroup_name: str, 
        timeout: Optional[int] = 900, 
        interval: Optional[int] = 10,
    ) -> bool:
        """
        Wait until the workgroup reaches AVAILABLE state.
        
        """
        self.log_stream.info(f"Waiting for workgroup {workgroup_name} to be updated...")
        return self.wait_create_workgroup(
            workgroup_name=workgroup_name,
            timeout=timeout,
            interval=interval,
        )

