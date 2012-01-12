import json
from schema import Schema, Table, Column, Relationship

class SchemaEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Schema):
            return obj.tables

        if isinstance(obj, Table):
            return {"columns": obj.columns,
                    "relationships": obj.relationships,
                    "primary_key": obj.primary_key,
                    "include": obj.include}

        if isinstance(obj, Column):
            return {"mysql_type": obj.mysql_type,
                    "options": obj.options}

        if isinstance(obj, Relationship):
            return {"name": obj.name,
                    "remote_table": obj.table,
                    "remote_column": obj.remote_column,
                    "action": obj.action}

        return json.JSONEncoder.default(self, obj)

def json2schema(data):
    schema = Schema()
    for name, t in data.items():
        table = schema.tables[name] = Table(name)
        table.include = t["include"]
        table.primary_key = t["primary_key"]

        for c, r in t["relationships"].items():
            relationship = table.relationships[c] = \
                Relationship(r["name"], c,
                             r["remote_table"],
                             r["remote_column"])

            relationship.action = r["action"]

        for name, c in t["columns"].items():
            column = table.columns[name] = \
                Column(name, c["mysql_type"], c["options"])
    return schema
