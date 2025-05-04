import typing
import inspect
import types
import collections.abc
from typing import (
    Any, Union, Literal, List, Dict, Set, Tuple, Callable, ParamSpec,Concatenate,
    get_origin, get_args, TypeVar, ForwardRef, Annotated, Type
)
from types import FunctionType, NoneType
# import functools

# @functools.lru_cache(maxsize=128)
# def resolve_forward_ref_cached(forward_arg: str, globalns_str: str, localns_str: str):
#     forward_ref = ForwardRef(forward_arg)
#     return forward_ref._evaluate(eval(globalns_str), eval(localns_str), frozenset())


def get_callable_signature(obj):
    """
    Given a callable object, retrieves its signature.
    Handles normal functions, bound methods, unbound methods, 
    classes (for __init__), static methods, class methods, and callable instances.
    """
    if not callable(obj):
        raise TypeError(f"Object {obj} is not callable.")
    
    # Case 1: If obj is a class, we need to get the signature of its __init__ method
    if inspect.isclass(obj):  # Class
        return inspect.signature(obj.__init__)
    
    # Case 2: If obj is a static method, get the signature of the function itself
    if isinstance(obj, staticmethod):  # Static method
        return inspect.signature(obj.__func__)
    
    # Case 3: If obj is a class method, get the signature of the function itself
    if isinstance(obj, classmethod):  # Class method
        return inspect.signature(obj.__func__)
    
    # Case 4: Normal function or lambda function
    if isinstance(obj, (types.FunctionType, types.LambdaType)):  # Normal function or lambda
        return inspect.signature(obj)

    # Case 5: Bound method (instance method), use the function itself
    if isinstance(obj, object):  # Bound method (instance method)
        return inspect.signature(obj.__func__)

    # Case 6: Callable object (implements __call__), inspect the __call__ method
    if isinstance(obj, collections.abc.Callable):  # Callable objects
        return inspect.signature(obj.__call__)

    # Case 7: Async function or coroutine function
    if inspect.iscoroutinefunction(obj):  # Async functions
        return inspect.signature(obj)
    
    # Default case: Should not reach here unless it's a callable we cannot handle
    raise TypeError(f"Object {obj} is callable, but its signature could not be determined.")



def resolve_forward_ref(forward_ref: ForwardRef, globalns, localns):
    try:
        if isinstance(forward_ref, ForwardRef):
            resolved = forward_ref._evaluate(globalns, localns, frozenset())
            if isinstance(resolved, ForwardRef):
                raise TypeError(f"Unresolvable ForwardRef: {forward_ref.__forward_arg__}")
            return resolved
        else:
            return forward_ref
    except Exception:
        raise TypeError(f"Cannot resolve ForwardRef: {forward_ref}")

