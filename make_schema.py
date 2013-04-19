from collections import namedtuple, OrderedDict
from xml.etree import ElementTree
from json import dumps


FIELD_TYPE_MAP = {
    'text': lambda field: {'type': 'string'},
    'java.lang.String': lambda field: {'type': 'string', 'maxLength': field.attrib['length']},
    'java.lang.Integer': lambda field: {'type': 'integer'},
    'java.lang.Long': lambda field: {'type': 'integer'},
    'java.lang.Byte': lambda field: {'type': 'integer'},
    'java.lang.Short': lambda field: {'type': 'integer'},
    'java.util.Calendar': lambda field: {'type': 'string', 'format': 'date-time'},
    'java.util.Date': lambda field: {'type': 'string', 'format': 'date-time'},
    'java.lang.Float': lambda field: {'type': 'number'},
    'java.lang.Double': lambda field: {'type': 'number'},
    'java.sql.Timestamp': lambda field: {'type': 'string', 'format': 'date-time'},
    'java.math.BigDecimal': lambda field: {'type': 'number'},
    'java.lang.Boolean': lambda field: {'type': 'boolean'}
    }

def make_property(field):
    return FIELD_TYPE_MAP.get(field.attrib['type'], lambda f: {})(field)

table_schema = namedtuple('TableSchema', 'title type required properties')

def make_schema_for_table(table):
    id_field = table.find('id').attrib['name']

    properties = OrderedDict([(id_field, {'type': 'integer'})])
    properties.update((field.attrib['name'], make_property(field))
                      for field in table.findall('field'))

    required = [field.attrib['name']
                for field in table.findall('field')
                if field.attrib['required'] == 'true']

    return table_schema(
        title=table.attrib['classname'].split('.')[-1],
        type='object',
        required=required,
        properties=properties)._asdict()


def make_jsonschema(xml):
    return [make_schema_for_table(table)
            for table in xml.findall('table')]

if __name__ == '__main__':
    import sys
    xml = ElementTree.parse(sys.argv[1])
    print(dumps(make_jsonschema(xml), indent=4))
