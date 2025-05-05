import os
import pytest
import sys
from pangu.particle.terminal.terminal import Terminal
from pangu.particle.terminal.command import Command
from pangu.particle.duration import Duration

def test_terminal_initialization_defaults():
    terminal = Terminal()
    assert terminal.cwd is None
    assert terminal.env is None
    assert terminal.encoding == "utf-8"
    assert isinstance(terminal.history, list)
    assert terminal.os_name in ("posix", "nt")

def test_terminal_initialization_custom_values():
    env = {"TEST_VAR": "123"}
    terminal = Terminal(cwd="/tmp", env=env, encoding="utf-16")
    assert terminal.cwd == "/tmp"
    assert terminal.env == env
    assert terminal.encoding == "utf-16"

def test_terminal_platform_properties():
    terminal = Terminal()
    if sys.platform.startswith("win"):
        assert terminal.is_windows is True
        assert terminal.is_linux is False
        assert terminal.is_macos is False
    elif sys.platform.startswith("darwin"):
        assert terminal.is_macos is True
        assert terminal.is_windows is False
        assert terminal.is_linux is False
    else:
        assert terminal.is_linux is True
        assert terminal.is_windows is False
        assert terminal.is_macos is False

def test_terminal_run_success_basic_command():
    terminal = Terminal()
    cmd = Command(cmd="echo hello")
    response = terminal.run(cmd)
    assert response.code == 0
    assert "hello" in response.stdout.lower()
    assert response.cwd == cmd.cwd or os.getcwd()
    assert isinstance(response.duration.base, float)

def test_terminal_run_custom_cwd(tmp_path):
    terminal = Terminal(cwd=str(tmp_path))
    cmd = Command(cmd="echo cwd_test", cwd=str(tmp_path))
    response = terminal.run(cmd)
    assert "cwd_test" in response.stdout.lower()
    assert tmp_path.as_posix() in response.cwd or tmp_path.name in response.cwd

def test_terminal_run_custom_env():
    env = {"CUSTOM_TEST_VAR": "MYVALUE"}
    terminal = Terminal(env=env)
    cmd = Command(
        cmd=["python3", "-c", "import os; print(os.getenv('CUSTOM_TEST_VAR'))"],
        shell=False
    )
    response = terminal.run(cmd)
    print("RESPONSE STDOUT:", response.stdout)
    assert "MYVALUE" in response.stdout
    

def test_terminal_run_custom_encoding():
    terminal = Terminal(encoding="utf-8")
    cmd = Command(cmd="echo test_encoding")
    response = terminal.run(cmd)
    assert "test_encoding" in response.stdout.lower()

def test_terminal_run_with_timeout_handling():
    terminal = Terminal()
    if terminal.is_windows:
        sleep_cmd = "timeout 5"  # Windows的sleep模拟
    else:
        sleep_cmd = "sleep 5"
    cmd = Command(cmd=sleep_cmd, timeout=Duration(second=1), check=False)
    response = terminal.run(cmd)
    assert response.code == -1
    assert "timeout" in response.stderr.lower()

def test_terminal_run_command_not_found():
    terminal = Terminal()
    cmd = Command(cmd="nonexistent_command_xyz", check=False, shell=True)
    response = terminal.run(cmd)
    assert response.code != 0 
    assert "not found" in response.stderr.lower() or "not recognized" in response.stderr.lower()

def test_terminal_history_recording():
    terminal = Terminal()
    cmd = Command(cmd="echo history_test")
    response = terminal.run(cmd)
    assert len(terminal.history) == 1
    record = terminal.history[0]
    assert "command" in record
    assert "response" in record
    assert record["command"]["cmd"] == "echo history_test"
    assert "history_test" in record["response"]["stdout"].lower()