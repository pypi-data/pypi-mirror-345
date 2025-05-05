import inspect
from typing import get_type_hints, Protocol, Any
from types import FunctionType, MethodType
from enum import Enum
import sys
from .safe_typing import safe_subtype

class ProtocolError(TypeError):
    """Custom error for protocol violations."""
    def __init__(self, message: str, *, class_name: str, method_name:str, parameter_name:str, expected: Any, actual: Any):
        super().__init__(message)
        self.message = message
        self.class_name = class_name
        self.method_name = method_name
        self.parameter_name = parameter_name
        self.expected = expected
        self.actual = actual

    def __str__(self):
        argstr = f"(..., {self.parameter_name}, ...)" if self.parameter_name != 'N/A' else ""
        return '\n'.join([
                f"Error: {self.message} at",  
                f"{self.class_name}.{self.method_name}{argstr}",
                f"Expected: {self.expected}",
                f"Found: {self.actual}"
                ])

        

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


def get_best_effort_annotations(func):
    try:
        # Try to resolve all annotations
        return get_type_hints(func, globalns=sys.modules[func.__module__].__dict__)
    except (NameError, TypeError) as e:
        # Fallback to raw annotations if resolution fails
        print(f"Warning: get_type_hints failed: {e}")
        sig = inspect.signature(func)
        annotations = {
            name: param.annotation if param.annotation is not inspect.Parameter.empty else None
            for name, param in sig.parameters.items()
        }
        # Add return annotation if present
        if sig.return_annotation is not inspect.Signature.empty:
            annotations['return'] = sig.return_annotation
        return annotations


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
            raise ProtocolError(
                "Parameter *args not found",
                class_name=class_name,
                method_name=method_name,
                parameter_name="*args",
                expected="*args",
                actual="None"
            )
            
        if has_kind(proto_params, inspect.Parameter.VAR_KEYWORD) and not has_kind(impl_params, inspect.Parameter.VAR_KEYWORD):
            raise ProtocolError(
                "Parameter **kwargs not found",
                class_name=class_name,
                method_name=method_name,
                parameter_name="**kwargs",
                expected="**kwargs",
                actual="None"
            )
            
    proto_types = get_best_effort_annotations(proto_func)
    impl_types = get_best_effort_annotations(impl_func)

    proto_param_map = {p.name: p for p in proto_params}
    impl_param_map = {p.name: p for p in impl_params}
    for name, proto_param in proto_param_map.items():
        # Skip self/cls
        if name in ("self", "cls"):
            continue
        if mode in {CheckMode.STRICT, CheckMode.LENIENT, CheckMode.LOOSE}:
            if name not in impl_param_map:
                raise ProtocolError(
                    "Parameter not found",
                    class_name=class_name,
                    method_name=method_name,
                    parameter_name=name,
                    expected=name,
                    actual="None"
                )
        impl_param = impl_param_map[name]
        # Check parameter kind (e.g., keyword-only, positional-only)
        if mode in {CheckMode.STRICT}:
            if proto_param.kind != impl_param.kind:
                raise ProtocolError(
                    "Parameter kind mismatch",
                    class_name=class_name,
                    method_name=method_name,
                    parameter_name=name,
                    expected=proto_param.kind,
                    actual=impl_param.kind
                )
        # Check default values
        if mode in {CheckMode.STRICT, CheckMode.LENIENT}:
            if proto_param.default != impl_param.default:
                raise ProtocolError(
                    "Default value mismatch",
                    class_name=class_name,
                    method_name=method_name,
                    parameter_name=name,
                    expected=proto_param.default,
                    actual=impl_param.default
                )

        # Check types
        proto_type = proto_types.get(name) 
        impl_type = impl_types.get(name) 
        if mode in {CheckMode.STRICT, CheckMode.LENIENT}:
            if isinstance(proto_type,str) and isinstance(impl_type,str):
                if proto_type != impl_type:
                    raise ProtocolError(
                        "Parameter type mismatch",
                        class_name=class_name,
                        method_name=method_name,
                        parameter_name=name,
                        expected=proto_type,
                        actual=impl_type
                    )
            elif isinstance(proto_type, str) and not isinstance(impl_type, str):
                if proto_type != impl_type.__name__:
                    raise ProtocolError(
                        "Parameter type mismatch",
                        class_name=class_name,
                        method_name=method_name,
                        parameter_name=name,
                        expected=proto_type,
                        actual=impl_type
                    )
            elif isinstance(impl_type, str) and not isinstance(proto_type, str):
                if impl_type != proto_type.__name__:
                    raise ProtocolError(
                        "Parameter type mismatch",
                        class_name=class_name,
                        method_name=method_name,
                        parameter_name=name,
                        expected=proto_type,
                        actual=impl_type
                    )

            elif proto_type and impl_type:
                if not safe_subtype(proto_type, 
                                    impl_type):                    
                    raise ProtocolError(
                        "Parameter type mismatch",
                        class_name=class_name,
                        method_name=method_name,
                        parameter_name=name,
                        expected=proto_type,
                        actual=impl_type
                    )

            elif proto_type is not None or impl_type is not None:
                raise ProtocolError(
                    "Parameter type mismatch",
                    class_name=class_name,
                    method_name=method_name,
                    parameter_name=name,
                    expected=proto_type,
                    actual=impl_type
                )

    if mode in {CheckMode.STRICT}:
        proto_type = proto_sig.return_annotation
        impl_type = impl_sig.return_annotation
        if proto_type and impl_type:
            if not safe_subtype(impl_type, proto_type):
                raise ProtocolError(
                    "Return type mismatch",
                    class_name=class_name,
                    method_name=method_name,
                    parameter_name="return",
                    expected=proto_type,
                    actual=impl_type
                )

        elif proto_type is not None and proto_type is not Any:
            raise ProtocolError(
                "Return type mismatch",
                class_name=class_name,
                method_name=method_name,
                parameter_name="return",
                expected=proto_type,
                actual=impl_type
            )
    return True    


