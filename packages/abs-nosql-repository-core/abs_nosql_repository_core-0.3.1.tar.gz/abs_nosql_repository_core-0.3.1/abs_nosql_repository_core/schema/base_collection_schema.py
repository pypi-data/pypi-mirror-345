
from pydantic import BaseModel
from typing import Optional, Any, List, Dict
from datetime import datetime, UTC
from uuid import uuid4
from enum import Enum


class FieldTypeEnum(str, Enum):
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    LIST = "list"
    DICT = "dict"
    DATETIME = "datetime"
# Add column field schema
class AddColumnField(BaseModel):
    column_field:str
    column_type:FieldTypeEnum
    column_default:Optional[Any] = None
    is_unique:Optional[bool] = False

class CreateCollectionSchema(BaseModel):
    collection_name:str
    default_values:Optional[Dict[str,Any]] = None