from parse_schema import parse_schema

def schema2dot(schema):
    dot = ["digraph Schema {"]
    for table in schema.tables.values():
        edges = ["\t%s -> %s;" % (table.name, r.table)
                 for r in table.relationships.values()]
        dot.extend(edges)
    dot.append("}")
    return "\n".join(dot)

if __name__ == '__main__':
    import sys
    schema = parse_schema(sys.stdin)
    print schema2dot(schema)
