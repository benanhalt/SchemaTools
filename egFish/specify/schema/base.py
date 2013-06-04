import sys

from .orderedclass import OrderedMeta
from .generics import WithGenerics

def is_field(obj):
    return isinstance(obj, Field)

def is_record(obj):
    return isinstance(obj, RecordMeta)

def is_tree(obj):
    return isinstance(obj, TreeMeta)

def is_schema(obj):
    return isinstance(obj, SchemaMeta)

class Field(WithGenerics):
    _record = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def get_name(self):
        return self._name

class RecordMeta(WithGenerics, OrderedMeta):
    def __new__(meta, name, bases, clsdict):
        record = super().__new__(meta, name, bases, clsdict)
        values = [getattr(record, key) for key in record._keys]
        record._children = [v for v in values if is_record(v)]
        for child in record._children:
            child._parent = record

        record._fields = []
        for name, field in ((k, v)
                            for k, v in zip(record._keys, values)
                            if is_field(v)):
            field._record = record
            field._name = name
            record._fields.append(field)
        return record

    def get_schema(cls):
        if hasattr(cls, '_parent'):
            return cls._parent.get_schema()
        else:
            return cls._schema.get_name()

    def get_name(cls):
        return cls.__name__


class Record(metaclass=RecordMeta):
    pass

class SchemaMeta(WithGenerics, OrderedMeta):
    def __new__(meta, name, bases, clsdict):
        schema = super().__new__(meta, name, bases, clsdict)
        values = [getattr(schema, key) for key in schema._keys]
        schema._records = [v for v in values if is_record(v)]
        for record in schema._records:
            record._schema = schema

        if hasattr(schema, '_schema_list'):
            schema._schema_list.append(schema)
        return schema

    def get_name(cls):
        return cls.__name__

def make_schema():
    schema_list = []
    class Schema(metaclass=SchemaMeta):
        _schema_list = schema_list

    schema_list.remove(Schema)
    return Schema

class TreeMeta(RecordMeta):
    pass

def make_tree(ranks_for_tree):
    class Tree(metaclass=TreeMeta):
        try:
            _ranks = ranks_for_tree.split()
        except AttributeError:
            _ranks = ranks_for_tree
    return Tree

