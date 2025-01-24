import sys

from nodes import *
from grammar import parser


_types = {
    'Integer': 'integer',
    'String': 'text'
}


def generate_sql(node):
    return record_def(node)


def record_def(node):
    key_fields = [field for field in node.field_list if field.is_key]
    if len(key_fields) > 0:
        key = '\n    primary key (' + ', '.join([field.name for field in key_fields]) + ')'
    else:
        key = ''
    return 'create table ' + node.name.lower() + ' (\n    ' + '\n    '.join([field_def(field) for field in node.field_list]) + key + '\n);'

def field_def(node):
    constraints = []
    if isinstance(node.domain, DomainRef):
        field_type = _types.get(node.domain.name)
        if field_type is None:
            field_type = 'integer'
            constraints.append('references ' + node.domain.name.lower())  # here we should actually look up the referenced table's definition
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
    return node.name + ' ' + field_type + ' ' + ' '.join(constraints) + ', '


def main():
    source = sys.stdin.read()
    tree = parser.parse(source)
    if tree is not None:
        print(generate_sql(tree))


if __name__ == '__main__':
    main()
