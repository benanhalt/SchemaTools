import sqlalchemy.schema
from sqlalchemy.dialects.postgresql import UUID as UUIDType
from .orderedclass import Ordered

class Field:
    sqlalchemy_type = sqlalchemy.Text

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def to_sqlalchemy(self, name, *args, **kwargs):
        return sqlalchemy.Column(
            name, self.sqlalchemy_type, *args,
            nullable=(field_options.required not in self.args),
            **kwargs)

    def __repr__(self):
        args = list(self.args)
        args.extend("%s=%s" % (k, v) for k, v in self.kwargs.items())

        return "%s(%s)" % (
            self.__class__.__name__,
            ', '.join(args)
            )

class Link(Field):
    sqlalchemy_type = None

    def to_sqlalchemy(self, *args, **kwargs):
        fk = '.'.join((get_schema(self.target), self.target.get_name(), 'uuid'))
        return super().to_sqlalchemy(
            *(args +  (sqlalchemy.ForeignKey(fk), )),
            **kwargs)

    def __init__(self, target, *args, **kwargs):
        self.target = target
        super().__init__(*args, **kwargs)

def is_field(obj):
    return isinstance(obj, Field)

def is_record(obj):
    return isinstance(obj, type) and issubclass(obj, Record) \
           and obj not in (Record, TreeRecord)

def get_schema(record):
    return record.__module__

class Record(Ordered):
    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    def base_columns(cls):
        return [
            sqlalchemy.Column('uuid', UUIDType, primary_key=True)
            ]

    @classmethod
    def to_sqlalchemy(cls, metadata, parent=None):
        fields = [field for field in cls._fields
                  if is_field(getattr(cls, field))]

        children = [field for field in cls._fields
                    if is_record(getattr(cls, field))]

        args = [cls.get_name(), metadata]
        args.extend(getattr(cls, field).to_sqlalchemy(field)
                    for field in fields)
        args.extend(cls.base_columns())
        yield sqlalchemy.Table(*args, schema=get_schema(cls))
        yield from (getattr(cls, child).to_sqlalchemy(metadata, cls)
                    for child in children)

class TreeRecord(Record):
    pass

def Tree(ranks_for_tree):
    class TreeClass(TreeRecord):
        try:
            _ranks = ranks_for_tree.split()
        except AttributeError:
            _ranks = ranks_for_tree
    return TreeClass

def schema_to_sqlalchemy(metadata, schema_module):
    for attr in schema_module.__dict__.values():
        if is_record(attr):
            yield from attr.to_sqlalchemy(metadata)

def create_schema(engine, metadata, schema_module):
    engine.execute(
        sqlalchemy.schema.DropSchema(schema_module.__name__,
                                     cascade=True))
    engine.execute(
        sqlalchemy.schema.CreateSchema(schema_module.__name__))

    for table in schema_to_sqlalchemy(metadata, schema_module):
        pass
    metadata.create_all(engine)
