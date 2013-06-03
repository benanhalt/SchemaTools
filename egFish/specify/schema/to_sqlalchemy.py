import sqlalchemy
from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects import postgresql

class Schema:
    @classmethod
    def to_sqlalchemy(cls, metadata):
        return [result
                for record in cls._records
                for result in record.to_sqlalchemy(metadata)]

    @classmethod
    def create(cls, engine):
        try:
            engine.execute(
                DropSchema(cls.get_name(), cascade=True))
        except:
            pass

        engine.execute(
            CreateSchema(cls.get_name()))

class Record:
    @classmethod
    def base_columns(cls):
        cols = [ Column('uuid', sqlalchemy.Text, #postgresql.UUID,
                        primary_key=True) ]
        if cls._parent is not None:
            name = cls._parent.get_name()
            fk = '.'.join((cls._parent.get_schema(), name, 'uuid'))
            col = Column(name, None, ForeignKey(fk, onupdate="CASCADE"), nullable=False)
            cols.append(col)
        else:
            cols.extend([
                Column('version', sqlalchemy.Integer, nullable=False, default=0),
            ])
        return cols

    @classmethod
    def to_sqlalchemy(cls, metadata, parent=None):
        args = [cls.get_name(), metadata]
        args.extend(field.to_sqlalchemy() for field in cls._fields)
        args.extend(cls.base_columns())
        yield Table(*args, schema=cls.get_schema())
        for child in cls._children:
            yield from child.to_sqlalchemy(metadata, cls)

class TreeRecord:
    @classmethod
    def base_columns(cls):
        cols = super().base_columns()
        cols.append( Column('path', postgresql.ARRAY(sqlalchemy.Text), nullable=False) )
        return cols

def process_schema_module(metadata, schema_module):
    from .base import is_schema

    schemas = [v for v in schema_module.__dict__.values()
               if is_schema(v)]

    for schema in schemas:
        schema.to_sqlalchemy(metadata)

    return schemas

def create_schemas(engine, metadata, schemas):
    for schema in schemas:
        schema.create(engine)

    metadata.create_all(engine)

class Field:
    def to_sqlalchemy(self, *args, **kwargs):
        from .fields import required

        return Column(
            self.get_name(), self.sqlalchemy_type, *args,
            nullable=(required not in self.args),
            **kwargs)

class Link:
    sqlalchemy_type = None

    def to_sqlalchemy(self, *args, **kwargs):
        from .base import is_record

        if is_record(self.target):
            fk = '.'.join((self.target.get_schema(), self.target.get_name(), 'uuid'))
        else:
            fk = '.'.join((self._record.get_schema(), self.target, 'uuid'))
        return super().to_sqlalchemy(
            *(args +  (ForeignKey(fk, onupdate="CASCADE"), )), **kwargs)


class Text:
    sqlalchemy_type = sqlalchemy.Text

class Boolean:
    sqlalchemy_type = sqlalchemy.Boolean

class Date:
    sqlalchemy_type = sqlalchemy.Date

class Integer:
    sqlalchemy_type = sqlalchemy.Integer

