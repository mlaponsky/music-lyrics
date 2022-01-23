from dataclasses import dataclass
from typing import Dict, Optional, Any, List, Union, Iterable

PRIMITIVE_TYPES = (str, int, float, bool)
ARANGO_TYPE_MAP: Dict[type, str] = {
    str: "string",
    int: "number",
    float: "number",
    bool: "boolean",
    list: "array",
    tuple: "array",
    dict: "object"
}
BOOL_TO_STRING_MAP: Dict[bool, str] = {
    True: "true",
    False: "false"
}


def _parse_complex_type(data_type) -> type:
    if data_type.__origin__ is Union:
        num_allowed = 2
    elif issubclass(data_type.__origin__, Dict):
        return type(None)
    elif issubclass(data_type.__origin__, Iterable):
        num_allowed = 1
    else:
        raise ValueError(f"Type {data_type} is an unsupported data type.")
    if len(data_type.__args__) > num_allowed:
        raise ValueError(f"Data type {data_type} is too complex for an ArangoDB document field.")
    return data_type.__args__[0]


class PropertyType(object):
    def __init__(self,
                 _type: str,
                 items: Optional['PropertyType'] = None,
                 required: bool = True):
        self.type: str = _type
        self.items: Optional['PropertyType'] = items
        self.required: bool = required

    @classmethod
    def from_type(cls, data_type):
        required: bool = True
        items = None
        if hasattr(data_type, "__args__"):
            if data_type.__origin__ is Union:
                data_type = _parse_complex_type(data_type)
                required = False
            elif issubclass(data_type.__origin__, Dict):
                data_type = dict
            elif issubclass(data_type.__origin__, Iterable):
                items = cls(_type=ARANGO_TYPE_MAP[_parse_complex_type(data_type)])
                data_type = list
        return cls(_type=ARANGO_TYPE_MAP[data_type],
                   items=items,
                   required=required)

    def as_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"type": self.type}
        if self.items:
            result["items"] = self.items.as_dict()
        return result


@dataclass
class DocumentSchemaRuleProperty(object):
    name: str
    property: PropertyType


@dataclass
class DocumentSchemaRule(object):
    properties: List[DocumentSchemaRuleProperty]
    additional_props: Optional[type] = None

    def as_dict(self) -> Dict[str, Any]:
        required: List[str] = []
        properties: Dict[str, Any] = {}
        result: Dict[str, Any] = {}
        for prop in self.properties:
            properties[prop.name] = prop.property.as_dict()
            if prop.property.required:
                required.append(prop.name)
        result["properties"] = properties
        if self.additional_props:
            result["additionalProperties"] = {"type": ARANGO_TYPE_MAP[self.additional_props]}
        result["required"] = required
        return result


@dataclass
class DocumentSchema(object):
    rule: DocumentSchemaRule
    level: str = "moderate"
    message: str = "Document validation failed."

    def as_dict(self) -> Dict[str, Any]:
        return {
            "rule": self.rule.as_dict(),
            "level": self.level,
            "message": self.message
        }
