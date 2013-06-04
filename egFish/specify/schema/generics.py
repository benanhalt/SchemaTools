from functools import wraps
from types import MethodType
import inspect

generics_map = {}
counter = 0

class GenericsMeta(type):
    def __new__(meta, name, bases, clsdict):
        cls = super().__new__(meta, name, bases, clsdict)
        generics_bases = tuple(generics_map.get(base) for base in bases
                               if base in generics_map)
        generics_cls = type(cls.__name__ + "Generics", generics_bases, {})
        generics_map[cls] = generics_cls
        return cls

class WithGenerics(metaclass=GenericsMeta):
    pass

def get_generics_cls(cls):
    try:
        return generics_map[cls]
    except KeyError:
        raise ValueError('%s was created without generics support' % cls)

def generic(func):
    global counter
    func_name = func.__name__ + str(counter)
    counter += 1

    @wraps(func)
    def wrapped(obj, *args, **kwargs):
        generics_cls = get_generics_cls(obj.__class__)
        return call_generic_func(generics_cls, func_name, obj, *args, **kwargs)
    wrapped.name = func_name
    return wrapped

def call_generic_func(generics_cls, func_name, obj, *args, **kwargs):
    return getattr(generics_cls, func_name)(obj, *args, **kwargs)

def get_class_from_annotation(func):
    argspec = inspect.getfullargspec(func)
    return argspec.annotations[argspec.args[0]]

def method(generic_func):
    def decorator(func):
        cls = get_class_from_annotation(func)
        generics_cls = get_generics_cls(cls)
        setattr(generics_cls, generic_func.name, func)
        return func
    return decorator

def next_method(generic_func, obj, *args, **kwargs):
    func_name = generic_func.name
    generics_cls = get_generics_cls(obj.__class__)
    return call_generic_func(super(generics_cls, generics_cls), func_name, obj, *args, **kwargs)

