import sqlalchemy
from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects import postgresql

from . import base, fields
from .generics import generic, method, call_next_method
from .utils import IgnoreException

@generic
def to_sqlalchemy(obj, *args, **kwargs):
    pass

@method(to_sqlalchemy)
def schema_to_sqlalchemy(schema: base.SchemaMeta, metadata):
    return [result
            for record in schema._meta.records.values()
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
        engine.execute( DropSchema(schema._meta.name, cascade=True) )

    engine.execute( CreateSchema(schema._meta.name) )

@generic
def base_columns(obj):
    pass

@method(base_columns)
def base_columns_for_record(record: base.RecordMeta):
    cols = [ Column('uuid', postgresql.UUID, primary_key=True) ]

    if record._meta.parent is not None:
        name = record._meta.parent._meta.name
        fk = '.'.join((record._meta.parent._meta.full_name, 'uuid'))
        col = Column(name, None, ForeignKey(fk, onupdate="CASCADE", deferrable=True), nullable=False)
        cols.append(col)
    else:
        cols.extend([
            Column('version', sqlalchemy.Integer, nullable=False, default=0),
        ])
    return cols

@method(to_sqlalchemy)
def record_to_sqlalchemy(record: base.RecordMeta, metadata):
    table_args = [record._meta.name, metadata]
    table_args.extend( to_sqlalchemy(field) for field in record._meta.fields.values() )
    table_args.extend( base_columns(record) )

    yield Table(*table_args, schema=record._meta.schema._meta.name)
    for child in record._meta.children.values():
        yield from to_sqlalchemy(child, metadata)

@method(base_columns)
def base_columns_for_tree_record(tree_record: base.TreeMeta):
        cols = call_next_method(tree_record)
        cols.append( Column('tree_structure', postgresql.HSTORE, nullable=False, server_default='') )
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
    fk = '.'.join((link.target._meta.full_name, 'uuid'))

    return call_next_method(link,
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