def safe_isinstance(obj, type_hint, *, globalns=globals(), localns=locals()) -> bool:
    if isinstance(type_hint, ForwardRef):
        type_hint = resolve_forward_ref(type_hint, globalns, localns)
        return safe_isinstance(obj, type_hint, globalns=globalns, localns=localns)
    if type_hint is typing.NoReturn:
        return False  # No object can be an instance of NoReturn
    if type_hint is Any:
        return True
    if inspect.isclass(type_hint):
        return isinstance(obj, type_hint)
    if isinstance(type_hint, FunctionType) and hasattr(type_hint, '__supertype__'):
        return safe_isinstance(obj, type_hint.__supertype__, globalns=globalns, localns=localns)
    if isinstance(type_hint, TypeVar):
        if type_hint.__constraints__:
            return any(safe_isinstance(obj, c, globalns=globalns, localns=localns) for c in type_hint.__constraints__)
        return True
    if isinstance(type_hint, ParamSpec):
        return True

    origin = get_origin(type_hint)
    args = get_args(type_hint)    
    if origin is Annotated:
        return safe_isinstance(obj, args[0], globalns=globalns, localns=localns)
    if origin is Union:
        return any(safe_isinstance(obj, arg, globalns=globalns, localns=localns) for arg in args)
    if origin is Literal:
        return obj in args
    if origin in (list, List):
        return isinstance(obj, list) and all(safe_isinstance(e, args[0], globalns=globalns, localns=localns) for e in obj)
    if origin in (dict, Dict):
        return isinstance(obj, dict) and all(
            safe_isinstance(k, args[0], globalns=globalns, localns=localns) and
            safe_isinstance(v, args[1], globalns=globalns, localns=localns)
            for k, v in obj.items())
    if origin in (set, Set):
        return isinstance(obj, set) and all(safe_isinstance(e, args[0], globalns=globalns, localns=localns) for e in obj)
    if origin in (tuple, Tuple):
        if not isinstance(obj, tuple):
            return False
        if len(args) == 2 and args[1] is Ellipsis:
            return all(safe_isinstance(e, args[0], globalns=globalns, localns=localns) for e in obj)
        if len(args) != len(obj):
            return False
        return all(safe_isinstance(o, t, globalns=globalns, localns=localns) for o, t in zip(obj, args))
    if origin in (Callable, collections.abc.Callable):
        if not callable(obj):
            return False
        expected_args, expected_return = args if len(args) == 2 else (Ellipsis, Any)
        if expected_args is Ellipsis:
            return True
        if isinstance(expected_args, ParamSpec):
            return True  # can't check param types at runtime; assume it's okay
        has_trailing_param_spec = False
        accepts_kwargs = False

        if get_origin(expected_args) is Concatenate:
            # Unpack Concatenate[int, str, P] → flatten to list of types (ignoring P)
            concrete_args = get_args(expected_args)
            prefix_args = []
            for arg in concrete_args:
                if isinstance(arg, ParamSpec):
                    has_trailing_param_spec = True
                    accepts_kwargs  = hasattr(arg, 'kwargs')
                    break  # stop at ParamSpec; runtime checking not possible beyond here
                prefix_args.append(arg)
            expected_args = prefix_args
        # Now use resolved_args instead of expected_args for param checks
        try:
            sig = get_callable_signature(obj)
            params = list(sig.parameters.values())
            positional_params = [
                p for p in params
                if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            ]
            keyword_only_params = [
                p for p in params
                if p.kind == inspect.Parameter.KEYWORD_ONLY
            ]            
            if not has_trailing_param_spec and len(expected_args) != len(params):
                return False
            if has_trailing_param_spec and len(expected_args) > len(positional_params):
                return False
            
            for expected, param in zip(expected_args, positional_params):
                if param.annotation is inspect.Parameter.empty:
                    continue
                if not safe_subtype(expected, param.annotation):
                    return False

            # Optional: check keyword-only params if no **kwargs in ParamSpec
            if not accepts_kwargs:
                for param in keyword_only_params:
                    if (param.default is inspect.Parameter.empty and
                        param.annotation is inspect.Parameter.empty):
                        return False  # Required untyped keyword-only param

            if sig.return_annotation is not inspect.Signature.empty:
                if not safe_subtype(sig.return_annotation, expected_return):
                    return False
            return True
        except Exception:
            return False
    origin = get_origin(type_hint)
    if origin is not None and inspect.isclass(origin):
        return isinstance(obj, origin)
    raise TypeError(f"safe_isinstance does not support this type hint: {type_hint}")


def safe_subtype_of_forward_ref(subclass, type_hint, globalns, localns, treat_literal_as_base_type: bool):
    try:
        type_hint = resolve_forward_ref(type_hint, globalns, localns)
        if isinstance(subclass, ForwardRef):
            subclass = resolve_forward_ref(subclass, globalns, localns)
        return safe_subtype(subclass, 
                            type_hint,
                            globalns=globalns,
                            localns=localns,
                            treat_literal_as_base_type=treat_literal_as_base_type)
    except TypeError:
        if isinstance(subclass, ForwardRef) and isinstance(type_hint, ForwardRef):
            # If both are ForwardRefs, an we can't resolve them, just compare their __forward_arg__ attributes
            return subclass.__forward_arg__ == type_hint.__forward_arg__
        return False

def safe_subtype_of_annotated(subclass, type_hint, globalns, localns, treat_literal_as_base_type: bool):
    args = get_args(type_hint)
    return safe_subtype(subclass, args[0],
                            globalns=globalns,
                            localns=localns,
                            treat_literal_as_base_type=treat_literal_as_base_type)

