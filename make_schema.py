from collections import namedtuple, OrderedDict
from xml.etree import ElementTree
from json import dumps


FIELD_TYPE_MAP = {
    'text': lambda field: {'type': 'string'},
    'java.lang.String': lambda field: {'type': 'string', 'maxLength': int(field.attrib['length'])},
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

def make_link(rel, id_field):
    related_table = rel.attrib['classname'].split('.')[-1]
    link = OrderedDict(rel=rel.attrib['relationshipname'])
    if 'columnname' in rel.attrib:
        link['href'] = '%s/{%s}/' % (related_table, rel.attrib['columnname'])
    else:
        link['href'] = '%s/?%s={%s}' % (related_table,
                                        rel.attrib['othersidename'],
                                        id_field)
    return link

table_schema = namedtuple('TableSchema', 'title type required properties links')

def make_schema_for_table(table):
    tablename = table.attrib['classname'].split('.')[-1]
    id_field = table.find('id').attrib['name']

    properties = OrderedDict([(id_field, {'type': 'integer'})])
    properties.update((field.attrib['name'], make_property(field))
                      for field in table.findall('field'))
    properties.update((rel.attrib['columnname'], {'type': 'integer'})
                      for rel in table.findall('relationship')
                      if 'columnname' in rel.attrib)

    required = [field.attrib['name']
                for field in table.findall('field')
                if field.attrib['required'] == 'true']
    required.extend(rel.attrib['columnname']
                    for rel in table.findall('relationship')
                    if 'columnname' in rel.attrib and
                    rel.attrib['required'] == 'true')

    links = [{'rel': 'self', 'href': '%s/{%s}/' % (tablename, id_field)},
             {'rel': 'instances', 'href': '%s/' % (tablename, )}]
    links.extend(make_link(rel, id_field) for rel in table.findall('relationship'))

    return table_schema(
        title=tablename,
        type='object',
        required=required,
        properties=properties,
        links=links
        )._asdict()


def make_jsonschema(xml):
    schema = OrderedDict()
    schema['$schema'] = "http://json-schema.org/draft-04/hyper-schema#"
    schema['type'] = 'array'
    schema['items'] = OrderedDict(type='object')
    schema['items']['oneOf']=[
        make_schema_for_table(table)
        for table in xml.findall('table')]

    return schema

def schema_from_xml(filename):
    xml = ElementTree.parse(filename)
    return make_jsonschema(xml)

if __name__ == '__main__':
    import sys
    print(dumps(schema_from_xml(sys.argv[1]), indent=2))

