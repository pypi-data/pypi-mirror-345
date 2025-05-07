from datetime import datetime
from typing import Type

from ..schema import Operator, LogicalOperator
from ..document import BaseDocument
from abs_exception_core.exceptions import BadRequestError

logical_operator_map = {
    LogicalOperator.AND: "$and",
    LogicalOperator.OR: "$or",
}

# Helper function to check if a string is a valid date
def is_valid_date(value: str) -> bool:
    """Check if the value is a valid date string."""
    try:
        datetime.fromisoformat(value)
        return True
    except ValueError:
        return False

def convert_to_datetime(value: any) -> any:
    """Convert a value to a datetime if it's a valid date string."""
    if isinstance(value, str) and is_valid_date(value):
        return datetime.fromisoformat(value)
    return value

def _get_operator_condition(operator: Operator, value: any) -> dict:
    """Get the MongoDB operator condition for a given operator and value"""
    value = convert_to_datetime(value)
    if operator == Operator.EQ:
        return {"$eq": value}
    elif operator == Operator.NE:
        return {"$ne": value}
    elif operator == Operator.GT:
        return {"$gt": value}
    elif operator == Operator.GTE:
        return {"$gte": value}
    elif operator == Operator.LT:
        return {"$lt": value}
    elif operator == Operator.LTE:
        return {"$lte": value}
    elif operator == Operator.IN:
        return {"$in": value}
    elif operator == Operator.NIN:
        return {"$nin": value}
    elif operator == Operator.LIKE:
        return {"$regex": f".*{value}.*"}
    elif operator == Operator.ILIKE:
        return {"$regex": f".*{value}.*", "$options": "i"}
    elif operator == Operator.BETWEEN:
        if isinstance(value, list) and len(value) == 2:
            return {"$gte": value[0], "$lte": value[1]}
        raise BadRequestError("BETWEEN operator requires a list of two values.")
    elif operator == Operator.IS_NULL:
        return {"$eq": None}
    elif operator == Operator.IS_NOT_NULL:
        return {"$ne": None}
    else:
        raise BadRequestError(f"Unsupported operator: {operator}")

def apply_condition(model:Type[BaseDocument],operator:Operator,field:str,value:any):
    """Apply the condition to the query"""
    try:
        # For the nested fields
        if "." in field:
            nested_path = field.split(".")
            nested_filter = {}
            current = nested_filter
            for i, part in enumerate(nested_path[:-1]):
                current[part] = {}
                current = current[part]
            current[nested_path[-1]] = _get_operator_condition(operator, value)
            return nested_filter
        else:
            # For the non-nested fields
            return {field: _get_operator_condition(operator, value)}
    except Exception as e:
        raise BadRequestError(f"Error applying condition: {e}")
