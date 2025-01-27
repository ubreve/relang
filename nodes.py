from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class Ref:
    name: str

@dataclass
class RangeDef:
    first: int
    second: int | None
    last: int

@dataclass
class SequenceDef:
    first: int
    second: int | None

@dataclass
class DomainRef:
    name: str

@dataclass
class RecordDef:
    name: str
    field_list: list

@dataclass
class FieldDef:
    name: str
    domain: DomainRef | RangeDef
    is_key: bool
    is_nullable: bool
    is_unique: bool

class FieldModifier(Enum):
    KEY_MEMBER = auto()
    NULLABLE = auto()

@dataclass
class CreateStmt:
    instance_list: list

@dataclass
class CreateInstance:
    name: str
    param_list: list

@dataclass
class KeywordParam:
    name: str
    value: str

@dataclass
class FloatPrimitive:
    value: float

@dataclass
class IntPrimitive:
    value: int

@dataclass
class StringPrimitive:
    value: str

@dataclass
class TruePrimitive:
    pass

@dataclass
class FalsePrimitive:
    pass

@dataclass
class NullPrimitive:
    pass

class Expr:
    """Abstract base class for expression nodes."""
    pass

@dataclass
class Call:
    func: Expr
    param_list: list

@dataclass
class AttrAccess:
    value: Expr
    attr: str

@dataclass
class FieldAccess:
    value: Expr
    field: str

@dataclass
class Addition(Expr):
    left: Expr
    right: Expr

@dataclass
class Subtraction(Expr):
    left: Expr
    right: Expr

@dataclass
class Multiplication(Expr):
    left: Expr
    right: Expr

@dataclass
class Division(Expr):
    left: Expr
    right: Expr

@dataclass
class ArithmeticNegation(Expr):
    value: Expr

@dataclass
class Conjunction(Expr):  # and
    left: Expr
    right: Expr

@dataclass
class Disjunction(Expr):  # or
    left: Expr
    right: Expr

@dataclass
class LogicalNegation(Expr):
    value: Expr

@dataclass
class InExpr(Expr):
    subject: Expr
    container: Expr

@dataclass
class NotInExpr(Expr):
    subject: Expr
    container: Expr

@dataclass
class IsExpr(Expr):
    left: Expr
    right: Expr

@dataclass
class IsNotExpr(Expr):
    left: Expr
    right: Expr

@dataclass
class ComparisonExpr(Expr):
    left: Expr
    right: Expr

@dataclass
class Less(ComparisonExpr):
    pass

@dataclass
class LessEqual(ComparisonExpr):
    pass

@dataclass
class Greater(ComparisonExpr):
    pass

@dataclass
class GreaterEqual(ComparisonExpr):
    pass

@dataclass
class NotEqual(ComparisonExpr):
    pass

@dataclass
class Equal(ComparisonExpr):
    pass
