import boto3
import time
from typing import Optional, Dict, Union, Any, List

from pangu.aws.base.aws_client import AwsClient
from pangu.particle.log.log_group import LogGroup
from pangu.particle.log.log_stream import LogStream
from pangu.aws.session import AwsSession
from pangu.aws.waiter import Waiter

class Ec2Client(AwsClient):
    """
    Inherit from the base class AwsClient.
    Provides a common interface for AWS EC2 clients.
    Including platform behaviors including logging and plugin registration.
    
    """

    def __init__(
        self,
        account_id: Optional[str] = None,
        service: Optional[str] = "ec2",
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
            self.client = session.client(service_name=service, region_name=region)
        else:
            self.client = boto3.client(
                service_name=service,
                region_name=region,
                **kwargs,
            )

    # --- VPCs ----------------------------------------------------------

    def list_vpcs(
        self,
        filters: Optional[List[Dict[str, Any]]] = None,
        vpc_ids: Optional[List[str]] = None,
        max_results: Optional[int] = 100,
        dry_run: Optional[bool] = False,
    ) -> List[Dict[str, Any]]:
        """
        List all VPC configurations in the current region/account.

        """
        vpcs = []
        next_token = None
        for _ in range(self.max_paginate):
            params = self.strip_params(
                Filters=filters,
                VpcIds=vpc_ids,
                MaxResults=max_results,
                DryRun=dry_run,
                NextToken=next_token,
            )
            response = self.client.describe_vpcs(
                **params,
            )
            vpcs.extend(response["Vpcs"])
            next_token = response.get("NextToken")
            if not next_token: break
            
        return vpcs

    def get_default_vpc(
        self,
        dry_run: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Get the default VPC for the current region/account.

        """
        vpcs = self.list_vpcs(
            filters=[
                {"Name": "is-default", "Values": ["true"]},
            ],
            dry_run=dry_run,
        )
        return self.pop_list(data=vpcs, index=0, default={})

    def get_vpc(
        self,
        vpc_id: str,
        dry_run: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Get the VPC configuration by VPC ID.

        """
        vpcs = self.list_vpcs(
            vpc_ids=[vpc_id],
            max_results=None,
            dry_run=dry_run,
        )
        return self.pop_list(data=vpcs, index=0, default={})


    # --- Security Groups -----------------------------------------------


    def create_security_group(
        self,
        group_name: str,
        description: str = "",
        vpc_id: Optional[str] = None,
        tag_specifications: Optional[List[Dict[str, Any]]] = None,
        dry_run: Optional[bool] = False,
        wait: Optional[bool] = True,
        exists_ok: Optional[bool] = True,
    ) -> Dict[str, Any]:
        """
        Create a new security group.
        If exists_ok is False, raise an exception.
        If exists_ok is True, return the existing group id.

        """
        if self.exists_security_group_by_name(group_name=group_name, vpc_id=vpc_id):
            if not exists_ok:
                raise Exception(f"Security group {group_name} already exists.")
            else:
                config = self.get_security_group_by_name(
                    group_name=group_name,
                    vpc_id=vpc_id,
                    dry_run=dry_run,
                )
                return config.get("GroupId", None)
                
        params = self.strip_params(
            GroupName=group_name,
            Description=description,
            VpcId=vpc_id,
            TagSpecifications=tag_specifications,
            DryRun=dry_run,
        )
        response = self.client.create_security_group(
            **params,
        )
        if wait:
            self.wait_create_security_group(group_id=response.get("GroupId", {}), vpc_id=vpc_id)
        return response.get("GroupId", None)

    def wait_create_security_group(
        self,
        group_id: str,
        vpc_id: str,
        timeout: Optional[int] = 900,
        interval: Optional[int] = 10,
    ) -> bool:
        """
        Wait until the security group (by ID and VPC) is created.
        """
        waiter = Waiter(
            getter=self.get_security_group_by_id,
            get_path="GroupId",
            expected=group_id,
            params={"group_id": group_id, "vpc_id": vpc_id},
            interval=interval,
            timeout=timeout,
            compare_mode="==",
            description=f"Wait for security group {group_id} in VPC {vpc_id} to be created",
            log_stream=self.log_stream,
        )
        return waiter.wait()

    def get_security_group(
        self,
        vpc_id: str,
        max_results: Optional[int] = 100,
        filters: Optional[List[Dict[str, Any]]] = None,
        dry_run: Optional[bool] = False,
    ):
        """
        Possible values for filters:
        group-id: The security group ID.
        description: The security groups description.
        group-name: The security group name.
        owner-id: The security group owner ID.
        primary-vpc-id: The VPC ID in which the security group was created.

        """
        groups = []
        next_token = None
        for _ in range(self.max_paginate):
            params = self.strip_params(
                VpcId=vpc_id,
                MaxResults=max_results,
                Filters=filters,
                DryRun=dry_run,
                NextToken=next_token,
            )
            response = self.client.get_security_groups_for_vpc(
                **params,
            )
            groups.extend(response.get("SecurityGroupForVpcs", []))
            next_token = response.get("NextToken")
            if not next_token:
                break
        return self.pop_list(data=groups, index=0, default={})

    def get_security_group_by_id(
        self,
        group_id: str,
        vpc_id: str,
        max_results: Optional[int] = 100,
        dry_run: Optional[bool] = False,
    ):
        return self.get_security_group(
            vpc_id=vpc_id,
            filters=[
                {"Name": "group-id", "Values": [group_id]},
            ],
            max_results=max_results,
            dry_run=dry_run,
        )

    def get_security_group_by_name(
        self,
        group_name: str,
        vpc_id: str,
        max_results: Optional[int] = 100,
        dry_run: Optional[bool] = False,
    ):
        """
        Get the security group by name.
        
        """
        return self.get_security_group(
            vpc_id=vpc_id,
            filters=[
                {"Name": "group-name", "Values": [group_name]},
            ],
            max_results=max_results,
            dry_run=dry_run,
        )

    def exists_security_group_by_name(
        self,
        group_name: str,
        vpc_id: str,
    ):
        """
        Check if the security group exists by name.
        
        """
        group = self.get_security_group_by_name(
            group_name=group_name,
            vpc_id=vpc_id,
        )
        return True if group else False

    def list_security_groups(
        self,
        group_ids: Optional[list] = None,
        group_names: Optional[list] = None,
        max_results: Optional[int] = 100,
        dry_run: Optional[bool] = False,
        filters: Optional[Dict[str, Union[str, list]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all security groups in the current region/account.
        Possible values for filters:
        group-id: The security group ID.
        group-name: The security group name.
        owner-id: The security group owner ID.
        primary-vpc-id: The VPC ID in which the security group was created.
        
        """
        groups = []
        next_token = None
        for _ in range(self.max_paginate):
            params = self.strip_params(
                GroupIds=group_ids,
                GroupNames=group_names,
                MaxResults=max_results,
                DryRun=dry_run,
                Filters=filters,
                NextToken=next_token,
            )
            try:
                response = self.client.describe_security_groups(**params)
                groups.extend(response.get("SecurityGroups", []))
                next_token = response.get("NextToken")
            except Exception as error:
                if "InvalidGroup.NotFound" in str(error):
                    groups = []
                else:
                    raise error
            if not next_token:
                break
        return groups

    def list_security_group_by_vpc(
        self,
        vpc_id: str,
        max_results: Optional[int] = 100,
        dry_run: Optional[bool] = False,
    ) -> List[Dict[str, Any]]:
        """
        List all security groups in the VPC.
        
        """
        return self.list_security_group(
            filters=[{"Name": "vpc-id", "Values": [vpc_id]}],
            max_results=max_results,
            dry_run=dry_run,
        )

    def delete_security_group(
        self,
        group_id: str,
        group_name: Optional[str] = None,
        dry_run: Optional[bool] = False,
        wait: Optional[bool] = True,
    ):
        """
        Delete the security group by ID or name.
        
        """
        params = self.strip_params(
            GroupId=group_id,
            GroupName=group_name,
            DryRun=dry_run,
        )
        response = self.client.delete_security_group(
            **params,
        )
        if wait:
            self.wait_delete_security_group(
                group_id=group_id,
            )
        return response.get("GroupId", {})

    def wait_delete_security_group(
        self,
        group_id: str,
        timeout: Optional[int] = 900,
        interval: Optional[int] = 10,
    ) -> bool:
        """
        Wait until the security group is deleted.
        
        """
        waiter = Waiter(
            getter=self.list_security_groups,
            get_path="",
            expected=None,
            params={"group_ids": [group_id]},
            interval=interval,
            timeout=timeout,
            compare_mode="exists",
            invert=True,
            description=f"Wait for deletion of security group {group_id}",
            log_stream=self.log_stream,
        )
        return waiter.wait()

    # --- Security Group Rules -------------------------------------------

    def authorize_security_group_ingress(
        self,
        cidr_ip: str,
        from_port: int,
        group_id: str,
        group_name: Optional[str] = None,
        ip_permisions: Optional[Dict[str, Any]] = None,
        ip_protocol: Optional[str] = None,
        source_security_group_name: Optional[str] = None,
        source_security_group_owner_id: Optional[str] = None,
        to_port: int = 0,
        tag_specifications: Optional[List[Dict[str, Any]]] = None,
        dry_run: Optional[bool] = False,
    ) -> Dict[str, Any]:
        params = self.strip_params(
            CidrIp=cidr_ip,
            FromPort=from_port,
            GroupId=group_id,
            GroupName=group_name,
            IpPermissions=ip_permisions,
            IpProtocol=ip_protocol,
            SourceSecurityGroupName=source_security_group_name,
            SourceSecurityGroupOwnerId=source_security_group_owner_id,
            ToPort=to_port,
            TagSpecifications=tag_specifications,
            DryRun=dry_run,
        )
        response = self.client.authorize_security_group_ingress(
            **params,
        )
        return response.get("SecurityGroupRules", [])

    def authorise_ingress_from_cidr_ips(
        self,
        group_id: str,
        cidr_ips_configs: List[Dict[str, Any]],
    ):
        response = []
        for cidr_ip_config in cidr_ips_configs:
            response.append(
                self.authorize_security_group_ingress(
                    group_id=group_id,
                    cidr_ip=cidr_ip_config["cidr_ip"],
                    ip_protocol=cidr_ip_config["ip_protocol"],
                    from_port=cidr_ip_config["from_port"],
                    to_port=cidr_ip_config["to_port"],
                )
            )
        return response

    def authorise_ingress_from_security_groups(
        self,
        group_id: str,
        security_groups_configs: List[Dict[str, Any]],
    ):
        response = []
        for security_group_config in security_groups_configs:
            response.append(
                self.authorize_security_group_ingress(
                    group_id=group_id,
                    ip_permisions=[
                        {
                            "IpProtocol": security_group_config["ip_protocol"],
                            "FromPort": security_group_config["from_port"],
                            "ToPort": security_group_config["to_port"],
                            "UserIdGroupPairs": [
                                {
                                    "GroupId": security_group_config.get(
                                        "security_group_id", group_id
                                    ),
                                }
                            ],
                        }
                    ],
                )
            )
        return response

    def authorise_ingress_from_self(
        self,
        group_id: str,
        security_groups_configs: List[Dict[str, Any]],
    ):
        response = []
        for security_group_config in security_groups_configs:
            response.append(
                self.authorize_security_group_ingress(
                    group_id=group_id,
                    ip_protocol=security_group_config["ip_protocol"],
                    from_port=security_group_config["from_port"],
                    to_port=security_group_config["to_port"],
                )
            )
        return response
