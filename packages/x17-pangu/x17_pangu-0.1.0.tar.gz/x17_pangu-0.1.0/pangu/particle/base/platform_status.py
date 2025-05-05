from enum import Enum, auto


class BasePlatformStatus(Enum):
    INIT = auto(), "Platform nitialized"
    LOADED = auto(), "Platform loaded"
    READY = auto(), "Platform ready"
    FAILED = auto(), "Platform failed"
    CLOSED = auto(), "Platform closed"

    @classmethod
    def from_value(cls, value: int):
        for status in cls:
            if status.value == value:
                return status
        raise ValueError(f"No PlatformStatus with value {value}")

    @classmethod
    def choices(cls):
        return [(status.name, status.description) for status in cls]

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    @property
    def dict(self):
        return {"name": self.name, "value": self.value, "description": self.description}

    def __repr__(self):
        attributes = []
        for unit, value in self.dict.items():
            if value != 0:
                attributes.append(f"{unit}={value}")
        return f"{self.__class__.__name__}({', '.join(attributes)})"

    def __str__(self):
        return self.__repr__()