def check_cls(cls, mode: CheckMode = CheckMode.STRICT):
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
                        raise ProtocolError(
                            "Field type mismatch",
                            class_name=cls.__name__,
                            method_name=field_name,
                            parameter_name='N/A',
                            expected=proto_type,
                            actual=impl_type
                        )
                else:
                    raise ProtocolError(
                        "Field not found",
                        class_name=cls.__name__,
                        method_name=field_name,
                        parameter_name='N/A',
                        expected=proto_type,
                        actual="None"
                    )
                    
            
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
                    raise ProtocolError(
                        "Method not found",
                        class_name=cls.__name__,
                        method_name=method_name,
                        parameter_name='N/A',
                        expected=proto_method,
                        actual="None"
                    )

                proto_func = inspect.unwrap(proto_method)
                impl_func = inspect.unwrap(impl_methods[method_name])

                is_signature_compatible(proto_func, 
                                        impl_func, 
                                        mode = mode,
                                        class_name=cls.__name__,
                                        method_name=method_name)



class StrictProtocol:    
    def __init_subclass__(cls, *, mode: CheckMode = CheckMode.STRICT, raise_exception: bool = True, **kwargs):
        super().__init_subclass__(**kwargs)  # Ensure other subclasses work
        # Get all methods from parent Protocol classes (via `mro()`)
        try:
            check_cls(cls, mode=mode)
        except ProtocolError as e:
            if raise_exception:
                raise e
            else:
                print(e)



if __name__ == '__main__':
    pass
    # class P7(Protocol):
    #     def do(self, a: int, b: int, *, c: str, d: bool = False) -> None: ...

    # class OK7:
    #     def do(self, a: int, b: int, *, c: str, d: bool = False) -> None: ...


    # assert is_signature_compatible(P7.do, OK7().do, mode=CheckMode.STRICT, class_name="OK7", method_name="do")
