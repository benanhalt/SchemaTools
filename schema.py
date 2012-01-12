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
        self.include = True

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
        self.action = "nop"

    def __str__(self):
        return "CONSTRAINT `%s` FOREIGN KEY (`%s`) REFERENCES `%s` (`%s`)" % (
            self.name, self.local_column, self.table, self.remote_column)

