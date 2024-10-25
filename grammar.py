import sys

import ply.yacc as yacc

import lang
from tokens import tokens  # import required by ply


def p_stmt(p):
    'stmt : record_def'
    p[0] = p[1]

def p_record_def(p):
    'record_def : record name open_brace field_list close_brace'
    p[0] = lang.Record(
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
    'field : name modifier unique_opt type'
    p[0] = lang.Field(
        name=p[1],
        type=p[4],
        is_key=(p[2] == lang.Modifier.KEY_MEMBER),
        is_nullable=(p[2] == lang.Modifier.NULLABLE),
        is_unique=p[3]
    )

def p_modifier_key_member(p):
    'modifier : exclam'
    p[0] = lang.Modifier.KEY_MEMBER

def p_modifier_nullable(p):
    'modifier : quest'
    p[0] = lang.Modifier.NULLABLE

def p_modifier_none(p):
    'modifier : empty'
    p[0] = None

def p_unique_true(p):
    'unique_opt : unique'
    p[0] = True

def p_unique_false(p):
    'unique_opt : empty'
    p[0] = False

def p_type_name(p):
    'type : name'
    p[0] = p[1]

def p_empty(p):
    'empty :'

def p_error(p):
    print('Syntax error')


def main():
    source = sys.stdin.read()
    parser = yacc.yacc()
    print(parser.parse(source))


if __name__ == '__main__':
    main()
