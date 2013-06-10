import sys
from collections import OrderedDict

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

class RecordMeta(OrderedMeta):
    def __new__(meta, name, bases, clsdict):
        record = super().__new__(meta, name, bases, clsdict)
        values = [getattr(record, key) for key in record._keys]
        record.children = OrderedDict((r.__name__, r) for r in values if is_record(r))
        for child in record.children.values():
            child.parent = record

        record.fields = OrderedDict()
        for name, field in ((k, v)
                            for k, v in zip(record._keys, values)
                            if is_field(v)):
            field.record = record
            field.__name__ = name
            record.fields[name] = field
        return record

    @property
    def schema(record):
        if hasattr(record, 'parent'):
            return record.parent.schema
        else:
            return record._schema

    @property
    def name(record):
        return record.__name__

    @property
    def full_name(record):
        return record.schema.name + '.' + record.name

    def all_descendants(record):
        for child in record.children.values():
            yield child
            yield from child.all_descendants()

class Record(metaclass=RecordMeta):
    pass

class SchemaMeta(OrderedMeta):
    def __new__(meta, name, bases, clsdict):
        schema = super().__new__(meta, name, bases, clsdict)
        values = [getattr(schema, key) for key in schema._keys]
        schema.records = OrderedDict((r.__name__, r) for r in values if is_record(r))
        for record in schema.records.values():
            record._schema = schema
        return schema

    @property
    def name(schema):
        return schema.__name__

    def all_records(schema):
        for record in schema.records.values():
            yield record
            yield from record.all_descendants()

class SchemaFamily:
    def __init__(self):
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

    def all_records(self):
        for schema in self.schemas.values():
            yield from schema.all_records()

class TreeMeta(RecordMeta):
    pass

def make_tree(ranks_for_tree):
    class Tree(metaclass=TreeMeta):
        try:
            _ranks = ranks_for_tree.split()
        except AttributeError:
            _ranks = ranks_for_tree
    return Tree

