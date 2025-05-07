# (generated with --quick)

import dataclasses
import datetime
import enum
import os
import requests.sessions
import wccls.bibliocommons
import wccls.parser
import wccls.wccls
from typing import Callable, Type, TypeVar, Union, overload

BiblioCommons: Type[wccls.bibliocommons.BiblioCommons]
Checkout: Type[wccls.wccls.Checkout]
Enum: Type[enum.Enum]
FormatType: Type[enum.Enum]
HoldInTransit: Type[wccls.wccls.HoldInTransit]
HoldNotReady: Type[wccls.wccls.HoldNotReady]
HoldPaused: Type[wccls.wccls.HoldPaused]
HoldReady: Type[wccls.wccls.HoldReady]
Item: Type[wccls.wccls.Item]
MultCoLibBiblioCommons: Type[wccls.bibliocommons.MultCoLibBiblioCommons]
ParseError: Type[wccls.wccls.ParseError]
Parser: Type[wccls.parser.Parser]
Session: Type[requests.sessions.Session]
StatusType: Type[enum.Enum]
Wccls: Type[wccls.bibliocommons.WcclsBiblioCommons]
WcclsBiblioCommons: Type[wccls.bibliocommons.WcclsBiblioCommons]
date: Type[datetime.date]

_T = TypeVar('_T')

@overload
def dataclass(__cls: None) -> Callable[[Type[_T]], Type[_T]]: ...
@overload
def dataclass(__cls: Type[_T]) -> Type[_T]: ...
@overload
def dataclass(*, init: bool = ..., repr: bool = ..., eq: bool = ..., order: bool = ..., unsafe_hash: bool = ..., frozen: bool = ...) -> Callable[[Type[_T]], Type[_T]]: ...
def gettempdir() -> str: ...
@overload
def join(a: Union[bytes, os.PathLike[bytes]], *paths: Union[bytes, os.PathLike[bytes]]) -> bytes: ...
@overload
def join(a: Union[str, os.PathLike[str]], *paths: Union[str, os.PathLike[str]]) -> str: ...
def makedirs(name: Union[bytes, str, os.PathLike[Union[bytes, str]]], mode: int = ..., exist_ok: bool = ...) -> None: ...
