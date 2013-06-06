from . import base, fields
from .generics import generic, method, next_method


def outerjoin(*args, **kwargs):
    pass

class Column(base.Field):
    def __init__(self, column_name, *args, process=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.column_name = column_name
        self.process = process if process is not None else lambda v: v

    def check_against_table(self):
        assert self.column_name in self.record.source_table.c, 'Table "%s" has no column named "%s".' % (table, self.column_name)

    def set_output_field(self, output_field):
        self.output_field = output_field
        try:
            self.check_field_types(output_field)
        except AssertionError as e:
            raise TypeError('Conversion field "%s" and schema field "%s" '
                            'have incompatible types.' % (self, output_field)) from e

    def check_field_types(self, output_field):
        check_field_types(output_field, self)

    def get_input_column(self):
        return self.record.source_table.c[self.column_name]

    def get_input_columns(self):
        return [ self.get_input_column() ]

    def process_row(self, row):
        input_column = self.get_input_column()
        output_column = self.output_field.name
        return output_column, self.process(row[input_column])

class Enum(Column):
    def __init__(self, column_name, values, *args, **kwargs):
        super().__init__(column_name, *args, **kwargs)
        self.values = values

    def process_row(self, row):
        output_col, value = super().process_row(row)
        return output_col, self.values[value]

    def check_field_types(self, output_field):
        super().check_field_types(output_field)
        assert isinstance(output_field, fields.Text)

class ForeignKey(Column):
    def process_row(self, row):
        output_col, value = super().process_row(row)
        return output_col, str(value) if value is not None else None

    def check_field_types(self, output_field):
        super().check_field_types(output_field)
        assert isinstance(output_field, fields.Link)

@generic
def check_field_types(output_field, input_field):
    pass

@method(check_field_types)
def check_base_field_types(out: base.Field, field):
    assert isinstance(field, Column)

@method(check_field_types)
def check_link_field_types(out: fields.Link, field):
    assert isinstance(field, ForeignKey)
