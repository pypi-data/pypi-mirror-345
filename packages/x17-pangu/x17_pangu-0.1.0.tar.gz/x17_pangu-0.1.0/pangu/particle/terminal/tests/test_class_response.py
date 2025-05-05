import pytest
from pangu.particle.terminal.response import Response
from pangu.particle.datestamp import Datestamp
from pangu.particle.duration import Duration

class MockCompletedProcess:
    def __init__(self, returncode=0, stdout="", stderr="", args=None):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.args = args or []

def test_response_init_and_properties():
    started = Datestamp.now()
    ended = Datestamp.now()
    
    res = Response(
        code=0,
        stdout="Hello World",
        stderr="",
        started=started,
        ended=ended,
        cwd="/tmp",
        env={"ENV": "test"},
        cmdline="echo Hello",
        captured=True,
        signal=None,
    )

    assert res.code == 0
    assert res.stdout == "Hello World"
    assert res.stderr == ""
    assert res.started == started
    assert res.ended == ended
    assert res.cwd == "/tmp"
    assert res.env == {"ENV": "test"}
    assert res.cmdline == "echo Hello"
    assert res.captured is True
    assert res.signal is None
    assert isinstance(res.duration, Duration)
    assert res.success is True
    assert res.failed is False
    assert res.timeout is False

def test_response_from_dict():
    data = {
        "code": 0,
        "stdout": "Success",
        "stderr": "",
        "started": Datestamp.now().datestamp_str,
        "started_tz": "UTC",
        "ended": Datestamp.now().datestamp_str,
        "ended_tz": "UTC",
        "cwd": "/path",
        "env": {"USER": "test"},
        "cmdline": "ls",
        "captured": True,
        "signal": None,
    }
    res = Response.from_dict(data)
    assert res.stdout == "Success"
    assert res.cwd == "/path"
    assert res.env == {"USER": "test"}
    assert res.captured is True
    assert res.signal is None

def test_response_from_object():
    mock = MockCompletedProcess(
        returncode=1,
        stdout="output",
        stderr="error",
        args=["ls", "-la"]
    )
    started = Datestamp.now()
    ended = Datestamp.now()
    res = Response.from_object(mock, started=started, ended=ended, cwd="/home", env={"A": "B"})
    assert res.code == 1
    assert res.stdout == "output"
    assert res.stderr == "error"
    assert res.cmdline == "ls -la"
    assert res.cwd == "/home"
    assert res.env == {"A": "B"}
    assert res.success is False
    assert res.failed is True

def test_response_str_repr():
    started = Datestamp.now()
    ended = Datestamp.now()
    res = Response(
        code=0,
        stdout="Some output",
        stderr="",
        started=started,
        ended=ended,
    )
    assert str(res) == "Some output"
    assert "Response" in repr(res)
    assert "code=0" in repr(res)
    assert "stdout=Some output" in repr(res)
    assert "stderr=" in repr(res)  # stderr is empty
    assert "started=" in repr(res)
    assert "ended=" in repr(res)

def test_response_dict_and_export():
    started = Datestamp.now()
    ended = Datestamp.now()
    res = Response(
        code=0,
        stdout="stdout content",
        stderr="stderr content",
        started=started,
        ended=ended,
        cwd="/test",
        env={"ENV": "dev"},
        cmdline="ls",
        captured=True,
        signal=None,
    )
    d = res.dict
    exported = res.export()
    assert d["code"] == 0
    assert d["stdout"] == "stdout content"
    assert d["cwd"] == "/test"
    assert d["cmdline"] == "ls"
    assert d == exported