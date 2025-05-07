# (generated with --quick)

import enum
import os
import wccls.bibliocommons
from typing import Any, Callable, Optional, Type

MultCoLibBiblioCommons: Type[wccls.bibliocommons.MultCoLibBiblioCommons]
StatusType: Type[enum.Enum]
WcclsBiblioCommons: Type[wccls.bibliocommons.WcclsBiblioCommons]
environ: os._Environ[str]
mark: Any
test_multcolib: Any
test_wccls: Any

def CheckOutput(items, prefix) -> None: ...
def ScrubStrings(stringReplacementPairs) -> Callable[[Any], Any]: ...
def pformat(object: object, indent: int = ..., width: int = ..., depth: Optional[int] = ..., *, compact: bool = ..., sort_dicts: bool = ...) -> str: ...
