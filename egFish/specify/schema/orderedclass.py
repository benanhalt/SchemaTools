from collections import OrderedDict

class OrderedMeta(type):
    @classmethod
    def __prepare__(metacls, name, bases):
        return OrderedDict()

    def __new__(cls, name, bases, clsdict):
        clsdict['_keys'] = tuple(clsdict.keys())
        return type.__new__(cls, name, bases, dict(clsdict))

class Ordered(metaclass=OrderedMeta):
    pass
