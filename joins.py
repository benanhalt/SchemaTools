from parse_schema import parse_schema

def compute_view(schema):
    for t in schema.tables.values():
        t.lh_emits = set()
        t.rh_emits = set()

    for t in schema.tables.values():
        for r in t.relationships.values():
            key = "%s.%s" % (r.table, r.remote_column)
            t.lh_emits.add((r.local_column, key))
            schema.tables[r.table].rh_emits.add(r.remote_column)

    view = ["function(doc) {"]
    for t in schema.tables.values():
        if len(t.lh_emits) + len(t.rh_emits) < 1:
            continue

        view.append('  if(doc.type == "%s") {' % t.name)
        for e in t.lh_emits:
            col, key = e
            field = 'doc["%s"]' % col
            view.append('    %s && emit(["%s" + %s, 1], null);' % \
                            (field, key, field))

        for col in t.rh_emits:
            key = "%s.%s" % (t.name, col)
            field = 'doc["%s"]' % col
            view.append('    %s && emit(["%s" + %s, 0], null);' % \
                            (field, key, field))

        view.append('    return;')
        view.append('  }')
    view.append('}')
    return "\n".join(view)

if __name__ == '__main__':
    import sys
    import json
    schema = parse_schema(sys.stdin)
    view = compute_view(schema)
    print json.dumps({"language":"javascript",
                      "views":
                          {"joins":
                               {"map": view,
                                "reduce": "_count"}
                           }
                      })
