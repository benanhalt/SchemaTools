import re
from schema import *

create_table_re = re.compile(r"CREATE TABLE `(?P<table_name>\w*)`")
end_create_table_re = re.compile(r".*;$")
column_re = re.compile(r"\s*`(?P<name>\w+)`\s(?P<type>[^\s]+)\s(?P<options>[^\,]*)\,")
primary_key_re = re.compile(r"\s*PRIMARY KEY\s+\(`(?P<name>[^`]+)`\)")
foreign_key_re =re.compile(r"\s*CONSTRAINT\s+`(?P<name>\w+)`\s+FOREIGN KEY\s+" +
                           r"\(`(?P<localcol>[^`]+)`\)\s+REFERENCES\s+" +
                           r"`(?P<table>[^`]+)`\s+" +
                           r"\(`(?P<remotecol>[^`]+)`\)")

def parse_schema(lines_in):
    schema = Schema()
    while True:
        line = lines_in.readline()
        if line == "": return schema

        match = create_table_re.match(line)
        if match is not None:
            table_name = match.group('table_name')
            schema.tables[table_name] = parse_create_table(table_name, lines_in)

def parse_create_table(table_name, lines_in):
    table = Table(table_name)
    while True:
        line = lines_in.readline()
        if line == "": raise EOFError()
        if end_create_table_re.match(line): return table

        match = column_re.match(line)
        if match is not None:
            col_name = match.group('name')
            table.columns[col_name] = Column(
                col_name,
                match.group('type'),
                match.group('options')
                )
            continue

        match = primary_key_re.match(line)
        if match is not None:
            table.primary_key = match.group('name')
            continue

        match = foreign_key_re.match(line)
        if match is not None:
            localcol = match.group('localcol')
            table.relationships[localcol] = Relationship(
                match.group('name'),
                localcol,
                match.group('table'),
                match.group('remotecol')
                )

if __name__ == '__main__':
    import sys
    import json
    from jsonschema import SchemaEncoder
    print json.dumps(parse_schema(sys.stdin), cls=SchemaEncoder, indent=4)
