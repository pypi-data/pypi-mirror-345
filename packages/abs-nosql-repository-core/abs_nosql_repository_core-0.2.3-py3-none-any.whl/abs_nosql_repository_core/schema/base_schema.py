from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum
from typing import Optional,Union,List,Any,Literal

class Operator(str, Enum):
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    NIN = "nin"
    LIKE = "like"
    ILIKE = "ilike"
    BETWEEN = "between"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"

class LogicalOperator(str, Enum):
    AND = "and"
    OR = "or"

class SortDirection(str, Enum):
    ASC = "ASC"
    DESC = "DESC"

class FieldTypeEnum(str, Enum):
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    LIST = "list"
    DICT = "dict"
    DATETIME = "datetime"

class BaseSchema(BaseModel):
    id:str
    uuid:str
    created_at:datetime
    updated_at:datetime

    model_config = ConfigDict(from_attributes=True)

class BaseDraftSchema(BaseSchema):
    is_draft:bool=True

# Schema for getting distinct values of a field
class FindUniqueByFieldInput(BaseModel):
    field_name: str
    ordering: Optional[Literal["asc", "desc"]]=None
    page: Optional[int]=1
    page_size: Optional[int]=10
    search: Optional[str]=None

# Primitive field condition
class FieldOperatorCondition(BaseModel):
    field: str
    operator: Operator
    value: Union[str,int,float,bool,list,dict,datetime]


# Base structure for a logical group
class LogicalCondition(BaseModel):
    operator: LogicalOperator
    conditions: List["ConditionType"]


# Each item in conditions list can be:
# 1. a logical condition (nested group)
# 2. a dict like {field: ..., operator: ..., value: ...}
ConditionType = Union["LogicalCondition", "FieldOperatorCondition"]

# Top-level filter schema
class FilterSchema(BaseModel):
    operator: LogicalOperator
    conditions: List[ConditionType]

# Sort schema
class SortSchema(BaseModel):
    field:str
    direction:SortDirection

# Base schema for find operations
class ListFilter(BaseModel):
    filters: Optional[FilterSchema] = None
    sort_order: Optional[List[SortSchema]] = None
    page: Optional[int] = 1
    page_size: Optional[int] = 20
    search: Optional[str] = None
    searchable_fields: Optional[List[str]] = None


# Schema for displaying search operations
class SearchOptions(BaseModel):
    search: Optional[str] = None
    sort_order: Optional[List[SortSchema]] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None
    total_count: Optional[int] = None

# Schema for displaying find operations' result
class ListResponse(BaseModel):
    founds: List[Any]
    search_options: SearchOptions

# Add column field schema
class AddColumnField(BaseModel):
    column_field:str
    column_type:FieldTypeEnum
    column_default:Optional[Any] = None