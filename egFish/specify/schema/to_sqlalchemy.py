import sqlalchemy
from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects import postgresql

from . import base, fields
from .generics import generic, method, next_method

@generic
def to_sqlalchemy(obj, *args, **kwargs):
    pass

@method(to_sqlalchemy)
def schema_to_sqlalchemy(schema: base.SchemaMeta, metadata):
    return [result
            for record in schema._records
            for result in to_sqlalchemy(record, metadata)]


def process_schemas(metadata, schema_class):
    for schema in schema_class._schema_list:
        to_sqlalchemy(schema, metadata)

def create_schemas(engine, metadata, schema_class):
    for schema in schema_class._schema_list:
        create_schema(schema, engine)

    metadata.create_all(engine)

def create_schema(schema, engine):
    try:
        engine.execute(
            DropSchema(schema.get_name(), cascade=True))
    except:
        pass

    engine.execute(
        CreateSchema(schema.get_name()))

@generic
def base_columns(obj):
    pass

@method(base_columns)
def base_columns_for_record(record: base.RecordMeta):
    cols = [ Column('uuid', sqlalchemy.Text, #postgresql.UUID,
                    primary_key=True) ]
    if hasattr(record, '_parent'):
        name = record._parent.get_name()
        fk = '.'.join((record._parent.get_schema(), name, 'uuid'))
        col = Column(name, None, ForeignKey(fk, onupdate="CASCADE"), nullable=False)
        cols.append(col)
    else:
        cols.extend([
            Column('version', sqlalchemy.Integer, nullable=False, default=0),
        ])
    return cols

@method(to_sqlalchemy)
def record_to_sqlalchemy(record: base.RecordMeta, metadata, parent=None):
    args = [record.get_name(), metadata]
    args.extend(to_sqlalchemy(field) for field in record._fields)
    args.extend(base_columns(record))
    yield Table(*args, schema=record.get_schema())
    for child in record._children:
        yield from to_sqlalchemy(child, metadata, record)

@method(base_columns)
def base_columns_for_tree_record(tree_record: base.TreeMeta):
        cols = next_method(base_columns, tree_record)
        cols.append( Column('path', postgresql.ARRAY(sqlalchemy.Text), nullable=False) )
        return cols

@generic
def get_sqlalchemy_type(obj):
    pass

@method(to_sqlalchemy)
def field_to_sqlalchemy(field: base.Field, *args, **kwargs):
    return Column(
        field.get_name(), get_sqlalchemy_type(field), *args,
        nullable=(fields.required not in field.args),
        **kwargs)

@method(get_sqlalchemy_type)
def link_type(obj: fields.Link):
    return None

@method(to_sqlalchemy)
def link_to_sqlalchemy(link: fields.Link, *args, **kwargs):
    if base.is_record(link.target):
        fk = '.'.join((link.target.get_schema(), link.target.get_name(), 'uuid'))
    else:
        fk = '.'.join((link._record.get_schema(), link.target, 'uuid'))

    return next_method(to_sqlalchemy, link,
        *(args +  (ForeignKey(fk, onupdate="CASCADE"), )), **kwargs)

@method(get_sqlalchemy_type)
def text_type(field: fields.Text):
    return sqlalchemy.Text

@method(get_sqlalchemy_type)
def bool_type(field: fields.Boolean):
    return sqlalchemy.Boolean

@method(get_sqlalchemy_type)
def date_type(field: fields.Date):
    return sqlalchemy.Date

@method(get_sqlalchemy_type)
def int_type(field: fields.Integer):
    return sqlalchemy.Integer

