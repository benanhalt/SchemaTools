from uuid import uuid4, uuid5
from collections import namedtuple
from functools import partial, wraps
from types import MethodType

from . import base
from .generics import generic, method, next_method

from sqlalchemy import Table, Column, Text, Integer, select, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.mysql import BIT as mysql_BIT

root_uuid = uuid4()

def mysql_BIT_processor(self, dialect, coltype):
    def process(value):
        if value is None:
            return None
        v = 0
        for i in value:
            v = v << 8 | i
        return v
    return process
mysql_BIT.result_processor = MethodType(mysql_BIT_processor, mysql_BIT)

SchemaFamily = base.SchemaFamily
Record = base.Record

def source_table(table_name, order_by=None, parent_field=None, where=None):
    def decorator(record):
        record.source_table_name = table_name
        record.order_by = order_by
        record.parent_field = parent_field
        record.where = where
        return record
    return decorator

def skip(cls):
    cls.skip = True
    return cls

class Tree(metaclass=base.TreeMeta):
    pass

def reflect_database(metadata, schema_family):
    for schema in schema_family.schemas.values():
        for record in schema._meta.records.values():
            reflect_record(record, metadata)
@generic
def reflect_record(record, metadata):
    pass

@method(reflect_record)
def reflect_regular_record(record: base.RecordMeta, metadata):
    record.source_table = reflect_table(record.source_table_name, metadata)

    for field in record._meta.fields.values():
        field.check_against_table()

    for child in record._meta.children.values():
        reflect_record(child, metadata)

def reflect_table(table_name, metadata):
    return Table(table_name, metadata, autoload=True)

def join_schema_family_with_conversion(schema_family, conversion_schema_family):
    for name in conversion_schema_family.schemas:
        join_schema_with_conversion(schema_family.schemas[name],
                                    conversion_schema_family.schemas[name])

def join_schema_with_conversion(schema, conversion_schema):
    for record_name in conversion_schema._meta.records:
        join_record_with_conversion(schema._meta.records[record_name],
                                    conversion_schema._meta.records[record_name])

def join_record_with_conversion(record, conversion_record):
    conversion_record.output_record = record
    for field in conversion_record._meta.fields.values():
        field.set_output_field()

    for child_name in conversion_record._meta.children:
        join_record_with_conversion(record._meta.children[child_name],
                                    conversion_record._meta.children[child_name])

def do_conversion(conversion_schema_family, output_metadata):

    def convert_schema(schema, connection):
        print('Converting schema "%s".' % schema.__name__)

        for record in schema._meta.records.values():
            if hasattr(record, 'skip'): continue
            convert_record(record, connection)

    def convert_record(record, connection):
        print('Converting record "%s"...' % record.__qualname__)
        data = get_data_for_record(record)

        print('Storing data...')
        output_table = output_metadata.tables[record.output_record._meta.full_name]
        connection.execute(output_table.insert(), data)

        postprocess_record(record, output_metadata, connection)

        for child in record._meta.children.values():
            convert_record(child, connection)

    with output_metadata.bind.begin() as connection:
        connection.execute('SET CONSTRAINTS ALL DEFERRED')
        for schema in conversion_schema_family.schemas.values():
            if hasattr(schema, 'skip'): continue
            convert_schema(schema, connection)

@generic
def get_data_for_record(record):
    pass

@method(get_data_for_record)
def get_data_for_regular_record(record: base.RecordMeta):
    input_columns = get_input_columns_for_record(record)
    processors = get_processors_for_record(record)

    query = select(input_columns)

    joins, wheres = add_joins(record)
    select_from = record.source_table
    for join in joins:
        select_from = select_from.join(*join)

    outer_joins = {table: cond
                   for field in record._meta.fields.values()
                   for table, cond in field.joins.items()}

    for table, cond in outer_joins.items():
        select_from = select_from.outerjoin(table, cond)

    query = query.select_from(select_from)
    for where in wheres:
        query = query.where(where)

    print('Loading data...')
    return [dict(processor(row) for processor in processors)
            for row in query.execute()]

def add_joins(record):
    joins = []
    wheres = []
    while True:
        if record.where is not None:
            wheres.append( record.where(record.source_table) )

        if record.parent_field is None:
            break

        joins.append( (record._meta.parent.source_table,
                       record.source_table.c[record.parent_field] == \
                       get_primary_key_col(record._meta.parent.source_table)) )

        record = record._meta.parent
    return joins, wheres

@generic
def get_input_columns_for_record(record):
    pass

@generic
def get_processors_for_record(record):
    pass

@method(get_input_columns_for_record)
def get_input_columns_for_regular_record(record: base.RecordMeta):
    input_columns = { col
                      for field in record._meta.fields.values()
                      for col in field.get_input_columns() }

    input_columns.add( get_primary_key_col(record.source_table) )

    if record.parent_field is not None:
        input_columns.add( record.source_table.c[record.parent_field] )

    return input_columns

@method(get_processors_for_record)
def get_processors_for_regular_record(record: base.RecordMeta):
    processors = [ field.process_row for field in record._meta.fields.values() ]
    processors.append( pk_processor(record) )

    if record.parent_field is not None:
        processors.append( parent_field_processor(record) )

    return processors

@generic
def postprocess_record(record, output_metadata, connection):
    pass

@method(postprocess_record)
def postprocess_regular_record(record: base.RecordMeta, *args):
    pass

def pk_processor(record):
    pk = get_primary_key_col(record.source_table)
    table_uuid = gen_table_uuid(record.source_table)
    print(table_uuid)
    return lambda row: ('uuid', gen_row_uuid(table_uuid, row[pk]))

def get_primary_key_col(table):
    return table.primary_key.columns.values()[0]

def parent_field_processor(record):
    parent_field = record.output_record._meta.parent._meta.name # TODO: this should make use of to_sqlalchemy
    fk_col = record.source_table.c[record.parent_field]
    table_uuid = gen_table_uuid(record._meta.parent.source_table)
    return lambda row: (parent_field, gen_row_uuid(table_uuid, row[fk_col]))

def gen_table_uuid(table):
    return uuid5(root_uuid, table.name)

def gen_row_uuid(table_uuid, id):
    if id is None: return None
    return uuid5(table_uuid, str(id))
