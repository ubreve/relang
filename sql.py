import sys

from nodes import *
from grammar import parser

_types = {
    'Integer': 'integer',
    'String' : 'text'
}

class Evaluator:
    def __init__(self, ast):
        self.node = ast

    def evaluate(self) -> str:
        pass

class EvaluatorFactory:
    @staticmethod
    def get(ast):
        if isinstance(ast, RecordDef):
            return DefEvaluator(ast)
        elif isinstance(ast, RecordCreate):
            raise ValueError('unexpected ast type')
        else:
            raise ValueError('unexpected ast type')

class DefEvaluator(Evaluator):
    '''Record definition evaluator aka create DDL statement generator'''

    def evaluate(self):
        sql = 'create table ' + self.node.name + ' ('
        sql += self._field_list(self.node.field_list) + ');'
        return sql

    def _field_list(self, node):
        if node:
            fields = [self._field_def(field) for field in node]
            return '\n\t' + ',\n\t'.join(fields) + '\n'
        else:
            return ''

    # TODO: check for multiple PKs or implement composite PK
    def _field_def(self, node):
        constraints = []
        if isinstance(node.domain, DomainRef):
            field_type = _types.get(node.domain.name)
            if field_type is None:
                field_type = 'integer'
                # here we should look up the referenced table's definition
                constraints.append('references ' + node.domain.name.lower())
        elif isinstance(node.domain, RangeDef):
            assert node.domain.second is None
            field_type = 'integer'
            constraints.append(f'check ({node.name} between {node.domain.first} and {node.domain.last})')
        else:
            raise ValueError('unimplemented field domain')
        if node.is_unique:
            constraints.append('unique')
        if not node.is_nullable:
            constraints.append('not null');
        if node.is_key:
            constraints.append('primary key');
        return node.name + ' ' + field_type + ' ' + ' '.join(constraints)


def main():
    source = sys.stdin.read()
    tree = parser.parse(source)
    if tree is not None:
        evaluator = EvaluatorFactory.get(tree)
        print(evaluator.evaluate())


if __name__ == '__main__':
    main()
