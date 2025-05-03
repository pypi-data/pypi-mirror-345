import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from .BaseStrategy import BaseStrategy
from .Loader import add_strategy
from .TwincatObjects.tc_plc_object import (
    Dut,
    Get,
    Itf,
    Method,
    Pou,
    Property,
    Set,
    TcPlcObject,
)
from .TwincatObjects.tc_plc_project import Compile, Project
from .TwincatDataclasses import (
    TcDocumentation,
    TcDut,
    TcGet,
    TcItf,
    TcMethod,
    TcObjects,
    TcPlcProject,
    TcPou,
    TcProperty,
    TcSet,
    TcVariable,
    TcVariableSection,
)

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.parsers.config import ParserConfig

logger = logging.getLogger(__name__)


def parse_documentation(declaration: str) -> Optional[TcDocumentation]:
    """
    Parse documentation comments from a declaration string.

    Args:
        declaration: The declaration string containing documentation comments.

    Returns:
        A TcDocumentation object or None if no documentation is found.
    """
    if not declaration:
        return None

    # Extract only the part before the first variable block
    var_pattern = re.compile(
        r"VAR(?:_INPUT|_OUTPUT|_IN_OUT|_INST|_STAT|[ ]CONSTANT)?", re.DOTALL
    )
    struct_pattern = re.compile(r"STRUCT", re.DOTALL)

    # Find the position of the first variable block
    var_match = var_pattern.search(declaration)
    struct_match = struct_pattern.search(declaration)

    # Determine the end position of the documentation block
    end_pos = len(declaration)
    if var_match:
        end_pos = min(end_pos, var_match.start())
    if struct_match:
        end_pos = min(end_pos, struct_match.start())

    # Extract only the part before the first variable block
    doc_part = declaration[:end_pos]

    # Define regex patterns for different comment styles
    # 1. Multi-line comment: (* ... *)
    # 2. Single-line comment: // ...
    # 3. Multi-line comment with stars: (*** ... ***)
    multiline_comment_pattern = re.compile(r"\(\*\s*(.*?)\s*\*\)", re.DOTALL)
    singleline_comment_pattern = re.compile(r"//\s*(.*?)$", re.MULTILINE)

    # Extract all comments
    comments = []

    # Check for multi-line comments
    for match in multiline_comment_pattern.finditer(doc_part):
        comments.append(match.group(1).strip())

    # Check for single-line comments
    single_line_comments = []
    for match in singleline_comment_pattern.finditer(doc_part):
        single_line_comments.append(match.group(1).strip())

    if single_line_comments:
        comments.append("\n".join(single_line_comments))

    if not comments:
        return None

    # Join all comments
    comment_text = "\n".join(comments)

    # Parse documentation tags
    doc = TcDocumentation()

    # Define regex patterns for documentation tags
    details_pattern = re.compile(r"@details\s*(.*?)(?=@\w+|\Z)", re.DOTALL)
    usage_pattern = re.compile(r"@usage\s*(.*?)(?=@\w+|\Z)", re.DOTALL)
    returns_pattern = re.compile(r"@return\s*(.*?)(?=@\w+|\Z)", re.DOTALL)
    custom_tag_pattern = re.compile(r"@(\w+)\s*(.*?)(?=@\w+|\Z)", re.DOTALL)

    # Helper function to clean up tag content
    def clean_tag_content(content):
        if content:
            # Remove lines that are just asterisks
            content = re.sub(r"^\s*\*+\s*$", "", content, flags=re.MULTILINE)
            # Remove trailing asterisks and whitespace
            content = re.sub(r"\s*\*+\s*$", "", content)
            # Remove leading asterisks and whitespace from each line
            content = re.sub(r"^\s*\*+\s*", "", content, flags=re.MULTILINE)
            # Remove leading and trailing whitespace
            content = content.strip()
            # Replace multiple whitespace with a single space
            content = re.sub(r"\s+", " ", content)
        return content

    # Extract details
    details_match = details_pattern.search(comment_text)
    if details_match:
        doc.details = clean_tag_content(details_match.group(1))

    # Extract usage
    usage_match = usage_pattern.search(comment_text)
    if usage_match:
        doc.usage = clean_tag_content(usage_match.group(1))

    # Extract returns
    returns_match = returns_pattern.search(comment_text)
    if returns_match:
        doc.returns = clean_tag_content(returns_match.group(1))

    # Extract custom tags
    for match in custom_tag_pattern.finditer(comment_text):
        tag_name = match.group(1)
        tag_value = clean_tag_content(match.group(2))
        if tag_name not in ["details", "usage", "return"]:
            doc.custom_tags[tag_name] = tag_value

    return doc


