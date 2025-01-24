from pprint import pp
import sys

import ply.yacc as yacc

from tokens import tokens  # import required by ply
from nodes import *


# ordered from lowest to highest precedence
# each line contains tokens with the same precedence
# line structure: [associativity, tokens...]
# associativity is one of "left", "right" and "nonassoc"
precedence = [
    ['left', 'or'],
    ['left', 'and'],
    ['right', 'not'],
    ['nonassoc',
        'less', 'less_equal', 'greater', 'greater_equal', 'not_equal',
        'equal_equal'
    ],
    ['left', 'in', 'not_in', 'is', 'is_not'],
    ['left', 'plus', 'minus'],
    ['left', 'star', 'slash'],
    ['right', 'unary_minus'],
    ['left', 'access']
]

def p_module_stmt(p):
    'module : stmt'
    p[0] = p[1]

def p_module_empty(p):
    'module : empty'
    p[0] = None

# def p_empty_stmt(p):
#     'stmt : empty'
#     p[0] = None

# def p_expr_stmt(p):
#     'stmt : expr'
#     p[0] = p[1]

def p_record_def_stmt(p):
    'stmt : record_def'
    p[0] = p[1]

def p_create_stmt(p):
    'stmt : create_stmt'
    p[0] = p[1]

def p_record_def(p):
    'record_def : record name open_brace field_list close_brace'
    p[0] = RecordDef(
        name=p[2],
        field_list=p[4]
    )

def p_field_list_recursive(p):
    'field_list : field_list field semicolon'
    p[1].append(p[2])
    p[0] = p[1]

def p_field_list_empty(p):
    'field_list : empty'
    p[0] = []

def p_field(p):
    'field : name modifier unique_opt domain_spec'
    p[0] = FieldDef(
        name=p[1],
        domain=p[4],
        is_key=(p[2] == FieldModifier.KEY_MEMBER),
        is_nullable=(p[2] == FieldModifier.NULLABLE),
        is_unique=p[3]
    )

def p_modifier_key_member(p):
    'modifier : exclam'
    p[0] = FieldModifier.KEY_MEMBER

def p_modifier_nullable(p):
    'modifier : quest'
    p[0] = FieldModifier.NULLABLE

def p_modifier_none(p):
    'modifier : empty'
    p[0] = None

def p_unique_true(p):
    'unique_opt : unique'
    p[0] = True

def p_unique_false(p):
    'unique_opt : empty'
    p[0] = False

def p_domain_spec_ref(p):
    '''domain_spec : domain_ref
                   | range_def'''
    p[0] = p[1]

def p_domain_ref(p):
    'domain_ref : name'
    p[0] = DomainRef(p[1])

def p_range_def(p):
    'range_def : open_brack int second_opt two_dots int close_brack'
    p[0] = RangeDef(first=p[2], second=p[3], last=p[5])

def p_second_opt_present(p):
    'second_opt : comma int'
    p[0] = p[2]

def p_second_opt_absent(p):
    'second_opt : empty'
    p[0] = None

def p_sequence_def(p):
    'sequence_def : open_brack int second_opt two_dots close_brack'
    p[0] = SequenceDef(first=p[2], second=p[3])

def p_create(p):
    'create_stmt : create record_creation_list semicolon'
    p[0] = CreateStmt(p[2])

def p_record_creation_list(p):
    'record_creation_list : record_creation_list_prefix'
    p[0] = p[1]

def p_record_creation_list_empty(p):
    'record_creation_list : empty'
    p[0] = []

def p_record_creation_list_single(p):
    'record_creation_list_prefix : record_creation'
    p[0] = [p[1]]

def p_record_creation_list_recursive(p):
    'record_creation_list_prefix : record_creation_list_prefix comma record_creation'
    p[1].append(p[3])
    p[0] = p[1]

def p_record_creation(p):
    'record_creation : name param_list'
    p[0] = CreateInstance(name=p[1], param_list=p[2])

def p_param_list(p):
    'param_list : open_paren param_list_prefix close_paren'
    p[0] = p[2]

def p_param_list_empty(p):
    'param_list : open_paren close_paren'
    p[0] = []

