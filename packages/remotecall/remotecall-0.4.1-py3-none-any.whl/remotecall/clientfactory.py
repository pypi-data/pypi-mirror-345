import typing
from typing import Optional
from typing import Any


def return_annotation_to_str(annotation: list[str]) -> str:
    if not annotation:
        return " -> None"
    if len(annotation) == 1:
        return f" -> {annotation[0]}"
    return f" -> typing.Union[{', '.join(annotation)}]"


def parameter_annotation_to_str(annotation: list[str], optional: bool) -> str:
    if optional:
        return f": typing.Optional[{annotation[0]}]"
    if len(annotation) == 1:
        return f": {annotation[0]}"
    return f": typing.Union[{', '.join(annotation)}]"


def default_parameter_value_to_str(
    value: typing.Union[str, None], annotation: list[str]
) -> str:
    if value is None:
        return ""
    if len(annotation) == 1 and annotation[0] == "str":
        return f' = "{value}"'
    return f" = {value}"


class ClientFactory:
    def __init__(self, definition: dict, class_name: Optional[str] = None):
        self._definition = definition
        self._client_class_name = class_name or "Client"

    def generate(self):
        address = self._definition.get("address", {})
        host = address.get("host", "localhost")
        port = address.get("port", 8000)

        c = Class(name=self._client_class_name)
        c.doc = self._definition.get("documentation", "")
        c.methods.append(self.generate_init_method((host, port)))

        endpoints = self._definition.get("endpoints", [])
        for endpoint in endpoints:
            name = endpoint.get("name")
            doc = endpoint.get("documentation")
            return_annotation = return_annotation_to_str(
                endpoint.get("returnAnnotation")
            )

            m = Method(name=name, return_annotation=return_annotation, doc=doc)
            c.methods.append(m)
            for parameter in endpoint.get("parameters", []):
                p = Parameter.from_dict(parameter)
                m.parameters.append(p)

        lines = ["from __future__ import annotations\n"]
        lines.append("import typing")
        lines.append("from typing import Optional\n")
        lines.append("from remotecall import BaseClient\n\n")
        lines.append(str(c))

        return "\n".join(lines)

    @classmethod
    def generate_init_method(cls, server_address):
        return (
            f"    def __init__(self, server_address={server_address}):\n"
            f"        super().__init__(server_address=server_address)\n"
        )


class Parameter:
    @classmethod
    def from_dict(cls, definition: dict):
        return cls(
            definition["name"],
            definition["annotation"],
            definition.get("default", None),
            definition["optional"],
        )

    def __init__(self, name: str, annotation: list[str], default: Any, optional: bool):
        self.name = name
        self.annotation = annotation
        self.default = default
        self.optional = optional

    def __str__(self):
        return "".join(
            [
                self.name,
                parameter_annotation_to_str(self.annotation, self.optional),
                default_parameter_value_to_str(self.default, self.annotation),
            ]
        )


class Method:
    def __init__(self, name: str, return_annotation: str, doc: str = None):
        self.name = name
        self.return_annotation = return_annotation
        self.parameters = []
        self.indent = "    "
        self.doc = indent_doc(doc, self.indent * 2)

    def __str__(self):
        lines = [f"{self.indent}def {self.name}(self"]

        # Signature
        for parameter in self.parameters:
            lines.append(f", {parameter}")
        lines.append(")")

        # Return type
        lines.append(self.return_annotation)
        lines.append(":\n")

        # Docstring
        if self.doc:
            lines.append(self.indent * 2)
            lines.append(f'"""{self.doc}\n')
            lines.append(self.indent * 2)
            lines.append('"""\n')

        # Method body
        lines.append(self.indent * 2)
        lines.append(f'return self.call("{self.name}"')

        for parameter in self.parameters:
            lines.append(f", {parameter.name}={parameter.name}")

        lines.append(")\n")

        return "".join(lines)


class Class:
    def __init__(self, name: str):
        self.name = name.capitalize()
        self.methods = []
        self.indent = ""
        self.doc = None

    def __str__(self):
        lines = [f"class {self.name}(BaseClient):"]

        if self.doc:
            lines.append(f'    """{self.doc}')
            lines.append('    """')

        for method in self.methods:
            lines.append(str(method))

        return "\n".join(lines)


def indent_doc(doc: str, indent: str) -> str:
    if not doc:
        return doc

    lines = doc.split("\n")
    for i, line in enumerate(lines[1:], 1):
        lines[i] = indent + line
    return "\n".join(lines)
