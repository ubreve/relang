from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class DomainRef:
    name: str


@dataclass
class DomainSpec:
    value: DomainRef


@dataclass
class RecordDef:
    name: str
    field_list: list


@dataclass
class FieldDef:
    name: str
    domain: DomainSpec
    is_key: bool
    is_nullable: bool
    is_unique: bool


class FieldModifier(Enum):
    KEY_MEMBER = auto()
    NULLABLE = auto()
