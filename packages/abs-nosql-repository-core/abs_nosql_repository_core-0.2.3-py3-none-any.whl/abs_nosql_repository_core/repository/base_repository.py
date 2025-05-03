from typing import Type, TypeVar, List, Dict, Any
from ..document import BaseDocument, BaseDraftDocument
from abs_exception_core.exceptions import BadRequestError, NotFoundError, InternalServerError
from pydantic import BaseModel
from pymongo import ASCENDING, DESCENDING
from beanie.operators import Set
from pymongo.errors import PyMongoError
from datetime import datetime


from ..schema import ListFilter, SortDirection, LogicalOperator, Operator, FindUniqueByFieldInput,AddColumnField, FieldTypeEnum
from ..util.operator_mappings import logical_operator_map, apply_condition

T = TypeVar("T", bound=BaseModel)

class BaseRepository:
    """
    Base repository class for doing all the database operations using Beanie for NoSQL database
    """

    def __init__(self, document:Type[BaseDocument|BaseDraftDocument]):
        self.document = document

    async def create(self,data:T):
        """
        Create a new document in the collection
        """
        obj_dict = data.__dict__ if hasattr(data, '__dict__') else dict(data)

        model_instance = self.document(**obj_dict)
        await model_instance.insert() 
        return model_instance
    
    async def bulk_create(self,data:List[T]):
        """
        Create multiple documents in the collection
        """
        
        get_obj = lambda obj: obj.__dict__ if hasattr(obj, '__dict__') else dict(obj)
        model_instances = [self.document(**get_obj(item)) for item in data]
        await self.document.insert_many(model_instances)
        return model_instances
    

    async def update(self,id:str,obj:T):
        """
        Update a document by id
        """
        obj_dict = {k: v for k, v in obj.__dict__.items() if v is not None}

        result = await self.document.get(id)
        if result is None:
            raise NotFoundError(detail="You're trying to update a non-existing object")

        await result.update(Set(obj_dict))

        return await self.document.get(id)

    async def get_by_attr(self,attr:str, value:any)->Type[BaseDocument]:
        """
        Get a document by a specific attribute
        """
        try:
            if hasattr(self.document,attr):
                return await self.document.find_one(getattr(self.document,attr)==value)
            else:
                raise BadRequestError(f"Attribute {attr} not found in document {self.document.__name__}")

        except Exception as e:
            raise e
        
    async def get_all(self,find:ListFilter):
        """
        Get all documents from the collection with advanced filtering, sorting, searching and pagination
        """
        page = find.page or 1
        page_size = find.page_size or 20
        skip = (page - 1) * page_size

        mongo_filter = None

        # Build the query with filter
        if find.filters:
            filter_dict = find.filters.model_dump()
            mongo_filter = self.build_mongo_filter(filter_dict)
            if find.search and find.searchable_fields and len(find.searchable_fields) > 0:
                search_conditions = [
                    {field: {"$regex": f".*{find.search}.*", "$options": "i"}}
                    for field in find.searchable_fields
                ]
                search_filter = {"$or": search_conditions}
                if mongo_filter:
                    mongo_filter = {"$and": [mongo_filter, search_filter]}
                else:
                    mongo_filter = search_filter
            query = self.document.find(mongo_filter)
        else:
            query = self.document.find_all()

        count = await query.count()

        # Apply pagination
        query = query.skip(skip).limit(page_size)

        # Apply sorting 
        if find.sort_order and len(find.sort_order) > 0:
            order = self.get_sort_order(find.sort_order)
            query = query.sort(order)

        # fetch data according to the query
        data = await query.to_list()
        data = data or []

        total_pages = (count + find.page_size - 1) // find.page_size

        response = {
            "founds": data, 
            "search_options": {
                "total_pages": total_pages,
                "total_count": count,
                "page": find.page,
                "page_size": find.page_size,
                "search": find.search,
                "sort_order": find.sort_order
            }
        }
        return response

    def get_sort_order(self,sort_order:List):
        order = []

        # Handle sort orders
        for sort in sort_order:
            if self.document.model_fields.get(sort.field):
                if sort.direction == SortDirection.ASC:
                    order.append((sort.field,ASCENDING))
                else:
                    order.append((sort.field,DESCENDING))
        return order
    
    def build_mongo_filter(self, filter_dict: Dict,operator:LogicalOperator=LogicalOperator.AND) -> Dict[str, Any]:
        if not isinstance(filter_dict, dict):
            return {}
        
        # Handle logical groups
        if "operator" in filter_dict and "conditions" in filter_dict:
            mongo_sub_filters = []

            for cond in filter_dict["conditions"]:
                # Handle nested logical groups
                sub_filter = self.build_mongo_filter(cond)
                if sub_filter:
                    mongo_sub_filters.append(sub_filter)

            return {
                logical_operator_map[filter_dict["operator"]]: mongo_sub_filters
            }

        # Handle primitive field conditions
        elif "field" in filter_dict and "operator" in filter_dict and "value" in filter_dict:
            try:
                comp_operator = Operator(filter_dict["operator"].lower())
                return apply_condition(self.document,comp_operator,filter_dict["field"], filter_dict["value"])
            except ValueError:
                raise BadRequestError(f"Invalid comparison operator: {filter_dict['operator']}")
        else:
            raise BadRequestError(f"Invalid filter structure: {filter_dict}")
        
    async def delete(self, id: str) -> bool:
        result = await self.document.get(id)
        if result:
            await result.delete()
            return True
        else:
            raise NotFoundError(detail="Youre trying to delete a non-existing object")
        
    async def get_unique_values(self, schema: FindUniqueByFieldInput):
        try:

            field_name = schema.field_name
            ordering = schema.ordering or "asc"
            page = schema.page or 1
            page_size = schema.page_size or 10
            search = schema.search or None

            if not field_name:
                raise BadRequestError(detail="There needs to be a field name to get unique values")

            # Build the aggregation pipeline
            pipeline = []

            # Apply search 
            if search:
                pipeline.append({
                    "$match": {
                        field_name: {"$regex": f".*{search}.*", "$options": "i"}
                    }
                })
            # Group by field for distinct values
            pipeline.append({
                "$group": {
                    "_id": f"${field_name}"
                }
            })
            if schema.ordering:
                pipeline.append({
                    "$sort": {
                        "_id": 1 if schema.ordering == "asc" else -1
                    }
                })


            # Count total
            count_pipeline = pipeline + [{"$count": "total"}]
            count_result = await self.document.get_motor_collection().aggregate(count_pipeline).to_list(length=1)
            total_count = count_result[0]["total"] if count_result else 0

            # Add pagination
            skip = (page - 1) * page_size
            pipeline.append({"$skip": skip})
            pipeline.append({"$limit": page_size})

            results = await self.document.get_motor_collection().aggregate(pipeline).to_list(length=None)
            values = [r["_id"] for r in results]

            return {
                    "founds": values,
                    "search_options": {
                        "page": page,
                        "page_size": page_size,
                        "ordering": ordering,
                        "total_count": total_count
                    }
            }

        except PyMongoError as e:
            raise InternalServerError(detail=str(e))
        except Exception as e:
            raise BadRequestError(detail=str(e))

    async def add_field(self,column:AddColumnField):
        collection = self.document.get_motor_collection()

        try:
            
            result = await collection.update_many(
                {column.column_field: {"$exists": False}},
                {"$set": {column.column_field: self.get_default_for_type(column.column_type)}},
                hint="_id_"
            )

            return True
        except Exception as e:
            print("Error adding field",e)
            raise InternalServerError(detail="Error adding field to the collection")

    def get_default_for_type(self, field_type: FieldTypeEnum) -> Any:
        default_values = {
            FieldTypeEnum.STRING: "",
            FieldTypeEnum.INTEGER: 0,
            FieldTypeEnum.BOOLEAN: False,
            FieldTypeEnum.FLOAT: 0.0,
            FieldTypeEnum.LIST: [],
            FieldTypeEnum.DICT: {},
            FieldTypeEnum.DATE: datetime.now()
        }
        return default_values.get(field_type, None)

