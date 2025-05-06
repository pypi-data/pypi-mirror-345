import pytest
from typing import Protocol, Optional, Any, List, Callable, Union, Tuple, Type
from strictprotocol import StrictProtocol, is_signature_compatible, CheckMode, ProtocolError

# --- Valid Implementation ---

class X(Protocol):
    pass
class Y(StrictProtocol, X, raise_exception=False):
    pass

def test_valid_signature_match():
    class P(Protocol):
        def do(self, x: int) -> str: ...

    class Impl(StrictProtocol, P):
        def do(self, x: int) -> str:
            return str(x)

    impl = Impl()
    assert impl.do(42) == "42"

# --- Missing Method ---

def test_missing_method_raises():
    class P(Protocol):
        def do(self) -> None: ...

    with pytest.raises(ProtocolError, match="Error: Method not found"):
        class Impl(StrictProtocol, P):
            def other(self) -> None:
                pass

def test_warning_mode(capsys):
    class P(Protocol):
        def do(self) -> None: ...

    class Impl(StrictProtocol, P, raise_exception=False):
        def other(self) -> None:
            pass
    out = capsys.readouterr().out
    assert "Error: Method not found" in out

# --- Signature Mismatch ---

def test_signature_mismatch_raises():
    class P(Protocol):
        def do(self, x: int) -> str: ...

    with pytest.raises(ProtocolError, match="Error: Parameter type mismatch"):
        class Impl(StrictProtocol, P):
            def do(self, x):  # missing return annotation
                return str(x)

def test_signature_mismatch_raises2():
    class P(Protocol):
        def do(self, x: int) -> str: ...

    with pytest.raises(ProtocolError, match="Error: Parameter type mismatch"):
        class Impl(StrictProtocol, P):
            def do(self, x)->str:  # missing return annotation
                return str(x)



# --- Extra Method Allowed ---

def test_extra_methods_allowed():
    class P(Protocol):
        def foo(self) -> int: ...

    class Impl(StrictProtocol, P):
        def foo(self) -> int:
            return 1

        def bar(self):  # extra method
            return "extra"

    assert Impl().foo() == 1
    assert Impl().bar() == "extra"


# --- Case 1: keyword-only ---
class P1(Protocol):
    def m(self, a: int, *, b: str) -> None: ...

class OK1:
    def m(self, a: int, *, b: str) -> None: ...


def test_keyword_only_pass():
    assert is_signature_compatible(P1.m, OK1().m, mode=CheckMode.STRICT, class_name="OK1", method_name="m")


def test_keyword_only_fail():
    class Bad:
        def m(self, a: int, b: str) -> None: ...
    with pytest.raises(ProtocolError):
        is_signature_compatible(P1.m, Bad().m, mode=CheckMode.STRICT, class_name="Bad", method_name="m")


# --- Case 2: missing *args ---
class P2(Protocol):
    def f(self, *args: int) -> None: ...

class OK2:
    def f(self, *args: int) -> None: ...


def test_args_pass():
    assert is_signature_compatible(P2.f, OK2().f, mode=CheckMode.STRICT, class_name="OK2", method_name="f")


def test_args_fail():
    class Bad:
        def f(self) -> None: ...
    with pytest.raises(ProtocolError):
        is_signature_compatible(P2.f, Bad().f, mode=CheckMode.STRICT, class_name="Bad", method_name="f")


# --- Case 3: type mismatch ---
class P3(Protocol):
    def g(self, x: int) -> None: ...

class OK3:
    def g(self, x: int) -> None: ...


def test_type_pass():
    assert is_signature_compatible(P3.g, OK3().g, mode=CheckMode.STRICT, class_name="OK3", method_name="g")


def test_type_fail():
    class Bad:
        def g(self, x: str) -> None: ...
    with pytest.raises(ProtocolError):
        is_signature_compatible(P3.g, Bad().g, mode = CheckMode.STRICT, class_name="Bad", method_name="g")


# --- Case 4: default mismatch ---
class P4(Protocol):
    def h(self, x: int = 10) -> None: ...

class OK4:
    def h(self, x: int = 10) -> None: ...


def test_default_pass():
    assert is_signature_compatible(P4.h, OK4().h, mode = CheckMode.STRICT, class_name="OK4", method_name="h")


def test_default_fail():
    class Bad:
        def h(self, x: int) -> None: ...
    with pytest.raises(ProtocolError):
        is_signature_compatible(P4.h, Bad().h, mode=CheckMode.STRICT, class_name="Bad", method_name="h")


# --- Case 5: missing **kwargs ---
class P5(Protocol):
    def x(self, **kwargs: str) -> None: ...

class OK5:
    def x(self, **kwargs: str) -> None: ...


def test_kwargs_pass():
    assert is_signature_compatible(P5.x, OK5().x, mode=CheckMode.STRICT, class_name="OK5", method_name="x")


def test_kwargs_fail():
    class Bad:
        def x(self) -> None: ...
    with pytest.raises(ProtocolError):
        is_signature_compatible(P5.x, Bad().x, mode=CheckMode.STRICT, class_name="Bad", method_name="x")


# --- Case 6: *args + **kwargs ---
class P6(Protocol):
    def do(self, *args: int, **kwargs: str) -> None: ...

class OK6:
    def do(self, *args: int, **kwargs: str) -> None: ...


def test_args_kwargs_pass():
    assert is_signature_compatible(P6.do, OK6().do, mode=CheckMode.STRICT, class_name="OK6", method_name="do")


def test_args_kwargs_fail():
    class Bad:
        def do(self, x: int) -> None: ...
    with pytest.raises(ProtocolError):
        is_signature_compatible(P6.do, Bad().do, mode=CheckMode.STRICT, class_name="Bad", method_name="do")


# --- Case 7: mixed kinds (positional + keyword-only) ---
class P7(Protocol):
    def do(self, a: int, b: int, *, c: str, d: bool = False) -> None: ...

class OK7:
    def do(self, a: int, b: int, *, c: str, d: bool = False) -> None: ...


def test_mixed_kinds_pass():
    assert is_signature_compatible(P7.do, OK7().do, mode=CheckMode.STRICT, class_name="OK7", method_name="do")


def test_mixed_kinds_fail():
    class Bad:
        def do(self, a: int, b: int, c: str, d: bool = False) -> None: ...
        # `c` should be keyword-only
    with pytest.raises(ProtocolError):
        is_signature_compatible(P7.do, Bad().do, mode=CheckMode.STRICT, class_name="Bad", method_name="do")



EntryFilterType = Union[
    Type[Any], 
    Callable[[Any], bool],
    Tuple[Union['NOT', 'AND', 'OR', 'XOR'], ...]
]

class Entry:
    pass
class NOT:
    pass
class AND:
    pass
class OR:
    pass
class XOR:
    pass

class ContainerProtocol(Protocol):
    def put(self, item: Any, **tags) -> Optional[Entry]:
        raise NotImplementedError

    def find(self, types: Optional[EntryFilterType] = None, **tags) -> List[Entry]:
        raise NotImplementedError

    def resolve(self, types: EntryFilterType, scopes: dict = {}, tags: dict = {}, *args, **kwargs) -> Any:
        raise NotImplementedError


def test_optional_args():

    class RootContainer(StrictProtocol, ContainerProtocol):
        def put(self, item: Any, **tags)-> Optional[Entry]:
            return None
            
        def find(self, types: Optional[EntryFilterType] = None, **tags) -> List[Entry]:
            return []

        def resolve(self, types: EntryFilterType, scopes: dict = {}, tags: dict = {},  *args, **kwargs) -> Any:
            pass