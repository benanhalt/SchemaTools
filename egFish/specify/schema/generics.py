from functools import wraps
from collections import defaultdict
import inspect

generics_map = defaultdict(dict)

class NoMethodException(Exception):
    pass

def generic(func):
    @wraps(func)
    def generic_func(obj, *args, **kwargs):
        try:
            return call_generic(obj.__class__.__mro__, generic_func, obj, *args, **kwargs)
        except NoMethodException as e:
            raise NoMethodException('No method for generic function "%r" for object "%r".' % (
                func, obj)) from e

    generic_func.default = func
    return generic_func

def call_generic(mro, generic_func, obj, *args, **kwargs):
    if mro is ():
        raise NoMethodException()

    cls = mro[0]

    try:
        meth = generics_map[cls][generic_func]
    except KeyError:
        return call_generic(cls.__mro__[1:], generic_func, obj, *args, **kwargs)

    return meth(obj, *args, **kwargs)

def get_class_from_annotation(func):
    argspec = inspect.getfullargspec(func)
    return argspec.annotations[argspec.args[0]]

def method(generic_func):
    def decorator(meth):
        cls = get_class_from_annotation(meth)
        generics_map[cls][generic_func] = meth
        meth.generic_func = generic_func
        return meth
    return decorator

def next_method(current_meth, obj, *args, **kwargs):
    cls = get_class_from_annotation(current_meth)
    try:
        return call_generic(cls.__mro__[1:], current_meth.generic_func, obj, *args, **kwargs)
    except NoMethodException as e:
        raise NoMethodException('No next method for generic function "%r" for object "%r".' % (
            func, obj)) from e