def safe_subtype_of_union(subclass, type_hint, globalns, localns, treat_literal_as_base_type: bool):
    def safe_flat_union(t):
        """
        Flattens a Union type hint into a set of types.
        Handles nested Unions and other typing constructs.
        """
        if get_origin(t) is Union:
            args = get_args(t)
            flattened = set()
            for arg in args:
                flattened.update(safe_flat_union(arg))
            return flattened
        else:
            return {t}
    flat_subclass = safe_flat_union(subclass)
    flat_type_hint = safe_flat_union(type_hint)
    for s in flat_subclass:
        found = False
        for t in flat_type_hint:    
            if safe_subtype(s, t,
                            globalns=globalns,
                            localns=localns,
                            treat_literal_as_base_type=treat_literal_as_base_type):
                found = True
                break
        if not found:
            return False
    return True



def safe_subtype_of_type(subclass, type_hint, globalns, localns, treat_literal_as_base_type: bool):
    if get_origin(subclass) not in (type, Type):
        return False
    targs = get_args(type_hint)
    sargs = get_args(subclass)
    if len(targs) != 1 or len(sargs) != 1:
        raise TypeError("Type hint must be a single type argument")
    return safe_subtype(sargs[0], targs[0],
                        globalns=globalns,
                        localns=localns,
                        treat_literal_as_base_type=treat_literal_as_base_type)

def safe_subtype_of_literal(subclass, type_hint, globalns, localns, treat_literal_as_base_type: bool):
    args = get_args(type_hint)
    if get_origin(subclass) is Literal:
        subclass_args = set(get_args(subclass))
        type_hint_args = set(args)
        return subclass_args.issubset(type_hint_args)
    elif treat_literal_as_base_type:
        return all(safe_subtype(subclass, type(lit),
                                globalns=globalns,
                                localns=localns,
                                treat_literal_as_base_type=treat_literal_as_base_type) for lit in args)
    else:
        raise TypeError("safe_subtype does not support Literal without treat_literal_as_base_type=True")


def safe_subtype_of_typevar(subclass, type_hint, globalns, localns, treat_literal_as_base_type: bool ):
    if type_hint.__constraints__:
        return any(safe_subtype(subclass, c,
                                    globalns=globalns,
                                    localns=localns,
                                    treat_literal_as_base_type=treat_literal_as_base_type) for c in type_hint.__constraints__)
    if type_hint.__bound__ is not None:
        if not safe_subtype(subclass, 
                            type_hint.__bound__,
                            globalns=globalns,
                            localns=localns,
                            treat_literal_as_base_type=treat_literal_as_base_type):
            return False        
    return True  # unconstrained TypeVar matches anything

def safe_subtype_of_list(subclass, type_hint, globalns, localns, treat_literal_as_base_type: bool):
    if subclass not in (List, list) and get_origin(subclass) not in (List, list):
        return False
    targs = get_args(type_hint)
    sargs = get_args(subclass)
    return safe_subtype(sargs[0], 
                        targs[0],
                        globalns=globalns,
                        localns=localns,
                        treat_literal_as_base_type=treat_literal_as_base_type)

def safe_subtype_of_dict(subclass, type_hint, globalns, localns, treat_literal_as_base_type: bool):
    if subclass not in (Dict, dict) and get_origin(subclass) not in (Dict, dict):
        return False
    targs = get_args(type_hint)
    sargs = get_args(subclass)
    # the key of a dict is like a parameter of a function
    # the value of a dict is like the return type of a function
    # so key is contravariant and value is covariant
    k = safe_subtype(targs[0], 
                     sargs[0],
                    globalns=globalns,
                    localns=localns,
                    treat_literal_as_base_type=treat_literal_as_base_type)
    v = safe_subtype(sargs[1], 
                     targs[1],
                    globalns=globalns,
                    localns=localns,
                    treat_literal_as_base_type=treat_literal_as_base_type)
    return  k and v

def safe_subtype_of_set(subclass, type_hint, globalns, localns, treat_literal_as_base_type: bool):
    if subclass not in (Set, set) and get_origin(subclass) not in (Set, set):
        return False
    targs = get_args(type_hint)
    sargs = get_args(subclass)
    return safe_subtype(sargs[0], 
                        targs[0],
                        globalns=globalns,
                        localns=localns,
                        treat_literal_as_base_type=treat_literal_as_base_type)



