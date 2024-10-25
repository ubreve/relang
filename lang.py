import dataclasses
import enum


@dataclasses.dataclass
class Type:
    name: str


@dataclasses.dataclass
class Record:
    name: str
    field_list: list


@dataclasses.dataclass
class Field:
    name: str
    type: Type
    is_key: bool
    is_nullable: bool
    is_unique: bool


class Modifier(enum.Enum):
    KEY_MEMBER = enum.auto()
    NULLABLE = enum.auto()
