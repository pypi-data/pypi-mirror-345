import os
import sys
import platform
import socket
import logging
from enum import Enum, auto
from typing import Any, Dict, Optional

from pangu.particle.base.platform_status import BasePlatformStatus


class BasePlatform:
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.status = BasePlatformStatus.INIT
        self.config = config or {}
        self.plugins: Dict[str, Any] = {}
        self.env_info = self.detect_environment()
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(levelname)s][%(name)s] %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def detect_environment(self) -> Dict[str, Any]:
        return {
            "platform": sys.platform,
            "os_name": os.name,
            "python_version": platform.python_version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": socket.gethostname(),
            "ip_address": socket.gethostbyname(socket.gethostname()),
            "is_docker": self._is_docker(),
            "env_vars": dict(os.environ),
        }

    def _is_docker(self) -> bool:
        try:
            with open("/proc/1/cgroup", "rt") as f:
                return "docker" in f.read() or "kubepods" in f.read()
        except Exception:
            return False

    def load_config(self, path: Optional[str] = None, env_prefix: Optional[str] = None):
        try:
            self.logger.info("Loading configuration...")
            # TODO: implement file/env loading logic
            self.status = BasePlatformStatus.LOADED
        except Exception as e:
            self.status = BasePlatformStatus.FAILED
            self.logger.error(f"Failed to load config: {e}")
            raise

    def register_plugin(self, name: str, plugin: Any):
        self.plugins[name] = plugin
        self.logger.info(f"Plugin registered: {name}")

    def get_plugin(self, name: str) -> Any:
        return self.plugins.get(name)

    def initialize(self):
        try:
            self.logger.info("Initializing platform...")
            self.status = BasePlatformStatus.READY
        except Exception as e:
            self.status = BasePlatformStatus.FAILED
            self.logger.error(f"Initialization failed: {e}")
            raise

    def shutdown(self):
        try:
            self.logger.info("Shutting down platform...")
            self.status = BasePlatformStatus.CLOSED
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")

    def is_ready(self) -> bool:
        return self.status == BasePlatformStatus.READY