def parse_variable_sections(declaration: str) -> List[TcVariableSection]:
    """
    Parse variable sections from a declaration string.

    Args:
        declaration: The declaration string containing variable sections.

    Returns:
        A list of TcVariableSection objects.
    """
    if not declaration:
        return []

    # Define regex patterns
    section_pattern = re.compile(
        r"(VAR(?:_INPUT|_OUTPUT|_IN_OUT|_INST|_STAT|[ ]CONSTANT)?)\s*(.*?)END_VAR",
        re.DOTALL,
    )
    struct_pattern = re.compile(r"STRUCT\s*(.*?)END_STRUCT", re.DOTALL)
    attribute_pattern = re.compile(
        r"\{attribute\s+\'([^\']+)\'\s*(?:\:=\s*\'([^\']*)\')?\}"
    )
    comment_pattern = re.compile(
        r"(?://(.*)$)|(?:\(\*\s*(.*?)\s*\*\))|(?:\(\*\*\*(.*?)\*\*\*\))",
        re.MULTILINE | re.DOTALL,
    )

    # Find all variable sections
    sections = []

    # Process VAR sections
    for section_match in section_pattern.finditer(declaration):
        section_type = section_match.group(1).strip()
        section_content = section_match.group(2).strip()

        # Create a new section
        section = TcVariableSection(section_type=section_type)

        # Split the section content into lines
        lines = section_content.split("\n")

        # Process each line
        current_var = None
        current_attributes = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for attribute
            attr_match = attribute_pattern.search(line)
            if attr_match:
                attr_name = attr_match.group(1)
                attr_value = attr_match.group(2) if attr_match.group(2) else ""
                current_attributes[attr_name] = attr_value
                continue

            # Check for variable declaration
            if ":" in line:
                # If we have a previous variable, add it to the section
                if current_var:
                    section.variables.append(current_var)

                # Parse the new variable
                var_parts = line.split(":", 1)
                var_name = var_parts[0].strip()

                # Extract comment if present
                var_comment = None
                comment_match = comment_pattern.search(line)
                if comment_match:
                    # Get the first non-None group
                    for group in comment_match.groups():
                        if group:
                            var_comment = group.strip()
                            break

                # Remove comment from line for further processing
                if comment_match:
                    line = line[: comment_match.start()].strip()

                # Parse type and initial value
                type_value_parts = var_parts[1].strip()
                if ";" in type_value_parts:
                    type_value_parts = type_value_parts.rstrip(";")

                var_type = type_value_parts
                var_initial_value = None

                # Check for initial value
                if ":=" in type_value_parts:
                    type_init_parts = type_value_parts.split(":=", 1)
                    var_type = type_init_parts[0].strip()
                    var_initial_value = type_init_parts[1].strip()

                # Create the variable
                current_var = TcVariable(
                    name=var_name,
                    type=var_type,
                    initial_value=var_initial_value,
                    comment=var_comment,
                    attributes=current_attributes if current_attributes else None,
                )

                # Reset attributes for the next variable
                current_attributes = {}

        # Add the last variable if there is one
        if current_var:
            section.variables.append(current_var)

        # Add the section to the list
        sections.append(section)

    # Process STRUCT sections for DUTs
    for struct_match in struct_pattern.finditer(declaration):
        struct_content = struct_match.group(1).strip()

        # Create a new section for the struct
        section = TcVariableSection(section_type="STRUCT")

        # Split the struct content into lines
        lines = struct_content.split("\n")

        # Process each line
        current_var = None
        current_attributes = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for attribute
            attr_match = attribute_pattern.search(line)
            if attr_match:
                attr_name = attr_match.group(1)
                attr_value = attr_match.group(2) if attr_match.group(2) else ""
                current_attributes[attr_name] = attr_value
                continue

            # Check for variable declaration
            if ":" in line:
                # If we have a previous variable, add it to the section
                if current_var:
                    section.variables.append(current_var)

                # Parse the new variable
                var_parts = line.split(":", 1)
                var_name = var_parts[0].strip()

                # Extract comment if present
                var_comment = None
                comment_match = comment_pattern.search(line)
                if comment_match:
                    # Get the first non-None group
                    for group in comment_match.groups():
                        if group:
                            var_comment = group.strip()
                            break

                # Remove comment from line for further processing
                if comment_match:
                    line = line[: comment_match.start()].strip()

                # Parse type and initial value
                type_value_parts = var_parts[1].strip()
                if ";" in type_value_parts:
                    type_value_parts = type_value_parts.rstrip(";")

                var_type = type_value_parts
                var_initial_value = None

                # Check for initial value
                if ":=" in type_value_parts:
                    type_init_parts = type_value_parts.split(":=", 1)
                    var_type = type_init_parts[0].strip()
                    var_initial_value = type_init_parts[1].strip()

                # Create the variable
                current_var = TcVariable(
                    name=var_name,
                    type=var_type,
                    initial_value=var_initial_value,
                    comment=var_comment,
                    attributes=current_attributes if current_attributes else None,
                )

                # Reset attributes for the next variable
                current_attributes = {}

        # Add the last variable if there is one
        if current_var:
            section.variables.append(current_var)

        # Add the section to the list if it has variables
        if section.variables:
            sections.append(section)

    return sections


