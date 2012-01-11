import couchdb
import MySQLdb
from MySQLdb.constants import FIELD_TYPE
from  MySQLdb.converters import conversions as default_conv

from parse_schema import parse_schema

BATCH_SIZE = 1000
RESERVED_COLUMN_NAMES = ("_id", "_rev", "type")

FIELD_CONVERSIONS = MySQLdb.converters.conversions.copy()
FIELD_CONVERSIONS.update({
        FIELD_TYPE.BIT: lambda s: s == '\x01',
        FIELD_TYPE.DATE: lambda s: default_conv[FIELD_TYPE.DATE](s).isoformat(),
        FIELD_TYPE.DATETIME: lambda s: default_conv[FIELD_TYPE.DATETIME](s).isoformat(),
        FIELD_TYPE.TIMESTAMP: lambda s: default_conv[FIELD_TYPE.TIMESTAMP](s).isoformat(),
        FIELD_TYPE.DECIMAL: lambda s: s,
        FIELD_TYPE.NEWDECIMAL: lambda s: s,
})

def convert(mysql, couch, schema):
    cursor = mysql.cursor(MySQLdb.cursors.DictCursor)

    for table in schema.tables.values():
        load_table(cursor, table, couch)

def load_table(cursor, table, couch):
    print "loading table: %s" % table.name
    cursor.execute("SELECT * FROM %s" % table.name)

    n_processed = 0
    while True:
        rows = cursor.fetchmany(BATCH_SIZE)
        if len(rows) < 1: break
        docs = [row2doc(row, table) for row in rows]
        couch.update(docs)
        n_processed += len(docs)

def row2doc(row, table):
    doc = couchdb.Document()
    doc['type'] = table.name

    for col in table.columns.values():
        load_value(doc, col, row)

    return doc

def load_value(doc, col, row):
    if col.name in RESERVED_COLUMN_NAMES: raise ValueError()
    value = row[col.name]
    if value is not None:
        doc[col.name] = value

if __name__ == "__main__":
    import getopt
    import sys

    optlist, args = getopt.getopt(sys.argv[1:], 'u:p:')
    options  = dict(optlist)
    username = options["-u"]
    password = options["-p"]
    mysqldbname = args[0]
    couchdbname = args[1]
    schemafile = args[2]

    schema = parse_schema(open(schemafile))

    mysql = MySQLdb.connect(user=username, passwd=password,
                            db=mysqldbname, charset = "utf8",
                            use_unicode = True, conv=FIELD_CONVERSIONS)

    couch = couchdb.Server()[couchdbname]

    convert(mysql, couch, schema)
