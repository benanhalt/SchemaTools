from collections import namedtuple

from . import base, fields
from .generics import generic, method, next_method
from .utils import IgnoreException
from .conversion import get_primary_key_col, reflect_table, gen_table_uuid, gen_row_uuid



ReverseJoin = namedtuple("ReverseJoin", "table_name column_name")

class Column(base.Field):
    def __init__(self, path, *, process=None):
        super().__init__()
        if isinstance(path, str):
            self.path = [ path ]
        else:
            self.path = path

        self.process = process if process is not None else lambda v: v

    def check_against_table(self):
        table = self.record.source_table
        path = list(self.path)
        self.joins = {}
        while True:
            column_name = path.pop(0)
            if isinstance(column_name, ReverseJoin):
                assert len(path) > 0, "ReverseJoin cannot be final element of path."
                pk = get_primary_key_col(table)
                table = reflect_table(column_name.table_name, self.record.source_table.metadata)
                column_name = column_name.column_name
                assert_column_in_table(table, column_name)
                column = table.c[column_name]
                self.joins[table] = column == pk
                continue

            assert_column_in_table(table, column_name)
            column = table.c[column_name]
            if len(path) > 0:
                table = get_remote_table_from_fk(column)
                self.joins[table] = column == get_primary_key_col(table)
            else:
                break

        self.column_name = column_name
        self.column = table.c[self.column_name]

    def set_output_field(self):
        self.output_field = self.record.output_record._meta.fields[self.__name__]
        try:
            self.check_field_types()
        except AssertionError as e:
            raise TypeError('Conversion field "%s" and schema field "%s" '
                            'have incompatible types.' % (self, self.output_field)) from e

    def check_field_types(self):
        check_field_types(self.output_field, self)

    def get_input_columns(self):
        return [ self.column ]

    def process_row(self, row):
        output_column = self.output_field.name
        return output_column, self.process(row[self.column])

class Enum(Column):
    def __init__(self, path, values, *args, **kwargs):
        super().__init__(path, *args, **kwargs)
        self.values = values

    def process_row(self, row):
        output_col, value = super().process_row(row)
        return output_col, self.values[value]

    def check_field_types(self):
        super().check_field_types()
        assert isinstance(self.output_field, fields.Text)

class ForeignKey(Column):
    def get_table_uuid(self):
        with IgnoreException(AttributeError):
            return self.table_uuid
        self.table_uuid = gen_table_uuid(get_remote_table_from_fk(self.column))
        return self.table_uuid

    def process_row(self, row):
        output_col, value = super().process_row(row)
        if value is not None:
            value = gen_row_uuid(self.get_table_uuid(), value)
        return output_col, value

    def check_field_types(self):
        super().check_field_types()
        assert isinstance(self.output_field, fields.Link)

@generic
def check_field_types(output_field, input_field):
    pass

@method(check_field_types)
def check_base_field_types(out: base.Field, field):
    assert isinstance(field, Column)

@method(check_field_types)
def check_link_field_types(out: fields.Link, field):
    assert isinstance(field, ForeignKey)

def assert_column_in_table(table, column_name):
    assert column_name in table.c, 'Table "%s" has no column named "%s".' % (table, column_name)

def get_remote_table_from_fk(column):
    return list(column.foreign_keys)[0].column.table
