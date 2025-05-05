#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Optional, Dict, Any, List

from pangu.particle.text.id import Id
from pangu.particle.log.log_group import LogGroup
from pangu.particle.log.log_stream import LogStream
from pangu.aws.base.aws_client import AwsClient

class AwsResource:
    
    """
    Base class for AWS resources.
    This class provides a common interface for AWS resources, including logging and plugin registration.
    Normally set the log module to log stream.
    
    """
    
    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        resource_id: str,
        account_id: Optional[str] = None,
        region: Optional[str] = None,
        log_group: Optional[LogGroup] = None,
    ):
        return cls(
            resource_id=resource_id,
            account_id=account_id,
            region=region,
            raw = data,
            log_group = log_group,
        )

    def __init__(
        self,
        resource_id: Optional[str] = None,
        account_id: Optional[str] = None,
        region: Optional[str] = None,
        raw: Optional[Dict[str, Any]] = None,
        log_group: Optional[LogGroup] = None,
    ):
        self.resource_id = resource_id or f"{self.__class__.__name__}:{Id.uuid(8)}"
        self.account_id = account_id
        self.region = region or AwsClient.REGION_NAME
        self.plugin = {}
        raw = raw or {}
        self.log_stream = LogStream(
            name=f"{self.__class__.__name__}:{self.region}:{self.account_id}:{self.resource_id}"
        )
        if log_group:
            self.log_group = log_group
            self.log_stream = self.log_group.register_stream(self.log_stream)
        else:
            self.log_group = None
        
        for key, value in raw.items():
            if not key.startswith("_") and key not in ["raw"]:
                setattr(self, key, value)
            
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return f"{self.__class__.__name__}(region={self.region}, account_id={self.account_id})"
            
    def log(
        self,
        message: str,
        level: str = "INFO",
        **kwargs: Optional[Dict[str, str]],
    ):
        """
        Log a message to the log stream.
        This method allows logging messages at different levels (e.g., INFO, ERROR).
        Normally assign the log level to the log stream.

        Args:
            message (str): _description_
            level (str, optional): _description_. Defaults to "INFO".
        
        """
        self.log_stream.log(
            level = level, 
            message = message,
            **kwargs,
        )

    def register_plugin(self, name: str, plugin: Any):
        """
        Register a plugin to the resource.
        Plugin could be any object (AwsResource, AwsClient, etc.)
        This method allows adding custom functionality to the resource.
        
        Args:
            name (str): The name of the plugin.
            plugin (Any): The plugin to register.
        Returns:
            Tuple[str, Any]: The name and plugin.
        """
        if name in self.plugin:
            raise ValueError(f"Plugin {name} already registered.")
        self.plugin[name] = plugin
        return name, plugin

    @property
    def dict(self) -> Dict[str, Any]:
        """
        Convert the resource to a dictionary representation.

        Returns:
            Dict[str, Any]: _description_
        """
        result = {
            key: value
            for key, value in vars(self).items()
            if not key.startswith("_") and not callable(value) and key not in ["log_stream", "log_group"]
        }
        result["log_stream"] = self.log_stream.name if self.log_stream else None
        result["log_group"] = self.log_group.name if self.log_group else None
        return result
