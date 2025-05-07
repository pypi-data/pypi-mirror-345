# (generated with --quick)

import dataclasses
import datetime
import enum
from typing import Annotated, Callable, Dict, Optional, Type, TypeVar, Union, overload

Enum: Type[enum.Enum]
FormatType: Type[enum.Enum]
StatusType: Type[enum.Enum]
date: Type[datetime.date]

_T = TypeVar('_T')

@dataclasses.dataclass
class Checkout(Item):
    dueDate: datetime.date
    renewals: int
    __dataclass_fields__: Dict[str, dataclasses.Field[Union[int, str, datetime.date, enum.Enum]]]
    renewable: Annotated[bool, 'property']
    def __init__(self, title: str, isDigital: bool, format: enum.Enum, dueDate: datetime.date, renewals: int) -> None: ...

@dataclasses.dataclass
class HoldInTransit(Item):
    __dataclass_fields__: Dict[str, dataclasses.Field[Union[bool, str, enum.Enum]]]
    __doc__: str
    def __init__(self, title: str, isDigital: bool, format: enum.Enum) -> None: ...

@dataclasses.dataclass
class HoldNotReady(Item):
    expiryDate: datetime.date
    queuePosition: int
    queueSize: Optional[int]
    copies: int
    __dataclass_fields__: Dict[str, dataclasses.Field[Optional[Union[int, str, datetime.date, enum.Enum]]]]
    __doc__: str
    def __init__(self, title: str, isDigital: bool, format: enum.Enum, expiryDate: datetime.date, queuePosition: int, queueSize: Optional[int], copies: int) -> None: ...

@dataclasses.dataclass
class HoldPaused(Item):
    reactivationDate: datetime.date
    __dataclass_fields__: Dict[str, dataclasses.Field[Union[bool, str, datetime.date, enum.Enum]]]
    def __init__(self, title: str, isDigital: bool, format: enum.Enum, reactivationDate: datetime.date) -> None: ...

@dataclasses.dataclass
class HoldReady(Item):
    expiryDate: datetime.date
    __dataclass_fields__: Dict[str, dataclasses.Field[Union[bool, str, datetime.date, enum.Enum]]]
    __doc__: str
    def __init__(self, title: str, isDigital: bool, format: enum.Enum, expiryDate: datetime.date) -> None: ...

@dataclasses.dataclass
class Item:
    title: str
    isDigital: bool
    format: enum.Enum
    __dataclass_fields__: Dict[str, dataclasses.Field[Union[bool, str, enum.Enum]]]
    status: Annotated[enum.Enum, 'property']
    def __init__(self, title: str, isDigital: bool, format: enum.Enum) -> None: ...
    def __init_subclass__(cls, *args, **kwargs) -> None: ...

class ParseError(Exception): ...

def _AddStatusType(name) -> None: ...
@overload
def dataclass(__cls: None) -> Callable[[Type[_T]], Type[_T]]: ...
@overload
def dataclass(__cls: Type[_T]) -> Type[_T]: ...
@overload
def dataclass(*, init: bool = ..., repr: bool = ..., eq: bool = ..., order: bool = ..., unsafe_hash: bool = ..., frozen: bool = ...) -> Callable[[Type[_T]], Type[_T]]: ...
