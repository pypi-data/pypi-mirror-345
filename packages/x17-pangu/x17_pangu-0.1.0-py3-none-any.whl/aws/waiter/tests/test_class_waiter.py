from typing import Any, Dict

import jmespath
import pytest

from pangu.aws.waiter.waiter import Waiter


@pytest.fixture
def sample_getter_success():
    def _getter(**kwargs) -> Dict[str, Any]:
        return {"status": "ready", "tags": ["alpha", "beta"], "data": {"exists": True}}

    return _getter


@pytest.fixture
def sample_getter_failure():
    def _getter(**kwargs) -> Dict[str, Any]:
        return {"status": "pending", "tags": ["gamma"], "data": {}}

    return _getter


@pytest.fixture
def slow_getter():
    def _getter(**kwargs):
        return {"status": "pending"}

    return _getter


@pytest.mark.parametrize(
    "compare_mode,expected,get_path",
    [
        ("==", "ready", "status"),
        ("!=", "pending", "status"),
        ("in", "alpha", "tags"),
        ("not in", "delta", "tags"),
        ("exists", True, "data.exists"),
        ("not exists", None, "nonexistent.key"),
    ],
)
def test_waiter_success_modes(sample_getter_success, compare_mode, expected, get_path):
    waiter = Waiter(
        getter=sample_getter_success,
        get_path=get_path,
        expected=expected,
        compare_mode=compare_mode,
        interval=0.01,
        attempts=3,
    )
    result = waiter.wait()
    assert result is True


def test_waiter_inverted_mode(sample_getter_failure):
    waiter = Waiter(
        getter=sample_getter_failure,
        get_path="status",
        expected="ready",
        compare_mode="==",
        invert=True,
        interval=0.01,
        attempts=3,
    )
    result = waiter.wait()
    assert result


def test_waiter_timeout(sample_getter_failure):
    waiter = Waiter(
        getter=sample_getter_failure,
        get_path="status",
        expected="ready",
        compare_mode="==",
        interval=0.01,
        attempts=2,
    )
    with pytest.raises(TimeoutError):
        waiter.wait()


def test_waiter_soft_timeout(sample_getter_failure):
    waiter = Waiter(
        getter=sample_getter_failure,
        get_path="status",
        expected="ready",
        compare_mode="==",
        interval=0.01,
        attempts=2,
    )
    result = waiter.wait(check=False)
    assert not result


def test_waiter_invalid_compare_mode(sample_getter_success):
    waiter = Waiter(
        getter=sample_getter_success,
        get_path="status",
        expected="ready",
        compare_mode="INVALID",
        interval=0.01,
        attempts=1,
    )
    with pytest.raises(ValueError):
        waiter.wait()


def test_repr_and_dict(sample_getter_success):
    waiter = Waiter(
        getter=sample_getter_success,
        get_path="status",
        expected="ready",
        compare_mode="==",
    )
    assert isinstance(str(waiter), str)
    assert isinstance(repr(waiter), str)

    info = waiter.dict
    assert isinstance(info, dict)
    assert info["getter"] == "_getter"
    assert "expected" in info
    assert "compare_mode" in info


def test_waiter_timeout_auto_attempts(slow_getter):
    """
    Verify that timeout parameter correctly overrides attempts.
    delay=0.1, timeout=0.3 => attempts=3
    """
    waiter = Waiter(
        getter=slow_getter,
        get_path="status",
        expected="ready",
        compare_mode="==",
        interval=0.1,
        timeout=0.3,  # auto => 3 attempts
    )
    assert waiter.attempts == 3
    with pytest.raises(TimeoutError):
        waiter.wait()