def p_param_list_prefix_single(p):
    'param_list_prefix : param'
    p[0] = [p[1]]

def p_param_list_prefix_recursive(p):
    'param_list_prefix : param_list_prefix comma param'
    p[1].append(p[3])
    p[0] = p[1]

def p_param_positional(p):
    'param : expr'
    p[0] = p[1]

def p_param_keyword(p):
    'param : name equal expr'
    p[0] = KeywordParam(name=p[1], value=p[3])

def p_expr_embraced(p):
    'expr : open_paren expr close_paren'
    p[0] = p[2]

def p_expr_primitive(p):
    'expr : primitive'
    p[0] = p[1]

def p_expr_ref(p):
    'expr : name'
    p[0] = Ref(p[1])

def p_expr_call(p):
    'expr : expr param_list'
    p[0] = Call(func=p[1], param_list=p[2])

def p_expr_attr_access(p):
    'expr : expr dot name %prec access'
    p[0] = AttrAccess(value=p[1], attr=p[3])

def p_expr_field_access(p):
    'expr : expr colon name %prec access'
    p[0] = FieldAccess(value=p[1], field=p[3])

def p_expr_addition(p):
    'expr : expr plus expr'
    p[0] = Addition(p[1], p[3])

def p_expr_subtraction(p):
    'expr : expr minus expr'
    p[0] = Subtraction(p[1], p[3])

def p_expr_multiplication(p):
    'expr : expr star expr'
    p[0] = Multiplication(p[1], p[3])

def p_expr_division(p):
    'expr : expr slash expr'
    p[0] = Division(p[1], p[3])

def p_expr_arithmetic_negation(p):
    'expr : minus expr %prec unary_minus'
    p[0] = ArithmeticNegation(p[2])

def p_expr_disjunction(p):
    'expr : expr or expr'
    p[0] = Disjunction(p[1], p[3])

def p_expr_conjunction(p):
    'expr : expr and expr'
    p[0] = Conjunction(p[1], p[3])

def p_expr_logical_negation(p):
    'expr : not expr'
    p[0] = LogicalNegation(p[2])

def p_expr_in(p):
    'expr : expr in expr'
    p[0] = InExpr(p[1], p[3])

def p_expr_not_in(p):
    'expr : expr not_in expr'
    p[0] = NotInExpr(p[1], p[3])

def p_expr_is(p):
    'expr : expr is expr'
    p[0] = IsExpr(p[1], p[3])

def p_expr_is_not(p):
    'expr : expr is_not expr'
    p[0] = IsNotExpr(p[1], p[3])

def p_expr_less(p):
    'expr : expr less expr'
    p[0] = Less(p[1], p[3])

def p_expr_less_equal(p):
    'expr : expr less_equal expr'
    p[0] = LessEqual(p[1], p[3])

def p_expr_greater(p):
    'expr : expr greater expr'
    p[0] = Greater(p[1], p[3])

def p_expr_greater_equal(p):
    'expr : expr greater_equal expr'
    p[0] = GreaterEqual(p[1], p[3])

def p_expr_not_equal(p):
    'expr : expr not_equal expr'
    p[0] = NotEqual(p[1], p[3])

def p_expr_equal(p):
    'expr : expr equal_equal expr'
    p[0] = Equal(p[1], p[3])

def p_primitive_float(p):
    'primitive : float'
    p[0] = FloatPrimitive(p[1])

def p_primitive_int(p):
    'primitive : int'
    p[0] = IntPrimitive(p[1])

def p_primitive_string(p):
    'primitive : string'
    p[0] = StringPrimitive(p[1])

def p_primitive_true(p):
    'primitive : true'
    p[0] = TruePrimitive()

def p_primitive_false(p):
    'primitive : false'
    p[0] = FalsePrimitive()

def p_primitive_null(p):
    'primitive : null'
    p[0] = NullPrimitive()

def p_empty(p):
    'empty :'

def p_error(p):
    print('Syntax error')
    exit(1)


parser = yacc.yacc()


def main():
    source = sys.stdin.read()
    tree = parser.parse(source)
    if tree is not None:
        pp(tree)


if __name__ == '__main__':
    main()
