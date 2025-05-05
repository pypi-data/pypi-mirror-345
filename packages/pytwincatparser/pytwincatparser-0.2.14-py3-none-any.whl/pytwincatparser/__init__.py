"""
pytwincatparser - A Python package for parsing TwinCAT PLC files using xsdata.
"""

from .TwincatDataclasses import (
    TcPou,
    TcDut,
    TcItf,
    TcMethod,
    TcProperty,
    TcGet,
    TcSet,
    TcVariable,
    TcVariableSection,
    TcDocumentation,
    TcObjects,
    TcSolution,
    TcPlcProject
)
from .Loader import add_strategy, Loader, get_default_strategy, get_strategy, get_strategy_by_object_path
from .Twincat4024Strategy import Twincat4024Strategy
from .BaseStrategy import BaseStrategy

__version__ = "0.1.1"
__all__ = [
    "TcPou",
    "TcDut",
    "TcItf",
    "TcMethod",
    "TcProperty",
    "TcGet",
    "TcSet",
    "TcVariable",
    "TcVariableSection",
    "TcDocumentation",
    "TcObjects",
    "TcSolution",
    "TcPlcProject",
    "add_strategy",
    "Twincat4024Strategy",
    "BaseStrategy",
    "Loader",
    "get_default_strategy", 
    "get_strategy", 
    "get_strategy_by_object_path"
]