def load_method(method: Method):
    if method is None:
        return None

    # Extract implementation text
    implementation_text = ""
    if hasattr(method.implementation, "st"):
        implementation_text = method.implementation.st

    # Parse access modifier and return type from declaration
    accessModifier = None
    returnType = None
    variable_sections = []
    documentation = None

    if method.declaration:
        declaration_lines = method.declaration.strip().split("\n")
        if declaration_lines:
            first_line = declaration_lines[0].strip()
            # Look for METHOD [MODIFIER] name : return_type;
            if first_line.startswith("METHOD "):
                # Check for return type after colon
                if ":" in first_line:
                    # Split by colon and get the part after it
                    return_part = first_line.split(":", 1)[1].strip()
                    # Remove trailing semicolon if present
                    if return_part.endswith(";"):
                        return_part = return_part[:-1].strip()
                    returnType = return_part

                # Check for access modifier
                parts = first_line.split(" ")
                if len(parts) >= 3:
                    # Check if the second part is an access modifier
                    possible_modifier = parts[1].upper()
                    if possible_modifier in [
                        "PROTECTED",
                        "PRIVATE",
                        "INTERNAL",
                        "PUBLIC",
                    ]:
                        accessModifier = possible_modifier

        # Parse variable sections
        variable_sections = parse_variable_sections(method.declaration)

        # Parse documentation
        documentation = parse_documentation(method.declaration)

    return TcMethod(
        name=method.name,
        accessModifier=accessModifier,
        returnType=returnType,
        declaration=method.declaration,
        implementation=implementation_text,
        variable_sections=variable_sections,
        documentation=documentation,
    )


def load_property(property: Property):
    if property is None:
        return None

    # Parse return type from declaration
    returnType = None
    if property.declaration:
        declaration_lines = property.declaration.strip().split("\n")
        if declaration_lines:
            first_line = declaration_lines[0].strip()
            # Look for PROPERTY name : return_type
            if first_line.startswith("PROPERTY "):
                # Check for return type after colon
                if ":" in first_line:
                    # Split by colon and get the part after it
                    return_part = first_line.split(":", 1)[1].strip()
                    returnType = return_part

    return TcProperty(
        name=property.name,
        returnType=returnType,
        get=load_get_property(get=property.get),
        set=load_set_property(set=property.set),
    )


def load_get_property(get: Get):
    if get is None:
        return None

    # Extract implementation text
    implementation_text = ""
    if hasattr(get.implementation, "st"):
        implementation_text = get.implementation.st

    return TcGet(
        name=get.name, declaration=get.declaration, implementation=implementation_text
    )


