import inspect
from typing import get_type_hints, Protocol
from types import FunctionType, MethodType
from enum import Enum
import sys
from .safe_typing import safe_subtype

class CheckMode(str, Enum):
    """Enum for different check modes."""

    STRICT = "STRICT"
    LENIENT = "LENIENT"
    LOOSE = "LOOSE"


def get_field_members(cls):
    return {
        name: value
        for name, value in cls.__dict__.items()
        if not isinstance(value, (FunctionType, MethodType))
    }
    
def get_callable_members(cls):
    return {
        name: value
        for name, value in cls.__dict__.items()
        if isinstance(value, (FunctionType, MethodType))
    }


def is_signature_compatible(proto_func, impl_func, *,  mode: CheckMode, class_name: str, method_name: str):
    proto_sig = inspect.signature(proto_func)
    impl_sig = inspect.signature(impl_func)
    
    proto_params = list(proto_sig.parameters.values())
    impl_params = list(impl_sig.parameters.values())
    # Check for required *args / **kwargs if present in proto
    if mode in {CheckMode.STRICT, CheckMode.LENIENT, CheckMode.LOOSE}:
        def has_kind(params, kind):
            return any(p.kind == kind for p in params)
        if has_kind(proto_params, inspect.Parameter.VAR_POSITIONAL) and not has_kind(impl_params, inspect.Parameter.VAR_POSITIONAL):
            raise TypeError("Missing *args in `{class_name}.{method_name}`")
        if has_kind(proto_params, inspect.Parameter.VAR_KEYWORD) and not has_kind(impl_params, inspect.Parameter.VAR_KEYWORD):
            raise TypeError("Missing **kwargs in `{class_name}.{method_name}`")

    proto_param_map = {p.name: p for p in proto_params}
    impl_param_map = {p.name: p for p in impl_params}

    proto_types = get_type_hints(proto_func, globalns=sys.modules[proto_func.__module__].__dict__)
    impl_types = get_type_hints(impl_func, globalns=sys.modules[impl_func.__module__].__dict__)

    for name, proto_param in proto_param_map.items():
        # Skip self/cls
        if name in ("self", "cls"):
            continue
        if mode in {CheckMode.STRICT, CheckMode.LENIENT, CheckMode.LOOSE}:
            if name not in impl_param_map:
                raise TypeError(
                    f"Missing parameter `{name}` in `{class_name}.{method_name}`."
                )
        impl_param = impl_param_map[name]
        # Check parameter kind (e.g., keyword-only, positional-only)
        if mode in {CheckMode.STRICT}:
            if proto_param.kind != impl_param.kind:
                raise TypeError(
                    f"Parameter kind mismatch for `{name}` in `{class_name}.{method_name}`:"
                    f" Expected: {proto_param.kind}"
                    f" Found: {impl_param.kind}"
                )
        # Check default values
        if mode in {CheckMode.STRICT, CheckMode.LENIENT}:
            if proto_param.default != impl_param.default:
                raise TypeError(
                    f"Default value mismatch for `{name}` in `{class_name}.{method_name}`:"
                    f" Expected: {proto_param.default}"
                    f" Found: {impl_param.default}"
                )

        # Check types
        proto_type = proto_types.get(name)
        impl_type = impl_types.get(name)
        if mode in {CheckMode.STRICT, CheckMode.LENIENT}:
            if proto_type and impl_type:
                if not safe_subtype(proto_type, 
                                    impl_type):
                    raise TypeError(
                        f"Type mismatch for `{name}` in `{class_name}.{method_name}`:"
                        f" Expected: {proto_type}"
                        f" Found: {impl_type}"
                    )
            elif proto_type is not None or impl_type is not None:
                raise TypeError(
                    f"Type mismatch for `{name}` in `{class_name}.{method_name}`:"
                    f" Expected: {proto_type}"
                    f" Found: {impl_type}"
                )
    if mode in {CheckMode.STRICT}:
        proto_type = proto_sig.return_annotation
        impl_type = impl_sig.return_annotation
        if proto_type and impl_type:
            if not safe_subtype(impl_type, proto_type):
                raise TypeError(
                    f"Return annotation mismatch in `{class_name}.{method_name}`:"
                    f" Expected: {proto_type}"
                    f" Found: {impl_type}"
                )
        elif proto_type is not None:
            raise TypeError(
                f"Return annotation mismatch in `{class_name}.{method_name}`:"
                f" Expected: {proto_type}"
                f" Found: {impl_type}"
            )
    return True



class StrictProtocol:
    mode: CheckMode = CheckMode.STRICT
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)  # Ensure other subclasses work
        # Get all methods from parent Protocol classes (via `mro()`)

        for proto_base in cls.__mro__[1:]:
            if safe_subtype(proto_base, Protocol) and not hasattr(proto_base, "__abstractmethods__"):
                # If the base class is a Protocol but not abstract, we should check the fields defined in it
                # against the fields in the current class.
                proto_fields = inspect.get_annotations(proto_base)
                impl_fields = inspect.get_annotations(cls)
                for field_name, proto_type in proto_fields.items():
                    if field_name in impl_fields:
                        impl_type = impl_fields[field_name]
                        if impl_type is not proto_type:
                            raise TypeError(
                                f"Field type mismatch for `{field_name}`:"
                                f" Expected: {proto_type}"
                                f" Found: {impl_type}"
                            )
                    else:
                        raise TypeError(f"{cls.__name__} is missing required field: `{field_name}`")
                
            elif safe_subtype(proto_base, Protocol) or hasattr(proto_base, "__abstractmethods__"):
                # If the base class is a Protocol and abstract, we should check the methods defined in it
                proto_methods = get_callable_members(proto_base)
                impl_methods = get_callable_members(cls)

                for method_name, proto_method in proto_methods.items():
                    if method_name == "__init__":  
                        # Skip __init__, this is safe as usually __init__ is not a protocol method
                        # and user temp to change the signature of __init__ and call super().__init__()
                        # in the implementation class
                        continue

                    if method_name not in impl_methods:
                        raise TypeError(f"{cls.__name__} is missing required method: `{method_name}`")

                    proto_func = inspect.unwrap(proto_method)
                    impl_func = inspect.unwrap(impl_methods[method_name])

                    if not is_signature_compatible(proto_func, 
                                                   impl_func, 
                                                   mode = kwargs.get("mode", cls.mode),
                                                   class_name=cls.__name__,
                                                   method_name=method_name):
                        raise TypeError(
                            f"Signature mismatch in `{cls.__name__}.{method_name}`:\n"
                            f"  Expected: {inspect.signature(proto_func)}\n"
                            f"  Found:    {inspect.signature(impl_func)}"
                        )


if __name__ == '__main__':
    pass
    # class P7(Protocol):
    #     def do(self, a: int, b: int, *, c: str, d: bool = False) -> None: ...

    # class OK7:
    #     def do(self, a: int, b: int, *, c: str, d: bool = False) -> None: ...


    # assert is_signature_compatible(P7.do, OK7().do, mode=CheckMode.STRICT, class_name="OK7", method_name="do")
