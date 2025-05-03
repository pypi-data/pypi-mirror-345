from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from abc import ABC


@dataclass
class TcBase(ABC):
    path: Path = None
    sub_paths: Optional[List[Path]] = None
    parent: Optional[object | None] = None
    name_space: Optional[str] = None
    name: Optional[str] = None

    def __post_init__(self):
        if self.sub_paths is None:
            self.sub_paths = []

    def get_identifier(self) -> str:
        _identifier:str=""
        if self.name_space is not None:
            _identifier = _identifier + self.name_space + "."
        if self.parent is not None:
            _identifier = _identifier + self.parent + "."
        if self.name is not None:
            _identifier = _identifier + self.name
        return _identifier



@dataclass
class TcDocumentation(TcBase):
    details: Optional[str] = None
    usage: Optional[str] = None
    brief: Optional[str] = None
    returns: Optional[str] = None
    custom_tags: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.custom_tags is None:
            self.custom_tags = {}
        TcBase.__post_init__(self)


@dataclass
class TcVariable(TcBase):
    type: str = ""
    initial_value: Optional[str] = None
    comment: Optional[str] = None
    attributes: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        TcBase.__post_init__(self)


@dataclass
class TcVariableSection(TcBase):
    section_type: str = (
        ""  # VAR, VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT, VAR_STAT, VAR CONSTANT
    )
    variables: List[TcVariable] = None

    def __post_init__(self):
        if self.variables is None:
            self.variables = []
        TcBase.__post_init__(self)


@dataclass
class TcGet(TcBase):
    declaration: str = ""
    implementation: str = ""


@dataclass
class TcSet(TcBase):
    declaration: str = ""
    implementation: str = ""


@dataclass
class TcMethod(TcBase):
    accessModifier: Optional[str] = None
    returnType: Optional[str] = None
    declaration: str = ""
    implementation: str = ""
    variable_sections: Optional[List[TcVariableSection]] = None
    documentation: Optional[TcDocumentation] = None

    def __post_init__(self):
        if self.variable_sections is None:
            self.variable_sections = []
        TcBase.__post_init__(self)


@dataclass
class TcProperty(TcBase):
    returnType: Optional[str] = None
    get: Optional[TcGet] = None
    set: Optional[TcSet] = None


@dataclass
class TcPou(TcBase):
    implements: Optional[list[str]] = None
    extends: Optional[str] = None
    declaration: str = ""
    implementation: str = ""

    methods: Optional[list[TcMethod]] = None
    properties: Optional[list[TcProperty]] = None
    variable_sections: Optional[List[TcVariableSection]] = None
    documentation: Optional[TcDocumentation] = None

    def __post_init__(self):
        if self.implements is None:
            self.implements = []
        if self.methods is None:
            self.methods = []
        if self.properties is None:
            self.properties = []
        if self.variable_sections is None:
            self.variable_sections = []
        TcBase.__post_init__(self)


@dataclass
class TcItf(TcBase):
    extends: Optional[list[str]] = None

    methods: Optional[list[TcMethod]] = None
    properties: Optional[list[TcProperty]] = None

    def __post_init__(self):
        if self.extends is None:
            self.extends = []
        if self.methods is None:
            self.methods = []
        if self.properties is None:
            self.properties = []
        TcBase.__post_init__(self)


@dataclass
class TcDut(TcBase):
    declaration: str = ""
    variable_sections: Optional[List[TcVariableSection]] = None
    documentation: Optional[TcDocumentation] = None

    def __post_init__(self):
        if self.variable_sections is None:
            self.variable_sections = []
        TcBase.__post_init__(self)


@dataclass
class TcPlcProject(TcBase):
    """Represents a plc project in a TwinCAT solution."""

    default_namespace: str = ""
    version: str = ""
    object_paths: Optional[List[Path]] = None

    def __post_init__(self):
        if self.object_paths is None:
            self.object_paths = []
        TcBase.__post_init__(self)

    def get_identifier(self) -> str:
        return self.name





@dataclass
class TcProject(TcBase):
    """Represents a project in a TwinCAT solution."""


@dataclass
class TcSolution(TcBase):
    """Represents a TwinCAT solution with its projects."""

    _projects: List[TcProject] = None

    def __post_init__(self):
        if self._projects is None:
            self._projects = []
        TcBase.__post_init__(self)


TcObjects = TcBase
