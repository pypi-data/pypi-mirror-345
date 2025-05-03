from datetime import datetime
from typing import Type

from ..schema import Operator, LogicalOperator
from ..document import BaseDocument
from ..exceptions import BadRequestError

logical_operator_map = {
    LogicalOperator.AND: "$and",
    LogicalOperator.OR: "$or",
}

def apply_condition(model:Type[BaseDocument],operator:Operator,field:str,value:any):
        field_type = model.model_fields[field].annotation
        if field_type == datetime:
            value = datetime.fromisoformat(value)
        if operator == Operator.EQ:
            return {field: {"$eq": value}}
        elif operator == Operator.NE:
            return {field: {"$ne": value}}
        elif operator == Operator.GT:
            return {field: {"$gt": value}}
        elif operator == Operator.GTE:
            return {field: {"$gte": value}}
        elif operator == Operator.LT:
            return {field: {"$lt": value}}
        elif operator == Operator.LTE:
            return {field: {"$lte": value}}

        # Handle 'IN' and 'NIN'
        elif operator == Operator.IN:
            return {field: {"$in": value}}
        elif operator == Operator.NIN:
            return {field: {"$nin": value}}

        # Handle 'LIKE' (wildcard match) and 'ILIKE' (case-insensitive match)
        elif operator == Operator.LIKE:
            return {field: {"$regex": f".*{value}.*"}}  # Case-sensitive LIKE
        elif operator == Operator.ILIKE:
            return {field: {"$regex": f".*{value}.*", "$options": "i"}}  # Case-insensitive LIKE

        # Handle 'BETWEEN'
        elif operator == Operator.BETWEEN:
            if isinstance(value, list) and len(value) == 2:
                return {field: {"$gte": value[0], "$lte": value[1]}}
            raise BadRequestError("BETWEEN operator requires a list of two values.")

        # Handle null checks
        elif operator == Operator.IS_NULL:
            return {field: {"$eq": None}}
        elif operator == Operator.IS_NOT_NULL:
            return {field: {"$ne": None}}