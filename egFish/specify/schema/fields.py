from .base import Field

class Text(Field):
    pass

class Date(Field):
    pass

class Integer(Field):
    pass

class Boolean(Field):
    pass

class Link(Field):
    def __init__(self, target, *args, **kwargs):
        self.target = target
        super().__init__(*args, **kwargs)

required = object()
