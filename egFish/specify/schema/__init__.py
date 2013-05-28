import sqlalchemy.schema
from sqlalchemy.dialects.postgresql import UUID as UUIDType
from .orderedclass import Ordered

class Field:
    sqlalchemy_type = sqlalchemy.Text

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def to_sqlalchemy(self, name):
        return sqlalchemy.Column(
            name, self.sqlalchemy_type,
            nullable=(field_options.required not in self.args))

class Link(Field):
    sqlalchemy_type = UUIDType

    def __init__(self, target, *args, **kwargs):
        fk = '.'.join((get_schema(target), target.get_name(), 'uuid'))
        self.args = args + (sqlalchemy.ForeignKey(fk), )
        self.kwargs = kwargs

def is_field(obj):
    return isinstance(obj, Field)

def is_entity(obj):
    return isinstance(obj, type) and issubclass(obj, Entity)

def get_schema(entity):
    return entity.__module__

class Entity(Ordered):
    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    def to_sqlalchemy(cls, metadata, parent=None):
        fields = [field for field in cls._fields
                  if is_field(getattr(cls, field))]

        children = [field for field in cls._fields
                    if is_entity(getattr(cls, field))]

        if len(fields) + len(children) < 1:
            return

        args = [cls.get_name(), metadata]
        args.extend(getattr(cls, field).to_sqlalchemy(field)
                    for field in fields)
        yield sqlalchemy.Table(*args, schema=get_schema(cls))
        yield from (getattr(cls, child).to_sqlalchemy(metadata, cls)
                    for child in children)

class TreeEntity(Entity):
    pass

def Tree(ranks_for_tree):
    class TreeClass(TreeEntity):
        try:
            _ranks = ranks_for_tree.split()
        except AttributeError:
            _ranks = ranks_for_tree
    return TreeClass

def schema_to_sqlalchemy(metadata, schema_module):
    for attr in schema_module.__dict__.values():
        if is_entity(attr):
            yield from attr.to_sqlalchemy(metadata)
