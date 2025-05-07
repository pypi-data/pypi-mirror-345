# (generated with --quick)

import os
import requests.sessions
import wccls.parser
import wccls.wccls
from typing import Annotated, Any, List, Type, Union, overload

Item: Type[wccls.wccls.Item]
ParseError: Type[wccls.wccls.ParseError]
Parser: Type[wccls.parser.Parser]
Session: Type[requests.sessions.Session]

class BiblioCommons:
    _debug: bool
    _parser: wccls.parser.Parser
    items: Annotated[List[wccls.wccls.Item], 'property']
    def _DoRequest(self, session, request) -> Any: ...
    def _DumpDebugFile(self, filename, text) -> None: ...
    def __init__(self, subdomain: str, login: str, password: str, debug_: bool = ...) -> None: ...

class MultCoLibBiblioCommons(BiblioCommons):
    _debug: bool
    _parser: wccls.parser.Parser
    def __init__(self, login: str, password: str, debug_: bool = ...) -> None: ...

class WcclsBiblioCommons(BiblioCommons):
    _debug: bool
    _parser: wccls.parser.Parser
    def __init__(self, login: str, password: str, debug_: bool = ...) -> None: ...

def gettempdir() -> str: ...
@overload
def join(a: Union[bytes, os.PathLike[bytes]], *paths: Union[bytes, os.PathLike[bytes]]) -> bytes: ...
@overload
def join(a: Union[str, os.PathLike[str]], *paths: Union[str, os.PathLike[str]]) -> str: ...
def makedirs(name: Union[bytes, str, os.PathLike[Union[bytes, str]]], mode: int = ..., exist_ok: bool = ...) -> None: ...
