from collections import OrderedDict

class OrderedMetaclass(type):
    @classmethod
    def __prepare__(metacls, name, bases):
        return OrderedDict()

    def __new__(cls, name, bases, clsdict):
        fields = tuple(clsdict.keys())
        clsdict['_fields'] = fields
        return type.__new__(cls, name, bases, dict(clsdict))

class Ordered(metaclass=OrderedMetaclass):
    pass
