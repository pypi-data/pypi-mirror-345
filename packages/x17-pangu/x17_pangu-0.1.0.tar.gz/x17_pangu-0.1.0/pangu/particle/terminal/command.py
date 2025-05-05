# -*- coding: utf-8 -*-
from typing import Any, Dict, Optional, List
import subprocess
import shlex
import os

from pangu.particle.duration import Duration


class Command:
    """
    Command class to represent a command line instruction.
    It can be used to build command line arguments, manage environment variables,
    and handle command execution parameters.

    """
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Command":
        return cls(
            cmd=data.get("cmd"),
            cwd=data.get("cwd", None),
            env=data.get("env", None),
            shell=data.get("shell", None),
            check=data.get("check", True),
            timeout=Duration.from_dict(data.get("timeout")) if data.get("timeout") else None,
            encoding=data.get("encoding", "utf-8"),
            text=data.get("text", True),
            output=data.get("output", True),
        )
    
    def __init__(
        self, 
        cmd: str, 
        cwd: Optional[str] = None,
        env: Optional[Dict[str, Any]] = None,
        shell: Optional[bool] = None,
        check: Optional[bool] = True,
        timeout: Optional[Duration] = None,
        encoding: str = "utf-8",
        text: Optional[bool] = True,
        output: Optional[str] = True,
    ) -> None:
        self.cmd = cmd
        self.cwd = cwd or os.getcwd()
        self.env = env
        self.check = check
        self.shell = shell if shell is not None else os.name == "nt"
        self.timeout = timeout or Duration(second=60)
        self.encoding = encoding
        self.text = text
        self.output = output

    @property
    def list(self) -> List[str]:
        """
        List of command line arguments
        
        """
        if isinstance(self.cmd, list):
            return self.cmd
        else:
            return shlex.split(self.cmd)
    
    @property
    def dict(self) -> Dict[str, Any]:
        return {
            "cmd": self.cmd,
            "cwd": self.cwd,
            "env": self.env,
            "shell": self.shell,
            "check": self.check,
            "timeout": self.timeout.dict if self.timeout else None,
            "encoding": self.encoding,
            "text": self.text,
            "output": self.output,
        }
    
    @property
    def params(
        self,
    ) -> Dict[str, Any]:
        params = {
            "args": self.list,
            "cwd": self.cwd,
            "env": self.env,
            "shell": self.shell or False,
            "timeout": self.timeout.base if self.timeout else None,
            "check": self.check,
            "capture_output": self.output,
            "text": self.text,
            "encoding": self.encoding,
        }
        return {k: v for k, v in params.items() if v is not None}
    
    def __str__(self) -> str:
        return " ".join(self.list)
    
    def __repr__(self) -> str:
        attributes = []
        for unit, value in self.dict.items():
            if value != 0:
                attributes.append(f"{unit}={value}")
        return f"{self.__class__.__name__}({', '.join(attributes)})"
    
    def add_option(self, option: str, value: Optional[str] = None) -> None:
        """
        Add an option to the command, optionally with a value.
        
        """
        if value is not None:
            self.cmd += f" {option} {shlex.quote(value)}"
        else:
            self.cmd += f" {option}"
    
    def export(self) -> Dict[str, Any]:
        return self.dict
    
    

