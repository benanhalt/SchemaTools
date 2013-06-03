from .base import Field, sql_mixin

class Text(sql_mixin.Text, Field):
    pass

class Date(sql_mixin.Date, Field):
    pass

class Integer(sql_mixin.Integer, Field):
    pass

class Boolean(sql_mixin.Boolean, Field):
    pass

class Link(sql_mixin.Link, Field):
    def __init__(self, target, *args, **kwargs):
        self.target = target
        super().__init__(*args, **kwargs)

required = object()
