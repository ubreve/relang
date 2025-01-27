from abc import abstractmethod
from ast import keyword
import sys

from ply.yacc import rightmost_terminal

from nodes import *
from grammar import parser

_types = {
    'Integer': 'integer',
    'String' : 'text',
    'Boolean': 'boolean',
    'Float'  : 'real'
}

class Evaluator:
    def __init__(self, ast):
        self.node = ast

    @abstractmethod
    def evaluate(self) -> str:
        pass

class EvaluatorFactory:
    @staticmethod
    def get(ast):
        if isinstance(ast, RecordDef):
            return DefEvaluator(ast)
        elif isinstance(ast, CreateStmt):
            return CreateEvaluator(ast)
        else:
            raise ValueError(
                'unexpected ast type {type}'
                .format(type=type(ast).__qualname__)
            )

class DefEvaluator(Evaluator):
    '''Record definition evaluator aka create DDL statement generator'''

    def evaluate(self):
        sql = 'create table ' + self.node.name + ' ('
        sql += self._field_list(self.node.field_list)
        sql += self._constraints_list(self.node.field_list)+ '\n);'
        return sql

    def _field_list(self, node):
        if node:
            fields = [self._field_def(field) for field in node]
            return '\n\t' + ',\n\t'.join(fields)
        else:
            return ''

    def _field_def(self, field):
        constraints = []
        if isinstance(field.domain, DomainRef):
            field_type = _types.get(field.domain.name)
            if field_type is None:
                field_type = 'integer'
                # here we should look up the referenced table's definition
                constraints.append('references ' + field.domain.name.lower())
        elif isinstance(field.domain, RangeDef):
            assert field.domain.second is None
            field_type = 'integer'
            constraints.append(f'check ({field.name} between {field.domain.first} and {field.domain.last})')
        else:
            raise ValueError('unimplemented field domain')
        if field.is_unique:
            constraints.append('unique')
        if not field.is_nullable:
            constraints.append('not null');
        # if node.is_key:
        #     constraints.append('primary key');
        field = field.name + ' ' + field_type
        if constraints:
            field += ' ' + ' '.join(constraints)
        return field
    def _constraints_list(self, node):
        keys = [field.name for field in node if field.is_key]
        if keys:
            return ',\n\tprimary key (' + ', '.join(keys) + ')'
        else:
            return ''


class CreateEvaluator(Evaluator):
    '''Record creation evaluator aka insert DML statement generator'''

    def evaluate(self):
        if len(self.node.instance_list) > 1:
            return self._deferred(self.node.instance_list)
        else:
            return self._immediate(self.node.instance_list)

    def _deferred(self, instances):
        '''Transactional wrapper for the immediate'''
        transaction = 'begin;\nset constraints all deferred;\n'
        transaction += self._immediate(instances) + '\ncommit;'
        return transaction

    def _immediate(self, instances):
        return '\n'.join([self._insert(ins) for ins in instances])

    def _insert(self, instance):
        insert = 'insert into ' + instance.name + ' '
        params = instance.param_list
        if any(isinstance(param, KeywordParam) for param in params):
            if not all(isinstance(param, KeywordParam) for param in params):
                raise ValueError('Incohesive use of keyword parameters')
            else:
                keywords = [param.name for param in params]
                insert += '(' + ', '.join(keywords) + ')\n\tvalues '
                params = [param.value for param in params] # unpack to primitive
        values = [self._value(param) for param in params]
        insert += '(' + ', '.join(values) + ');'
        return insert

    def _value(self, param) -> str:
        if isinstance(param, Expr):
            return self._expression(param)
        elif isinstance(param, Call):
            return self._expression(param)
        else:
            return self._primitive(param)

    _binary_operators = {
        'Addition': '+',
        'Subtraction': '-',
        'Multiplication': '*',
        'Division': '/',
        'Conjunction': 'and',
        'Disjunction': 'or',
        'Less': '<',
        'LessEqual': '<=',
        'Greater': '>',
        'GreaterEqual': '>=',
        'Equal': '==',
        'NotEqual': '!='
    }

    _unary_operators = {
        'ArithmeticNegation': '-',
        'LogicalNegation': 'not '
    }

    def _expression(self, param) -> str:
        if type(param).__name__ in self._binary_operators:
            return '({left} {op} {right})'.format(
                left=self._value(param.left),
                right=self._value(param.right),
                op=self._binary_operators[type(param).__name__]
            )
        elif type(param).__name__ in self._unary_operators:
            # print(type(param).__name__)
            return '({op}{value})'.format(
                op=self._unary_operators[type(param).__name__],
                value=self._value(param.value)
            )
        elif isinstance(param, Call):
            if not isinstance(param.func, Ref):
                raise ValueError('higher-order function are not supported')
            return '{func_name}({arg_list})'.format(
                func_name=param.func.name,
                arg_list=', '.join(map(self._value, param.param_list))
            )
        else:
            raise ValueError(
                'unsupporter expression type: {type}'
                .format(type=type(param).__qualname__)
            )

    def _primitive(self, param) -> str:
        if isinstance(param, TruePrimitive):
            return 'true'
        elif isinstance(param, FalsePrimitive):
            return 'false'
        elif isinstance(param, NullPrimitive):
            return 'null'
        elif isinstance(param, IntPrimitive):
            return str(param.value)
        elif isinstance(param, FloatPrimitive):
            return str(param.value)
        else:
            return '\'' + str(param.value) + '\''


def main():
    source = sys.stdin.read()
    module = parser.parse(source)
    for stmt in module:
        evaluator = EvaluatorFactory.get(stmt)
        print(evaluator.evaluate())


if __name__ == '__main__':
    main()