def safe_subtype_of_tuple(subclass, type_hint, globalns, localns, treat_literal_as_base_type: bool):
    if subclass not in (Tuple, tuple) and get_origin(subclass) not in (Tuple, tuple):
        return False
    targs = get_args(type_hint)  
    sargs = get_args(subclass)
    for s, t in zip(sargs, targs):
        if s is Ellipsis and t is not Ellipsis:
            return False
        if t is Ellipsis:
            # If the type hint is a tuple with Ellipsis, we can skip checking the rest
            break
        if not safe_subtype(s, 
                            t,
                            globalns=globalns,
                            localns=localns,
                            treat_literal_as_base_type=treat_literal_as_base_type):
            return False
    return True

def safe_subtype_of_callable(subclass, type_hint, globalns, localns, treat_literal_as_base_type: bool):
    if get_origin(subclass) not in (Callable, collections.abc.Callable):
        return False
    expected = get_args(type_hint)
    expected_args, expected_ret = expected if len(expected) == 2 else (Ellipsis, Any)
    actual = get_args(subclass)
    actual_args, actual_ret = actual if len(actual) == 2 else (Ellipsis, Any)

    if actual_args is not Ellipsis and expected_args is Ellipsis:
        return False
    if isinstance(actual_args, ParamSpec) and not isinstance(expected_args, ParamSpec):
        return False
    if isinstance(expected_args, ParamSpec) and not isinstance(actual_args, ParamSpec):
        return False
    if (actual_args is Ellipsis 
        or expected_args is Ellipsis 
        or (isinstance(expected_args, ParamSpec) and isinstance(actual_args, ParamSpec))
        ):
        return safe_subtype(actual_ret, 
                            expected_ret,
                            globalns=globalns,
                            localns=localns,
                            treat_literal_as_base_type=treat_literal_as_base_type)
    expected_has_trailing_param_spec = False
    if get_origin(expected_args) is Concatenate:
        expected_concrete_args = get_args(expected_args)
        expected_prefix_args = []
        for arg in expected_concrete_args:
            if isinstance(arg, ParamSpec):
                expected_has_trailing_param_spec = True
                break
            expected_prefix_args.append(arg)
        expected_args = expected_prefix_args
    
    actual_has_trailing_param_spec = False
    if get_origin(actual_args) is Concatenate:
        actual_concrete_args = get_args(actual_args)
        actual_prefix_args = []
        for arg in actual_concrete_args:
            if isinstance(arg, ParamSpec):
                actual_has_trailing_param_spec = True
                break
            actual_prefix_args.append(arg)
        actual_args = actual_prefix_args

    if expected_has_trailing_param_spec and not actual_has_trailing_param_spec:
        return False
    if not actual_has_trailing_param_spec and len(expected_args) != len(actual_args):
        return False
    if actual_has_trailing_param_spec and len(expected_args) < len(actual_args):
        return False
    for expected, actual in zip(expected_args, actual_args):
        if not safe_subtype(expected, actual,
                            globalns=globalns,
                            localns=localns,
                            treat_literal_as_base_type=treat_literal_as_base_type):
            return False    
    return safe_subtype(actual_ret, expected_ret,
                        globalns=globalns,
                        localns=localns,
                        treat_literal_as_base_type=treat_literal_as_base_type)
        
    
