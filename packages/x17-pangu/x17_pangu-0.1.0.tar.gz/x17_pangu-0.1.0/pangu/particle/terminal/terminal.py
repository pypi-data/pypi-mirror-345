# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from typing import Any, Dict, Optional

from pangu.particle.terminal.command import Command
from pangu.particle.terminal.response import Response
from pangu.particle.datestamp import Datestamp
from pangu.particle.duration import Duration


class Terminal:
    """
    A cross-platform virtual Terminal.
    Responsible for executing commands within its own environment context.
    
    """

    def __init__(
        self,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        encoding: str = "utf-8",
    ):
        self.cwd = cwd
        self.env = env
        self.os_name = os.name
        self.encoding = encoding
        self.history = []

    @property
    def is_windows(self) -> bool:
        return sys.platform.startswith("win")

    @property
    def is_macos(self) -> bool:
        return sys.platform.startswith("darwin")

    @property
    def is_linux(self) -> bool:
        return sys.platform.startswith("linux")

    def run(self, cmd: Command) -> Response:
        start = Datestamp.now()
        params = cmd.params.copy()
        params["cwd"] = cmd.cwd or self.cwd or os.getcwd()
        params["env"] = cmd.env or self.env or os.environ.copy()
        params["encoding"] = cmd.encoding or self.encoding

        try:
            result = subprocess.run(**params)
            end = Datestamp.now()
            response = Response.from_object(
                obj=result,
                started=start,
                ended=end,
                cwd=params["cwd"],
                env=params["env"],
                captured=True,
            )
        except subprocess.TimeoutExpired as e:
            end = Datestamp.now()
            response = Response(
                code=-1,
                stdout="",
                stderr=f"Timeout after {params.get('timeout')} seconds",
                started=start,
                ended=end,
                cwd=params["cwd"],
                env=params["env"],
                cmdline=" ".join(cmd.list),
                captured=True,
                signal=None,
            )
        except Exception as e:
            end = Datestamp.now()
            response = Response(
                code=-1,
                stdout="",
                stderr=str(e),
                started=start,
                ended=end,
                cwd=params["cwd"],
                env=params["env"],
                cmdline=" ".join(cmd.list),
                captured=True,
                signal=None,
            )
        
        self.record(cmd, response)
        return response

    def record(self, cmd: Command, response: Response) -> None:
        self.history.append({
            "command": cmd.dict,
            "response": response.dict,
        })