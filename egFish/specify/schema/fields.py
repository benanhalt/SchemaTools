from .base import Field, is_record

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
        self._target = target
        super().__init__(*args, **kwargs)

    @property
    def target(self):
        if is_record(self._target):
            return self._target
        return self.record._meta.schema._meta.records[self._target]

required = object()
