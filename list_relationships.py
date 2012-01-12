from jsonschema import json2schema

def list_relationships(schema):
    out = []
    for table in schema.tables.values():
        if not table.include: continue
        rels = ["n %s.%s -> %s.%s" % \
                    (table.name, r.local_column,
                     r.table, r.remote_column)
                for r in table.relationships.values()
                if schema.tables[r.table].include]
        out.extend(rels)
    return "\n".join(out)

if __name__ == '__main__':
    import sys
    import json
    schema = json2schema(json.load(sys.stdin))
    print list_relationships(schema)
