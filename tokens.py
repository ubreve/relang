import sys

import ply.lex as lex


embrace = [
    f'{side}_{type}'
        for side in ['open', 'close']
        for type in ['paren', 'brack', 'brace']
]

operators = [
    'colon', 'comma', 'dot', 'ellipsis', 'equal', 'exclam', 'greater',
    'greater_equal', 'less', 'less_equal', 'minus', 'not_equal', 'plus',
    'quest', 'semicolon', 'slash', 'star', 'two_dots', 'two_equal'
]

composites = ['is_not', 'not_in']

keywords = [
    'and', 'check', 'false', 'is', 'not', 'null', 'or', 'record', 'true',
    'unique'
]

# name "literals" is reserved by ply.lex to single-character token definition
primitives = ['int', 'string', 'float']

tokens = ['name', 'comment'] + embrace + operators + composites + keywords + primitives


def t_is_not(token):
    r'is\snot'
    return token

def t_not_in(token):
    r'not\sin'
    return token

def t_name(token):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    if token.value in keywords:
        token.type = token.value
    return token

def t_int(token):
    r'\d+'
    token.value = int(token.value)
    return token

def t_string(token):
    r'".*?"'
    token.value = token.value[1:-1]  # trim quotes
    return token

def t_newline(token):
    r'\n+'
    token.lexer.lineno += len(token.value)

def t_error(token):
    print(f"Illegal token {token.value}")
    token.lexer.skip(1)


t_open_paren  = r'\('
t_open_brack  = r'\['
t_open_brace  = r'\{'
t_close_paren = r'\)'
t_close_brack = r'\]'
t_close_brace = r'\}'

t_colon         = r':'
t_comma         = r','
t_dot           = r'\.'
t_ellipsis      = r'\.{3}'
t_equal         = r'='
t_exclam        = r'!'
t_greater       = r'>'
t_greater_equal = r'>='
t_less          = r'<'
t_less_equal    = r'<='
t_minus         = r'-'
t_not_equal     = r'!='
t_plus          = r'\+'
t_quest         = r'\?'
t_semicolon     = r';'
t_slash         = r'/'
t_star          = r'\*'
t_two_dots      = r'\.{2}'
t_two_equal     = r'=='

t_ignore = ' \t'
t_ignore_comment = r'\#.*'


def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


def main():
    source = sys.stdin.read()
    lexer = lex.lex()
    lexer.input(source)
    for token in lexer:
        print(token)


if __name__ == '__main__':
    main()