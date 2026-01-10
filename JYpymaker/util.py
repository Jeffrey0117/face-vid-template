"""輔助函數，主要與模板模式有關"""

import inspect

from typing import Union, Type
from typing import List, Dict, Any

JsonExportable = Union[int, float, bool, str, List["JsonExportable"], Dict[str, "JsonExportable"]]

def provide_ctor_defaults(cls: Type) -> Dict[str, Any]:
    """為構造函數提供默認值，以繞開構造函數的參數限制"""

    signature = inspect.signature(cls.__init__)
    provided_defaults: Dict[str, Any] = {}

    for name, param in signature.parameters.items():
        if name == 'self': continue
        if param.default is not inspect.Parameter.empty: continue

        if param.annotation is int or param.annotation is float:
            provided_defaults[name] = 0
        elif param.annotation is str:
            provided_defaults[name] = ""
        elif param.annotation is bool:
            provided_defaults[name] = False
        else:
            raise ValueError(f"Unsupported parameter type: {param.annotation}")

    return provided_defaults

def assign_attr_with_json(obj: object, attrs: List[str], json_data: Dict[str, Any]):
    """根據json數據賦值給指定的對象屬性

    若有複雜類型，則嘗試調用其`import_json`方法進行構造
    """
    type_hints: Dict[str, Type] = {}
    for cls in obj.__class__.__mro__:
        if '__annotations__' in cls.__dict__:
            type_hints.update(cls.__annotations__)

    for attr in attrs:
        if hasattr(type_hints[attr], 'import_json'):
            obj.__setattr__(attr, type_hints[attr].import_json(json_data[attr]))
        else:
            obj.__setattr__(attr, type_hints[attr](json_data[attr]))

def export_attr_to_json(obj: object, attrs: List[str]) -> Dict[str, JsonExportable]:
    """將對象屬性導出為json數據

    若有複雜類型，則嘗試調用其`export_json`方法進行導出
    """
    json_data: Dict[str, Any] = {}
    for attr in attrs:
        if hasattr(getattr(obj, attr), 'export_json'):
            json_data[attr] = getattr(obj, attr).export_json()
        else:
            json_data[attr] = getattr(obj, attr)
    return json_data
