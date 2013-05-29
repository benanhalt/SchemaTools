from .orderedclass import OrderedMeta
from . import to_sqlalchemy as sql_mixin

def is_field(obj):
    return isinstance(obj, Field)

def is_record(obj):
    return isinstance(obj, type) and issubclass(obj, Record)


class Field(sql_mixin.Field):
    _record = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def get_name(self):
        return self._name

class Link(sql_mixin.Link, Field):
    def __init__(self, target, *args, **kwargs):
        self.target = target
        super().__init__(*args, **kwargs)

class RecordMeta(OrderedMeta):
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

class Record(sql_mixin.Record, metaclass=RecordMeta):
    _parent = None

    @classmethod
    def get_schema(cls):
        if cls._parent is None:
            return cls._schema.get_name()
        else:
            return cls._parent.get_schema()

    @classmethod
    def get_name(cls):
        return cls.__name__

class SchemaMeta(type):
    def __new__(meta, name, bases, clsdict):
        schema = type.__new__(meta, name, bases, clsdict)
        schema._records = [v for v in clsdict.values() if is_record(v)]
        for record in schema._records:
            record._schema = schema
        return schema

class Schema(sql_mixin.Schema, metaclass=SchemaMeta):
    @classmethod
    def get_name(cls):
        return cls.__name__

def make_tree(ranks_for_tree):
    class TreeClass(Record):
        try:
            _ranks = ranks_for_tree.split()
        except AttributeError:
            _ranks = ranks_for_tree
    return TreeClass
