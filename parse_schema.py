import re

create_table_re = re.compile(r"CREATE TABLE `(?P<table_name>\w*)`")
end_create_table_re = re.compile(r".*;$")
column_re = re.compile(r"\s*`(?P<name>\w+)`\s(?P<type>[^\s]+)\s(?P<options>[^\,]*)\,")
primary_key_re = re.compile(r"\s*PRIMARY KEY\s+\(`(?P<name>[^`]+)`\)")
foreign_key_re =re.compile(r"\s*CONSTRAINT\s+`(?P<name>\w+)`\s+FOREIGN KEY\s+" +
                           r"\(`(?P<localcol>[^`]+)`\)\s+REFERENCES\s+" +
                           r"`(?P<table>[^`]+)`\s+" +
                           r"\(`(?P<remotecol>[^`]+)`\)")

class Schema:
    def __init__(self):
        self.tables = {}

    def __str__(self):
        tables = [str(t) for t in self.tables.values()]
        return "\n".join(tables)

class Table:
    def __init__(self, name):
        self.name = name
        self.primary_key = None
        self.columns = {}
        self.relationships = {}

    def __str__(self):
        body = ["  %s" % str(c) for c in self.columns.values()]

        if self.primary_key is not None:
            body.append("  PRIMARY KEY `%s`" % self.primary_key)

        body.extend(["  %s" % str(r) for r in self.relationships.values()])

        return "create table `%s` (\n%s\n);\n" % (self.name, ",\n".join(body))


class Column:
    def __init__(self, name, mysql_type, options):
        self.name = name
        self.mysql_type = mysql_type
        self.options = options

    def __str__(self):
        return "`%s` %s %s" % (self.name, self.mysql_type, self.options)

class Relationship:
    def __init__(self, name, local_column, table, remote_column):
        self.name = name
        self.local_column = local_column
        self.table = table
        self.remote_column = remote_column

    def __str__(self):
        return "CONSTRAINT `%s` FOREIGN KEY (`%s`) REFERENCES `%s` (`%s`)" % (
            self.name, self.local_column, self.table, self.remote_column)


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
    print str(parse_schema(sys.stdin))