def load_set_property(set: Set):
    if set is None:
        return None

    # Extract implementation text
    implementation_text = ""
    if hasattr(set.implementation, "st"):
        implementation_text = set.implementation.st

    return TcSet(
        name=set.name, declaration=set.declaration, implementation=implementation_text
    )


class FileHandler(ABC):
    def __init__(self, suffix):
        self.suffix: str = suffix.lower()
        self.config = ParserConfig(fail_on_unknown_properties=False)
        self.parser = XmlParser(config=self.config)
        super().__init__()

    @abstractmethod
    def load_object(self, path: Path) -> TcObjects:
        raise NotImplementedError()


class SolutionHandler(FileHandler):
    def __init__(self):
        super().__init__(suffix=".sln")

    def load_object(self, path):
        raise NotImplementedError("SolutionFileHandler not implemented")


class TwincatProjectHandler(FileHandler):
    def __init__(self):
        super().__init__(suffix=".tsproj")

    def load_object(self, path):
        raise NotImplementedError("TwincatProjectHandler not implemented")


class XtiHandler(FileHandler):
    def __init__(self):
        super().__init__(suffix=".xti")

    def load_object(self, path):
        raise NotImplementedError("XtiHandler not implemented")


class PlcProjectHandler(FileHandler):
    def __init__(self):
        super().__init__(suffix=".plcproj")

    def load_object(self, path):
        _prj: Project = self.parser.parse(path, Project)
        if _prj is None:
            return None

        object_paths: List[Path] = []
        compile_elements: List[Compile] = []
        for object in _prj.item_group:
            for elem in object.compile:
                if not elem.exclude_from_build:
                    compile_elements.append(elem)

        for elem in compile_elements:
            object_paths.append((path.parent / Path(elem.include)).resolve())

        return TcPlcProject(
            name=_prj.property_group.name,
            path=path.resolve(),
            default_namespace=_prj.property_group.default_namespace,
            name_space=_prj.property_group.default_namespace,
            version=_prj.property_group.project_version,
            object_paths=object_paths,
            sub_paths=object_paths,
        )


class TcPouHandler(FileHandler):
    def __init__(self):
        super().__init__(suffix=".tcpou")

    def load_object(self, path):
        _pou: Pou = self.parser.parse(path, TcPlcObject).pou
        if _pou is None:
            return None

        # Extract implementation text
        implementation_text = ""
        if hasattr(_pou.implementation, "st"):
            implementation_text = _pou.implementation.st

        properties = []
        if hasattr(_pou, "property") and _pou.property:
            properties = [load_property(property=prop) for prop in _pou.property]

        methods = []
        if hasattr(_pou, "method") and _pou.method:
            methods = [load_method(method=meth) for meth in _pou.method]

        # Parse extends and implements from declaration
        extends = None
        implements = None
        variable_sections = []

        if _pou.declaration:
            declaration_lines = _pou.declaration.strip().split("\n")
            if declaration_lines:
                first_line = declaration_lines[0].strip()

                # Check for EXTENDS
                if " EXTENDS " in first_line:
                    # Extract the part after EXTENDS
                    extends_part = first_line.split(" EXTENDS ")[1]
                    # If there's an IMPLEMENTS part, remove it
                    if " IMPLEMENTS " in extends_part:
                        extends_part = extends_part.split(" IMPLEMENTS ")[0]
                    extends = extends_part.strip()

                # Check for IMPLEMENTS
                if " IMPLEMENTS " in first_line:
                    # Extract the part after IMPLEMENTS
                    implements_part = first_line.split(" IMPLEMENTS ")[1]
                    # Split by comma to get multiple interfaces
                    implements = [
                        interface.strip() for interface in implements_part.split(",")
                    ]

            # Parse variable sections
            variable_sections = parse_variable_sections(_pou.declaration)

            # Parse documentation
            documentation = parse_documentation(_pou.declaration)

        return TcPou(
            name=_pou.name,
            path=path.resolve(),
            declaration=_pou.declaration,
            implementation=implementation_text,
            properties=properties,
            methods=methods,
            extends=extends,
            implements=implements,
            variable_sections=variable_sections,
            documentation=documentation,
        )


