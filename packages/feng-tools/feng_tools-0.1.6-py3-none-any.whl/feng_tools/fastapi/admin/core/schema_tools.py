from typing import Optional, List, Type

import pydantic
from pydantic import BaseModel, Field, ConfigDict
from sqlmodel.main import FieldInfo

def _create_property_type(field_info:FieldInfo, required:bool =None):
    if not required:
        return (Optional[field_info.annotation],
                Field(default=None, title=field_info.title,
                      description=field_info.description))
    if field_info.is_required() or required:
        return (field_info.annotation,
                           Field(title=field_info.title,
                                 description=field_info.description))
    return (Optional[field_info.annotation],
                           Field(default=None, title=field_info.title,
                                 description=field_info.description))

def create_model_schema(schema_name, model_field_dict:dict[str, FieldInfo],
                        schema_fields:Optional[List[str|FieldInfo]] = None,
                        exclude_fields:Optional[list[str]]=None,
                        extra_allow:bool=False,
                        required:bool =None) ->Type[BaseModel]:
    properties = dict()
    for key, field_info in model_field_dict.items():
        if exclude_fields and key in exclude_fields:
            continue
        if schema_fields is None:
            properties[key] =_create_property_type(field_info, required=required)
        elif len(schema_fields) ==0:
            break
        else:
            for tmp_field in schema_fields:
                if not isinstance(tmp_field, str):
                    tmp_field = getattr(tmp_field, 'key')
                if key == tmp_field:
                    properties[key] = _create_property_type(field_info)

    config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
    if extra_allow:
        config = ConfigDict(extra="allow", arbitrary_types_allowed=True, from_attributes=True)
    return pydantic.create_model(
        schema_name,
        __config__=config,
        __base__=None,
        __module__=__name__,
        __validators__=None,
        __cls_kwargs__=None,
        __slots__=None,
        **properties
    )





