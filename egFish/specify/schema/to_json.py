from collections import OrderedDict
import json
import inspect

from . import base, fields
from .generics import generic, method, call_next_method

def to_json(schema_family):
    return json.dumps(to_data(schema_family), indent=4, separators=(',', ': '))

@generic
def to_data(obj, *args, **kwargs):
    pass

@method(to_data)
def schema_family_to_data(family: base.SchemaFamily):
    data = OrderedDict()
    data['title'] = family.name
    data['$schema'] = "http://json-schema.org/draft-04/schema#"
    for schema in family.schemas.values():
        data[schema.__name__] = to_data(schema)
    return data


@method(to_data)
def schema_to_data(schema: base.SchemaMeta):
    data = OrderedDict()
    data['title'] = schema.__name__
    data['description'] = inspect.getdoc(schema)
    for record in schema._meta.records.values():
        data[record.__name__] = to_data(record)
    return data

@method(to_data)
def record_to_data(record: base.RecordMeta):
    data = OrderedDict()
    data['title'] = record.__name__
    data['type'] = "object"
    data['properties'] = OrderedDict( (field.__name__, to_data(field))
                                      for field in record._meta.fields.values() )

    links = [ to_link_description(link)
              for link in record._meta.fields.values()
              if isinstance(link, fields.Link) ]

    if len(links) > 0:
        data['links'] = links

    for child in record._meta.children.values():
        prop_name = getattr(child, 'collective_name', child.__name__)
        data['properties'][prop_name] = OrderedDict((
            ('type', 'array'), ('items', to_data(child))))

    return data

@method(to_data)
def tree_record_to_data(tree: base.TreeMeta):
    data = call_next_method(tree)
    tree_structure = OrderedDict(((rank, {'type': 'string'})
                                  for rank in tree._ranks))
    data['properties']['tree_structure'] = OrderedDict((
        ('type', 'object'), ('properties', tree_structure)))

    return data

@method(to_data)
def field_to_data(field: base.Field):
    return OrderedDict()

@method(to_data)
def text_field_to_data(field: fields.Text):
    data = call_next_method(field)
    data["type"] = "string"
    return data

@method(to_data)
def date_field_to_data(field: fields.Date):
    data = call_next_method(field)
    data["type"] = "string"
    data['format'] = "date-time"
    return data

@method(to_data)
def integer_field_to_data(field: fields.Integer):
    data = call_next_method(field)
    data["type"] = "integer"
    return data

@method(to_data)
def boolean_field_to_data(field: fields.Boolean):
    data = call_next_method(field)
    data["type"] = "boolean"
    return data

@method(to_data)
def link_to_data(link: fields.Link):
    data = call_next_method(link)
    data["type"] = "string"
    data["format"] = "uuid"
    return data

def to_link_description(link):
    target_schema = "#/%s/%s" % (link.target._meta.schema.__name__,
                                 link.target.__name__)

    href = "/%s/%s/{%s}/" % (link.target._meta.schema.__name__,
                             link.target.__name__,
                             link.__name__)
    return OrderedDict((
        ('rel', link.__name__),
        ('href', href),
        ('targetSchema', target_schema)))
