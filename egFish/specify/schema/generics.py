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

def call_next_method(obj, *args, **kwargs):
    mro, generic_func = find_generic_func_in_stack()
    try:
        return call_generic(mro[1:], generic_func, obj, *args, **kwargs)
    except NoMethodException as e:
        raise NoMethodException('No next method for generic function "%r" for object "%r".' % (
            func, obj)) from e

def find_generic_func_in_stack():
    for outer_frame in inspect.getouterframes(inspect.currentframe()):
        frame = outer_frame[0]
        if frame.f_code is call_generic.__code__:
            return frame.f_locals['mro'], frame.f_locals['generic_func']
    raise Exception("Couldn't locate 'call_generic' function in call stack.")
