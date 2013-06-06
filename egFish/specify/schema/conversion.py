import uuid
from collections import namedtuple
from functools import partial, wraps

from . import base
from .generics import generic, method, next_method

from sqlalchemy import Table, Column, Text, Integer, select, text
from sqlalchemy.dialects.postgresql import UUID

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

class Tree(metaclass=base.TreeMeta):
    pass

def reflect_database(metadata, schema_family):
    for schema in schema_family.schemas.values():
        for record in schema.records.values():
            reflect_record(record, metadata)
@generic
def reflect_record(record, metadata):
    pass

@method(reflect_record)
def reflect_regular_record(record: base.RecordMeta, metadata):
    record.source_table = Table(record.source_table_name, metadata, autoload=True)
    for field in record.fields.values():
        field.check_against_table()

    for child in record.children.values():
        reflect_record(child, metadata)

def join_schema_family_with_conversion(schema_family, conversion_schema_family):
    for name in conversion_schema_family.schemas:
        join_schema_with_conversion(schema_family.schemas[name],
                                    conversion_schema_family.schemas[name])

def join_schema_with_conversion(schema, conversion_schema):
    for record_name in conversion_schema.records:
        join_record_with_conversion(schema.records[record_name],
                                    conversion_schema.records[record_name])

def join_record_with_conversion(record, conversion_record):
    conversion_record.output_record = record
    for field_name in conversion_record.fields:
        conversion_record.fields[field_name].set_output_field(record.fields[field_name])

        for child_name in conversion_record.children:
            join_record_with_conversion(record.children[child_name],
                                        conversion_record.children[child_name])

def do_conversion(conversion_schema_family, output_metadata):

    def convert_schema(schema, connection):
        print('Converting schema "%s".' % schema.__name__)

        for record in schema.records.values():
            convert_record(record, connection)

    def convert_record(record, connection):
        print('Converting record "%s"...' % record.__qualname__)
        data = get_data_for_record(record)

        print('Storing data...')
        output_table = output_metadata.tables[record.output_record.full_name]
        connection.execute(output_table.insert(), data)

    with output_metadata.bind.begin() as connection:
        connection.execute('SET CONSTRAINTS ALL DEFERRED')
        for schema in conversion_schema_family.schemas.values():
            convert_schema(schema, connection)

@generic
def get_data_for_record(record):
    pass

@method(get_data_for_record)
def get_data_for_regular_record(record: base.RecordMeta):
    input_columns = get_input_columns_for_record(record)
    processors = get_processors_for_record(record)

    query = select(input_columns)
    if record.where is not None:
        query = query.where( record.where(record.source_table) )

    print('Loading data...')
    return [dict(processor(row) for processor in processors)
            for row in query.execute()]

@generic
def get_input_columns_for_record(record):
    pass

@generic
def get_processors_for_record(record):
    pass

@method(get_input_columns_for_record)
def get_input_columns_for_regular_record(record: base.RecordMeta):
    input_columns = { col
                      for field in record.fields.values()
                      for col in field.get_input_columns() }

    input_columns.add( get_primary_key_col(record.source_table) )
    return input_columns

@method(get_processors_for_record)
def get_processors_for_regular_record(record: base.RecordMeta):
    processors = [ field.process_row for field in record.fields.values() ]
    processors.append( pk_processor(record) )
    return processors

@method(get_processors_for_record)
def get_processors_for_tree(tree: base.TreeMeta):
    processors = next_method(get_processors_for_record, tree)
    processors.append( lambda row: ('path', []) )
    return processors

def pk_processor(record):
    pk = get_primary_key_col(record.source_table)
    return lambda row: ('uuid', str(row[pk]))

def get_primary_key_col(table):
    return table.primary_key.columns.values()[0]