class TcItfHandler(FileHandler):
    def __init__(self):
        super().__init__(suffix=".tcitf")

    def load_object(self, path):
        _itf: Itf = self.parser.parse(path, TcPlcObject).itf
        if _itf is None:
            return None

        properties = []
        if hasattr(_itf, "property") and _itf.property:
            properties = [load_property(property = prop) for prop in _itf.property]

        methods = []
        if hasattr(_itf, "method") and _itf.method:
            methods = [load_method(method=meth) for meth in _itf.method]

        # Parse extends from declaration
        extends = None

        if _itf.declaration:
            declaration_lines = _itf.declaration.strip().split("\n")
            if declaration_lines:
                first_line = declaration_lines[0].strip()

                # Check for EXTENDS
                if " Extends " in first_line or " EXTENDS " in first_line:
                    # Extract the part after EXTENDS (case insensitive)
                    if " Extends " in first_line:
                        extends_part = first_line.split(" Extends ")[1]
                    else:
                        extends_part = first_line.split(" EXTENDS ")[1]

                    # Split by comma to get multiple interfaces
                    extends = [
                        interface.strip() for interface in extends_part.split(",")
                    ]

        return TcItf(
            name=_itf.name,
            path=path.resolve(),
            properties=properties,
            methods=methods,
            extends=extends,
        )


class TcDutHandler(FileHandler):
    def __init__(self):
        super().__init__(suffix=".tcdut")

    def load_object(self, path):
        _dut: Dut = self.parser.parse(path, TcPlcObject).dut
        if _dut is None:
            return None

        variable_sections = []
        documentation = None
        if _dut.declaration:
            # Parse variable sections
            variable_sections = parse_variable_sections(_dut.declaration)

            # Parse documentation
            documentation = parse_documentation(_dut.declaration)

        return TcDut(
            name=_dut.name,
            path=path.resolve(),
            declaration=_dut.declaration,
            variable_sections=variable_sections,
            documentation=documentation,
        )


_handler: List[FileHandler] = []


def add_handler(handler: FileHandler):
    _handler.append(handler)


def get_handler(suffix: str) -> FileHandler:
    for handler in _handler:
        if handler.suffix == suffix.lower():
            return handler
    raise Exception(f"Handler for suffix:  {handler.suffix} not found. Registered Handlers: {', '.join(x.suffix for x in _handler)}")


add_handler(handler=SolutionHandler())
add_handler(handler=TwincatProjectHandler())
add_handler(handler=XtiHandler())
add_handler(handler=PlcProjectHandler())
add_handler(handler=TcPouHandler())
add_handler(handler=TcItfHandler())
add_handler(handler=TcDutHandler())


class Twincat4024Strategy(BaseStrategy):
    def check_strategy(self, path: Path):
        for handler in _handler:
            if path.suffix == handler.suffix:
                return True

    def _load_tc_object(self, path: Path) -> TcObjects:
        _path = Path(path)
        handler = get_handler(suffix=_path.suffix)
        return handler.load_object(path)

    def _load_all_sub_objects(self, tcObject: TcObjects, datastore: List[TcObjects]):
        for sub_path in tcObject.sub_paths:
            sub_obj = self._load_tc_object(sub_path)
            sub_obj.parent = tcObject
            if tcObject.name_space is not None:
                sub_obj.name_space = tcObject.name_space
            datastore.append(sub_obj)
            self._load_all_sub_objects(tcObject=sub_obj, datastore=datastore)

    def load_objects(self, path):
        datastore: List[TcObjects] = []
        obj: TcObjects = None
        obj = self._load_tc_object(path=path)
        datastore.append(obj)
        self._load_all_sub_objects(tcObject=obj, datastore=datastore)

        return datastore


# present the strategy to the loader
add_strategy(Twincat4024Strategy)


if __name__ == "__main__":
    strategy = Twincat4024Strategy()

    print(strategy.load_objects(Path("TwincatFiles\Base\FB_Base.TcPOU")))
    print(strategy.load_objects(Path("TwincatFiles\Commands\ST_PmlCommand.TcDUT")))
    print(strategy.load_objects(Path("TwincatFiles\TwincatPlcProject.plcproj")))
