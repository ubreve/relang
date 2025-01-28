relang
======

![Python](https://img.shields.io/badge/Python-ply-blue?logo=python)
![relang](https://img.shields.io/badge/relang-red)

**relang** is an experimental relational database population language made as a
university assignment. relang statements are translated to the PostgreSQL
dialect of SQL. The name relang originates with relational+language.

Features
--------

relang attempts to rethink the most common interactions with relational
databases and introduce more intuitive syntax as compared to the SQL.

- Record definition aka DDL create
  - Create fields of basic types
  relang types are mapped to the types supported by PostgreSQL.
  - Create fields of record types: foreign key
  Instead of constraints, relang provides references.
  - Define fields modifiers: primary key, not null, and nullable
  By default, all fields are `not null` unless specified otherwise.
  - Define the ranges of the values: check
  In relang, ranges are defined as `[first,second..last]`
- Record creation aka DML insert
  - Instantiate with parameter lists: values()
  - Specify field names
  - Instantiate multiple records in one statement: deferring contraints
- Compilation into PostgreSQL SQL dialect

Installation
------------

The only requirement is local installation of python3.

It is recommended to install the dependencies inside a virtual environment:
```bash
python3 -m venv .venv
```
```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

Usage
-----

To run the compiler, you need to provided the relang statements to the standard
input of the `sql.py` file, which is the backend for evaluation into SQL.

```bash
cat my_record_creation.rln | python sql.py
```

```bash
python sql.py
record myrecord{}
^D
```

The output can be redirected right to the database client.
```bash
cat my_record_creation.rln | python sql.py | psql -U username -d database_name
```

Examples
--------

relang record definition:
```java
record Processor {
  id! Integer;
  manufacturer Manufacturer;
  cores [1..16];
  frequency Float;
  hasBoost Boolean;
  boost? Float;
}
```

Generated SQL table creation:
```sql
create table Processor (
	id integer not null,
	manufacturer integer references manufacturer not null,
	cores integer check (cores between 1 and 16) not null,
	frequency real not null,
	hasBoost boolean not null,
	boost real,
	primary key (id)
);
```

relang record creation:
```java
create CyclicEdge(from=1, to=2), CyclicEdge(2, 1);
```

Generated SQL insertion:
```sql
begin;
set constraints all deferred;
insert into CyclicEdge (from, to)
	values ('1', '2');
insert into CyclicEdge ('2', '1');
commit;
```
