import sqlalchemy.schema
from sqlalchemy.dialects.postgresql import UUID as UUIDType

from . import field_options

class Schema:
    @classmethod
    def to_sqlalchemy(cls, metadata):
        return [result
                for record in cls._records
                for result in record.to_sqlalchemy(metadata)]

    @classmethod
    def create(cls, engine, metadata):
        try:
            engine.execute(
                sqlalchemy.schema.DropSchema(cls.get_name(), cascade=True))
        except:
            pass

        engine.execute(
            sqlalchemy.schema.CreateSchema(cls.get_name()))

        cls.to_sqlalchemy(metadata)

class Record:
    @classmethod
    def base_columns(cls):
        cols = [ sqlalchemy.Column('uuid', UUIDType, primary_key=True) ]
        if cls._parent is not None:
            name = cls._parent.get_name()
            fk = '.'.join((cls._parent.get_schema(), name, 'uuid'))
            col = sqlalchemy.Column(name, None, sqlalchemy.ForeignKey(fk), nullable=False)
            cols.append(col)
        else:
            cols.extend([
                sqlalchemy.Column('version', sqlalchemy.Integer, nullable=False, default=0),
            ])
        return cols

    @classmethod
    def to_sqlalchemy(cls, metadata, parent=None):
        args = [cls.get_name(), metadata]
        args.extend(field.to_sqlalchemy() for field in cls._fields)
        args.extend(cls.base_columns())
        yield sqlalchemy.Table(*args, schema=cls.get_schema())
        for child in cls._children:
            yield from child.to_sqlalchemy(metadata, cls)

class Field:
    sqlalchemy_type = sqlalchemy.Text

    def to_sqlalchemy(self, *args, **kwargs):
        return sqlalchemy.Column(
            self.get_name(), self.sqlalchemy_type, *args,
            nullable=(field_options.required not in self.args),
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
            *(args +  (sqlalchemy.ForeignKey(fk), )), **kwargs)

