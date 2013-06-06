import sqlalchemy
from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects import postgresql

from . import base, fields
from .generics import generic, method, next_method
from .utils import IgnoreException

@generic
def to_sqlalchemy(obj, *args, **kwargs):
    pass

@method(to_sqlalchemy)
def schema_to_sqlalchemy(schema: base.SchemaMeta, metadata):
    return [result
            for record in schema.records.values()
            for result in to_sqlalchemy(record, metadata)]


def process_schemas(metadata, schema_family):
    for schema in schema_family.schemas.values():
        to_sqlalchemy(schema, metadata)

def create_schemas(engine, metadata, schema_family):
    for schema in schema_family.schemas.values():
        create_schema(schema, engine)

    metadata.create_all(engine)

def create_schema(schema, engine):
    with IgnoreException():
        engine.execute( DropSchema(schema.name, cascade=True) )

    engine.execute( CreateSchema(schema.name) )

@generic
def base_columns(obj):
    pass

@method(base_columns)
def base_columns_for_record(record: base.RecordMeta):
    cols = [ Column('uuid', sqlalchemy.Text, primary_key=True) ]

    if hasattr(record, 'parent'):
        name = record.parent.name
        fk = '.'.join((record.parent.schema.name, record.parent.name, 'uuid'))
        col = Column(name, None, ForeignKey(fk, onupdate="CASCADE", deferrable=True), nullable=False)
        cols.append(col)
    else:
        cols.extend([
            Column('version', sqlalchemy.Integer, nullable=False, default=0),
        ])
    return cols

@method(to_sqlalchemy)
def record_to_sqlalchemy(record: base.RecordMeta, metadata, parent=None):
    table_args = [record.name, metadata]
    table_args.extend( to_sqlalchemy(field) for field in record.fields.values() )
    table_args.extend( base_columns(record) )

    yield Table(*table_args, schema=record.schema.name)
    for child in record.children.values():
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
        field.name, get_sqlalchemy_type(field), *args,
        nullable=(fields.required not in field.args),
        **kwargs)

@method(get_sqlalchemy_type)
def link_type(obj: fields.Link):
    return None

@method(to_sqlalchemy)
def link_to_sqlalchemy(link: fields.Link, *args, **kwargs):
    if base.is_record(link.target):
        fk = '.'.join((link.target.schema.name, link.target.name, 'uuid'))
    else:
        fk = '.'.join((link.record.schema.name, link.target, 'uuid'))

    return next_method(to_sqlalchemy, link,
                       *(args +  (ForeignKey(fk, onupdate="CASCADE", deferrable=True), )),
                       **kwargs)

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

