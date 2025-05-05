#!/usr/bin/python
# -*- coding: utf-8 -*-
import jmespath

from typing import Optional, Dict, Union, Any, List
from pangu.particle.log.log_stream import LogStream
from pangu.particle.log.log_group import LogGroup


class AwsClient:
    """
    Base class for AWS clients.
    This class provides a common interface for AWS clients, including logging and plugin registration.
    Normally set the log module to log group.
    
    """

    REGION_NAME = "ap-southeast-2"
    MAX_PAGINATE = 100

    def __init__(
        self,
        account_id: Optional[str] = None,
        service: Optional[str] = None,
        region: Optional[str] = None,
        plugin: Optional[Dict[str, Any]] = None,
        log_group: Optional[LogGroup] = None,
        max_paginate: Optional[int] = None,
        **kwargs: Optional[Dict[str, Any]],
    ):
        self.account_id = account_id
        self.region = region or self.REGION_NAME
        self.service = service
        self.plugin = plugin or {}
        self.extra_config = kwargs
        self.max_paginate = max_paginate or self.MAX_PAGINATE
        self.log_stream = LogStream(
            name=f"{self.__class__.__name__}:{self.service}:{self.region}:{self.account_id}",
        )
        if log_group:
            self.log_group = log_group
            self.log_stream = self.log_group.register_stream(self.log_stream)
        else:
            self.log_group = None

    def register_plugin(self, name: str, plugin: Any):
        """
        Register a plugin to the client.
        
        """
        if name in self.plugin:
            raise ValueError(f"Plugin {name} already registered.")
        self.plugin[name] = plugin
        return name, plugin

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.__class__.__name__}(service={self.service}, region={self.region}, account_id={self.account_id})"

    @property
    def dict(self):
        return {
            "account_id": self.account_id,
            "region": self.region,
            "service": self.service,
            "plugin": self.plugin,
            "log_stream": self.log_stream.name,
        }

    def log(
        self,
        message: str,
        level: str = "INFO",
        **kwargs: Optional[Dict[str, str]],
    ):
        """
        Log a message to the log stream.
        
        """
        self.log_stream.log(
            level=level,
            message=message,
            **kwargs,
        )

    def pop_list(
        self,
        data: List,
        index: int = 0,
        default: Optional[Any] = None,
    ) -> Union[Dict[str, Any], None]:
        """
        Pop out a list of data by index.
        When the index is out of range, return the default value.

        """
        if index < 0 or index >= len(data):
            return default

        try:
            return data.pop(index)
        except Exception as e:
            return default

    def slice_list(
        self,
        data: List,
        start: int = 0,
        end: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return a slice of the list between start and end indexes.
        If end is None, return the rest of the list.
        
        """
        if end is None:
            end = len(data)
        return data[start:end]

    def strip_params(
        self,
        **kwargs: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Strip None values from a group of kwargs.
        And return a dictionary of the remaining values.
        This is useful for filtering out None values from the parameters passed to AWS API calls.
        
        """
        return {k: v for k, v in kwargs.items() if v is not None}

    def search_metadata(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        expression: str,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Use jmespath to query the data.
        This is useful for filtering out data from the AWS API response.
        
        """
        return jmespath.search(expression, data)
    