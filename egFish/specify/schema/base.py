import sys
from collections import OrderedDict, namedtuple

from .orderedclass import OrderedMeta

def is_field(obj):
    return isinstance(obj, Field)

def is_record(obj):
    return isinstance(obj, RecordMeta)

def is_tree(obj):
    return isinstance(obj, TreeMeta)

def is_schema(obj):
    return isinstance(obj, SchemaMeta)

class Field:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @property
    def name(self):
        return self.__name__

    def __str__(self):
        return self.__class__.__name__ + ': ' + self.record.__qualname__ + '.' + self.__name__

class RecordMetaData:
    def __init__(self, **kwargs):
        for arg in "schema name parent fields children".split():
            setattr(self, arg, kwargs.get(arg))

    @property
    def full_name(self):
        return self.schema._meta.name + '.' + self.name

    def set_schema(self, schema):
        self.schema = schema
        for child in self.children.values():
            child._meta.set_schema(schema)

    def __repr__(self):
        return self.__class__.__name__ + '(%s)' % ', '.join(
            "%s=%r" % (arg, getattr(self, arg))
            for arg in "schema name parent fields children".split())


class RecordMeta(OrderedMeta):
    def __new__(meta, name, bases, clsdict):
        record = super().__new__(meta, name, bases, clsdict)
        values = [getattr(record, key) for key in record._keys]

        children = OrderedDict((r.__name__, r) for r in values if is_record(r))

        for child in children.values():
            child._meta.parent = record

        fields = OrderedDict()
        for name, field in ((k, v)
                            for k, v in zip(record._keys, values)
                            if is_field(v)):
            field.record = record
            field.__name__ = name
            fields[name] = field

        record._meta = RecordMetaData(schema=None, parent=None, # will be set by parent objects
                                      name=record.__name__,
                                      fields=fields,
                                      children=children)
        return record

class Record(metaclass=RecordMeta):
    pass

class SchemaMetaData(namedtuple("SchemaMetaData", "name records")):
    pass

class SchemaMeta(OrderedMeta):
    def __new__(meta, name, bases, clsdict):
        schema = super().__new__(meta, name, bases, clsdict)
        values = [getattr(schema, key) for key in schema._keys]

        records = OrderedDict((r.__name__, r) for r in values if is_record(r))
        for record in records.values():
            record._meta.set_schema(schema)

        schema._meta = SchemaMetaData(name=name, records=records)
        return schema

class SchemaFamily:
    def __init__(self, name):
        self.name = name
        self.schemas = OrderedDict()

        class Meta(SchemaMeta):
            def __new__(meta, name, bases, clsdict):
                schema = super().__new__(meta, name, bases, clsdict)
                self.schemas[schema.__name__] = schema
                return schema

        class Schema(metaclass=Meta):
            schema_family = self

        self.schemas.pop('Schema')
        self.Schema = Schema


class TreeMeta(RecordMeta):
    pass

def make_tree(ranks_for_tree):
    class Tree(metaclass=TreeMeta):
        try:
            _ranks = ranks_for_tree.split()
        except AttributeError:
            _ranks = ranks_for_tree
    return Tree

def many(name):
    def decorator(record):
        record.collective_name = name
        return record
    return decorator
