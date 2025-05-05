import math
import time
from typing import Any, Callable, Dict, List, Optional, Union

import jmespath

from pangu.particle.log.log_stream import LogStream


class Waiter:
    """
    A class to wait for a condition to be met by repeatedly calling a getter function.
    The condition is defined by a JMESPath expression and a set of expected values.
    The class supports inversion of the condition, custom interval and number of attempts.
    note that compare mode has to be one of ['==', '!=', 'in', 'not in', 'exists', 'not exists'].

    This class provides a flexible, extensible, and service-agnostic way to wait for changes
    in AWS resource state, or any other asynchronous backend operation. Instead of relying on
    boto3 built-in waiters—which are limited in scope, poorly documented, and hard to customize—
    this implementation offers a unified interface that can operate on any JSON-like API response.

    The condition is evaluated via a JMESPath expression (`get_path`) and compared against a set of
    expected values using various compare modes. Inversion is supported to wait for non-existence or
    negated conditions (e.g., wait until a resource is deleted). This class also supports configurable
    timeouts and polling intervals, and integrates with the platform's logging system for observability.

    This class is essential when building generalized AWS service clients, where standardized polling
    behavior is required across services like EC2, S3, Redshift, VPC, and beyond.

    """

    def __init__(
        self,
        getter: Callable[..., Dict],
        get_path: str,
        expected: Union[Any, List[Any]],
        params: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        interval: int = 1,
        attempts: int = 5,
        timeout: Optional[int] = None,
        invert: bool = False,
        compare_mode: str = "==",
        log_stream: Optional[LogStream] = None,
    ):
        self.getter = getter
        self.getter_name = getattr(getter, "__name__", str(getter))
        self.get_path = get_path or "@"
        self.expected = set(expected) if isinstance(expected, list) else {expected}
        self.params = params or {}
        self.interval = interval
        if timeout is not None:
            self.attempts = max(1, math.ceil(timeout / interval))
        else:
            self.attempts = attempts
        self.invert = invert
        self.compare_mode = compare_mode
        self.description = description or get_path
        self.log_stream = log_stream or LogStream(
            name=f"{self.__class__.__name__}:{self.getter_name}"
        )

    @property
    def dict(self) -> Dict[str, Any]:
        return {
            "getter": self.getter_name,
            "get_path": self.get_path,
            "expected": self.expected,
            "params": self.params,
            "interval": self.interval,
            "attempts": self.attempts,
            "invert": self.invert,
            "compare_mode": self.compare_mode,
            "description": self.description,
            "log_stream": self.log_stream.name,
        }

    def __str__(self):
        return f"{self.__class__.__name__}({self.getter_name})"

    def __repr__(self):
        attributes = []
        for unit, value in self.dict.items():
            if value is not None:
                attributes.append(f"{unit}={str(value)}")
        return f"{self.__class__.__name__}({', '.join(attributes)})"

    def wait(self, check=True) -> bool:
        """
        Run the waiter until the expected condition is met or timeout occurs.

        """
        for attempt in range(1, self.attempts + 1):
            try:
                result = self.getter(**self.params)
                actual = jmespath.search(self.get_path, result)
            except Exception as e:
                if check: 
                    raise e
                self.log_stream.warn(f"Attempt {attempt}: Error - {str(e)}")
                actual = None

            self.log_stream.debug(
                f"Attempt {attempt}: actual={actual}, expected={self.expected}"
            )

            match = self.evaluate(actual)
            if self.invert:
                match = not match

            if match:
                self.log_stream.info(
                    f"Success: {self.description} matched {self.compare_mode} {self.expected} (got {actual})"
                )
                return True

            self.log_stream.debug(
                f"Attempt {attempt}/{self.attempts}: actual={actual}, expected={self.expected}"
            )
            time.sleep(self.interval)

        if check:
            raise TimeoutError(
                f"Timeout: {self.description} did not meet expected value(s) {self.expected}"
            )
        return False

    def evaluate(self, actual: Any) -> bool:
        """
        Evaluate the actual value against the expected values based on the compare mode.

        """
        if self.compare_mode == "==":
            return actual in self.expected
        elif self.compare_mode == "!=":
            return actual not in self.expected
        elif self.compare_mode == "in":
            return isinstance(actual, list) and any(x in actual for x in self.expected)
        elif self.compare_mode == "not in":
            return isinstance(actual, list) and all(
                x not in actual for x in self.expected
            )
        elif self.compare_mode == "exists":
            return actual not in (None, {}, [], "")
        elif self.compare_mode == "not exists":
            return actual in (None, {}, [], "")
        else:
            raise ValueError(f"Unsupported compare_mode: {self.compare_mode}")