def safe_subtype(
    subclass,
    type_hint,
    *,
    globalns=globals(),
    localns=locals(),
    treat_literal_as_base_type: bool = False
) -> bool:
    if isinstance(type_hint, ForwardRef):
        return safe_subtype_of_forward_ref(subclass, type_hint, globalns=globalns, localns=localns, treat_literal_as_base_type=treat_literal_as_base_type)

    if isinstance(type_hint, FunctionType) and hasattr(type_hint, '__supertype__'):
        return safe_subtype(subclass, type_hint.__supertype__,
                            globalns=globalns,
                            localns=localns,
                            treat_literal_as_base_type=treat_literal_as_base_type)    
    if type_hint is typing.NoReturn:
        return subclass is typing.NoReturn  # Only NoReturn is subtype of NoReturn    
    if type_hint is Any:
        return True
    if isinstance(type_hint, TypeVar):
        return safe_subtype_of_typevar(subclass, type_hint, globalns=globalns, localns=localns, treat_literal_as_base_type=treat_literal_as_base_type)
    if isinstance(type_hint, ParamSpec):
        return True

    origin = get_origin(type_hint)
    if origin is Annotated:
        return safe_subtype_of_annotated(subclass, type_hint, globalns=globalns, localns=localns, treat_literal_as_base_type=treat_literal_as_base_type)
    if inspect.isclass(type_hint):
        if not inspect.isclass(subclass):
            return False
        return issubclass(subclass, type_hint)
    if origin is Union:
        return safe_subtype_of_union(subclass, type_hint, globalns=globalns, localns=localns, treat_literal_as_base_type=treat_literal_as_base_type)
    if origin is Literal:
        return safe_subtype_of_literal(subclass, type_hint, globalns=globalns, localns=localns, treat_literal_as_base_type=treat_literal_as_base_type)    
    if origin in (list, List):
        return safe_subtype_of_list(subclass, type_hint, globalns=globalns, localns=localns, treat_literal_as_base_type=treat_literal_as_base_type)
    if origin in (dict, Dict):
        return safe_subtype_of_dict(subclass, type_hint, globalns=globalns, localns=localns, treat_literal_as_base_type=treat_literal_as_base_type)
    if origin in (set, Set):
        return safe_subtype_of_set(subclass, type_hint, globalns=globalns, localns=localns, treat_literal_as_base_type=treat_literal_as_base_type)
    if origin in (tuple, Tuple):
        return safe_subtype_of_tuple(subclass, type_hint, globalns=globalns, localns=localns, treat_literal_as_base_type=treat_literal_as_base_type)    
    if origin in (Callable, collections.abc.Callable):
        return safe_subtype_of_callable(subclass, type_hint, globalns=globalns, localns=localns, treat_literal_as_base_type=treat_literal_as_base_type)        
    if origin in (type, Type):
        return safe_subtype_of_type(subclass, type_hint, globalns=globalns, localns=localns, treat_literal_as_base_type=treat_literal_as_base_type)
    return issubclass(subclass, type_hint)

    



def is_type_object(obj, special_form_as_type:bool = True) -> bool:
    if inspect.isclass(obj):
        return True  # normal class    
    if isinstance(obj, TypeVar):
        return True  # TypeVar
    if isinstance(obj, ForwardRef):
        return True  # ForwardRef
    if isinstance(obj, typing._SpecialForm):  # This includes Literal, Union, Optional, etc.
        return special_form_as_type        
    if obj in (typing.Any, typing.NoReturn):
        return True  # special typing markers
    if get_origin(obj) is not None:
        return True  # typing constructs like Union, Optional, List[int], etc.
    # Handle NewType (they are just functions, but typing treats them as distinct)
    if isinstance(obj, FunctionType) and hasattr(obj, "__supertype__"):
        return True
    return False


def is_service_class(cls: type, deep: bool = False) -> bool:
    if not inspect.isclass(cls):
        return False

    # Determine the class or MRO to inspect
    classes_to_check = cls.__mro__ if deep else (cls,)

    has_class_or_static = False

    # Loop through the classes in MRO (or just the class itself)
    for base in classes_to_check:
        for name, attr in base.__dict__.items():
            # If it's an instance method, reject it
            if inspect.isfunction(attr):
                return False  # Found an instance method — not a service class

            # If it's a classmethod or staticmethod, mark it
            if isinstance(attr, (classmethod, staticmethod)):
                has_class_or_static = True

            # Special check for __init__ method
            if name == "__init__":
                if not isinstance(attr, (classmethod, staticmethod)) and attr is not object.__init__:
                    return False

    # Return True if we found at least one classmethod or staticmethod
    return has_class_or_static


if __name__ == '__main__':
    pass
    # from typing import Optional
    # class A:
    #     pass
    # class B(A):
    #     pass
    # class C:
    #     pass
    # print(safe_subtype(Optional[A], Optional[A]))
    # print(safe_subtype(A, Optional[A]))
    # print(safe_subtype(NoneType, Optional[A]))
    # print(safe_subtype(Union[A], Optional[A]))
    # print(safe_subtype(Union[NoneType], Optional[A]))
    # print(safe_subtype(B, Optional[A]))
    # print(safe_subtype(C, Optional[A]))
    # print(safe_subtype(Type[Any], Type[Any]))

    # EntryFilterType = Union[
    #     Type[Any], 
    #     Callable[[Any], bool],
    #     Tuple[Union['NOT', 'AND', 'OR', 'XOR'], ...]
    # ]
    # class NOT:
    #     pass
    # class AND:
    #     pass
    # class OR:
    #     pass
    # class XOR:
    #     pass

    # # print(safe_subtype(Optional[EntryFilterType], Optional[EntryFilterType]))
    # print(safe_subtype(List[NOT], List[NOT]))