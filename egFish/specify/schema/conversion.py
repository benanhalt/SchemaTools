#from specify.schema.conversion import Record, Schema, source_table, Enum, Tree, outerjoin
import uuid
from collections import namedtuple
from functools import partial

from sqlalchemy import Table, Column, Text, Integer, select, text
from sqlalchemy.dialects.postgresql import UUID

def outerjoin(*args, **kwargs):
    pass

def source_table(table, order_by=None, where=None):
    def decorator(cls):
        cls._source_table = table
        cls._order_by = order_by
        return cls
    return decorator

def Enum(field, values):
    class Enum:
        name = field
        def process(self, value):
            return values[value]
    return Enum()

class Schema:
    pass

class Record:
    pass

class Tree(Record):
    pass

def is_schema(obj):
    return isinstance(obj, type) and issubclass(obj, Schema)

def is_record(obj):
    return isinstance(obj, type) and issubclass(obj, Record)

def reflect_database(metadata, conversion_module):
    schemas = [v for v in conversion_module.__dict__.values() if is_schema(v)]

    records = [v for schema in schemas for v in schema.__dict__.values()
               if is_record(v)]

    for record in records:
        reflect_record(metadata, record)

def reflect_record(metadata, record):
    Table(record._source_table, metadata, autoload=True)
    sub_records = [v for v in record.__dict__.values()
                  if is_record(v)]
    for record in sub_records:
        reflect_record(metadata, record)

def define_id_map_table(metadata):
    return Table('conversion_id_map', metadata,
                 Column('source_table', Text, nullable=False),
                 Column('input_id', Integer, nullable=False),
                 Column('output_id', UUID, nullable=False, server_default=text('uuid_generate_v4()')))

def populate_id_map(input_metadata, id_map):
    insert = id_map.insert()
    with id_map.bind.begin() as connection:
        for table in input_metadata.tables.values():
            pk = get_primary_key_col(table)
            print("Fetching ids for %s" % table.name)
            values = [dict(source_table=table.name, input_id=row[0]) for row in select([pk]).execute()]
            if len(values) > 0:
                print("Inserting in map %d" % len(values))
                connection.execute(insert, values)

def get_primary_key_col(table):
    return table.primary_key.columns.values()[0]

def do_conversion(input_metadata, output_metadata, conversion_module, output_schemas, id_map=None):
    with output_metadata.bind.begin() as connection:
        connection.execute('set constraints all deferred')
        converter = Converter(input_metadata, output_metadata, conversion_module, output_schemas, id_map, connection)
        converter.do_conversion()

class Converter(
        namedtuple('Params', "input_metadata output_metadata conversion_module output_schemas id_map connection") ):

    def do_conversion(self):
        for schema in sorted(self.output_schemas, key=lambda schema: schema.get_name()):
            conversion_schema = getattr(self.conversion_module, schema.__name__)
            self.convert_schema(conversion_schema, schema)

    def convert_schema(self, conversion_schema, output_schema):
        print ("Converting schema %s..." % output_schema.get_name())

        for record in output_schema._records:
            conversion_record = getattr(conversion_schema, record.__name__)
            self.convert_record(conversion_record, record)

    def convert_record(self, conversion_record, output_record):
        print("Converting %s..." % output_record.get_name())

        input_table = self.input_metadata.tables[conversion_record._source_table]
        output_table = self.output_metadata.tables[output_record.get_schema() + '.' + output_record.get_name()]

        field_names = [field.get_name() for field in output_record._fields]
        input_field_specs = [getattr(conversion_record, name, None) for name in field_names]

        output_fields = [ 'uuid' ]
        output_fields.extend( field.get_name() for field in output_record._fields )

        from .base import is_tree
        if is_tree(output_record):
            print("Tree!")
            input_field_specs.append(namedtuple('PathSpec', 'name process')(None, lambda v: []))
            output_fields.append('path')


        input_fields = [ get_primary_key_col(input_table) ]
        input_fields.extend( input_table.c[name] if name is not None else None
                             for s in input_field_specs
                             for name in [ self.get_field_name_from_spec(s) ])


        field_processors = [ str ]
        field_processors.extend( self.get_field_processor_from_spec(s)
                                 for s in input_field_specs )

        process_row = partial(self.process_row, field_processors)

        print("Loading data...")
        data = list(dict(zip(output_fields, process_row(row)))
                    for row in select(input_fields).execute())

        print("Writing data...")
        self.execute(output_table.insert(), data)

    def get_field_name_from_spec(self, spec):
        return spec.name if hasattr(spec, 'name') else spec

    def get_field_processor_from_spec(self, spec):
        return spec.process if hasattr(spec, 'process') else lambda v: v

    def process_row(self, field_processors, row):
        return [p(v) for p, v in zip(field_processors, row)]

    def execute(self, *args, **kwargs):
        return self.connection.execute(*args, **kwargs)
