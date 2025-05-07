from typing import Type, TypeVar, List, Dict, Any, Union, Optional
from ..document import BaseDocument
from abs_exception_core.exceptions import BadRequestError, NotFoundError, GenericHttpError
from pydantic import BaseModel
from pymongo import ASCENDING, DESCENDING
from beanie.operators import Set
from pymongo.errors import PyMongoError
from datetime import datetime, UTC
from motor.motor_asyncio import AsyncIOMotorDatabase
from beanie import Document, PydanticObjectId
from bson import ObjectId, Decimal128
from decimal import Decimal
from uuid import uuid4

from ..schema import ListFilter, SortDirection, LogicalOperator, Operator, FindUniqueByFieldInput, AddColumnField, FieldTypeEnum, CreateCollectionSchema
from ..util.operator_mappings import logical_operator_map, apply_condition

T = TypeVar("T", bound=BaseModel)
DocumentType = TypeVar("DocumentType", bound=Document)

class BaseRepository:
    """
    Base repository class for doing all the database operations using Beanie for NoSQL database.
    """

    def __init__(self, document: Optional[Type[DocumentType]] = None, db: Optional[AsyncIOMotorDatabase] = None):
        self.document = document
        self.db = db

    def _convert_to_json_serializable(self, data: Any) -> Any:
        """
        Converts MongoDB documents to JSON-serializable format.
        """
        if data is None:
            return None
            
        # Fast path for common types
        if isinstance(data, (str, int, float, bool)):
            return data
            
        # Handle MongoDB specific types
        if isinstance(data, (ObjectId, Decimal128)):
            return str(data)
            
        if isinstance(data, datetime):
            return data.isoformat()
            
        if isinstance(data, Decimal):
            return float(data)
            
        # Handle collections
        if isinstance(data, dict):
            return {str(k): self._convert_to_json_serializable(v) for k, v in data.items()}
            
        if isinstance(data, (list, tuple, set)):
            return [self._convert_to_json_serializable(item) for item in data]
            
        # Handle Pydantic and Beanie models
        if isinstance(data, (BaseModel, Document)):
            return self._convert_to_json_serializable(data.model_dump())
            
        # Handle objects with __dict__
        if hasattr(data, '__dict__'):
            return self._convert_to_json_serializable(vars(data))
            
        return str(data)

    def get_collection(self, collection_name: Optional[str] = None) -> Any:
        """Get the collection from the database"""
        return self.db[collection_name] if collection_name else self.document.get_motor_collection()
    
    def get_base_document_fields(self) -> Dict[str, Any]:
        """Get the base document fields"""
        return {
            "id": PydanticObjectId(), 
            "uuid": str(uuid4()),  
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        }

    async def _handle_mongo_error(self, operation: str, error: Exception) -> None:
        """Handle MongoDB errors consistently."""
        if isinstance(error, PyMongoError):
            raise GenericHttpError(
                status_code=500,
                detail=str(error),
                error_type="PyMongoError",
                message=f"Failed to {operation}"
            )
        raise BadRequestError(detail=str(error))

    async def create(self, obj: T, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new document in the collection"""
        try:
            obj_dict = obj.model_dump() if hasattr(obj, 'model_dump') else dict(obj)
            
            if collection_name:
                collection = self.get_collection(collection_name)
                result = await collection.insert_one({**self.get_base_document_fields(), **obj_dict})
                return await self.get_by_attr("_id", result.inserted_id, collection_name)
            
            model_instance = self.document(**obj_dict)
            await model_instance.insert()
            return await self.get_by_attr("_id", model_instance._id)
            
        except Exception as e:
            await self._handle_mongo_error("create document", e)

    async def bulk_create(self, data: List[T], collection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Create multiple documents in the collection"""
        try:
            get_obj = lambda obj: obj.model_dump() if hasattr(obj, 'model_dump') else dict(obj)
            
            if collection_name:
                collection = self.get_collection(collection_name)
                documents = [{**self.get_base_document_fields(), **get_obj(item)} for item in data]
                result = await collection.insert_many(documents)
                return [{"_id": id, **doc} for id, doc in zip(result.inserted_ids, documents)]
            
            model_instances = [self.document(**get_obj(item)) for item in data]
            await self.document.insert_many(model_instances)
            return [doc.model_dump() for doc in model_instances]
            
        except Exception as e:
            await self._handle_mongo_error("bulk create documents", e)

    async def update(self, id: Union[str, ObjectId], obj: T, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Update a document by id"""
        try:
            obj_dict = obj.model_dump() if hasattr(obj, 'model_dump') else dict(obj)
            object_id = ObjectId(id) if isinstance(id, str) else id

            if collection_name:
                collection = self.get_collection(collection_name)
                result = await collection.update_one(
                    {"_id": object_id},
                    {"$set": obj_dict, "$currentDate": {"updated_at": True}}
                )
                
                if result.matched_count == 0:
                    raise NotFoundError(detail=f"Document with id {id} not found")
                
                return await self.get_by_attr("_id", object_id, collection_name)
            
            result = await self.document.get(object_id)
            if not result:
                raise NotFoundError(detail=f"Document with id {id} not found")
                
            await result.update(Set(obj_dict))
            return await self.get_by_attr("_id", object_id)
            
        except Exception as e:
            await self._handle_mongo_error("update document", e)

    async def get_by_attr(self, attr: str, value: Any, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Get a document by a specific attribute"""
        try:
            if collection_name:
                collection = self.get_collection(collection_name)
                if attr == "_id":
                    value = ObjectId(value)
                result = await collection.find_one({attr: value})
                if not result:
                    raise NotFoundError(detail=f"Document with {attr}={value} not found")
                return self._convert_to_json_serializable(result)
            
            if not hasattr(self.document, attr):
                raise BadRequestError(f"Attribute {attr} not found in document {self.document.__name__}")
                
            result = await self.document.find_one(getattr(self.document, attr) == value)
            if not result:
                raise NotFoundError(detail=f"Document with {attr}={value} not found")
            return self._convert_to_json_serializable(result)
            
        except Exception as e:
            await self._handle_mongo_error("get document", e)

    async def get_all(self, find: ListFilter, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Get all documents with filtering, sorting, searching and pagination"""
        try:
            page = find.page or 1
            page_size = find.page_size or 20
            skip = (page - 1) * page_size

            collection = self.get_collection(collection_name) if collection_name else self.document.get_motor_collection()
            mongo_filter = self._build_query_filter(find)
            
            count = await collection.count_documents(mongo_filter or {})
            query = collection.find(mongo_filter or {})
            
            if find.sort_order:
                query = query.sort(self._get_sort_order(find.sort_order))
            
            query = query.skip(skip).limit(page_size)
            data = await query.to_list(length=None) or []
            
            total_pages = (count + page_size - 1) // page_size
            
            return {
                "founds": self._convert_to_json_serializable(data),
                "search_options": {
                    "total_pages": total_pages,
                    "total_count": count,
                    "page": page,
                    "page_size": page_size,
                    "search": find.search,
                    "sort_order": find.sort_order
                }
            }
            
        except Exception as e:
            await self._handle_mongo_error("get documents", e)

    def _build_query_filter(self, find: ListFilter) -> Optional[Dict[str, Any]]:
        """Build MongoDB filter from ListFilter"""
        mongo_filter = None

        if find.filters:
            mongo_filter = self.build_filter_condition(find.filters.model_dump())

        if find.search and find.searchable_fields:
            search_conditions = self._build_search_conditions(find.search, find.searchable_fields)
            search_filter = {"$or": search_conditions}
            mongo_filter = (
                {"$and": [mongo_filter, search_filter]} 
                if mongo_filter 
                else search_filter
            )

        return mongo_filter

    def _build_search_conditions(self, search_term: str, searchable_fields: List[str]) -> List[Dict[str, Any]]:
        """Build search conditions for MongoDB query"""
        conditions = []
        for field in searchable_fields:
            if "." in field:
                nested_path = field.split(".")
                conditions.append({
                    ".".join(nested_path): {
                        "$regex": f".*{search_term}.*",
                        "$options": "i"
                    }
                })
            else:
                conditions.append({
                    field: {
                        "$regex": f".*{search_term}.*",
                        "$options": "i"
                    }
                })
        return conditions

    def _get_sort_order(self, sort_order: List[Dict[str, Any]]) -> List[tuple]:
        """Get MongoDB sort order from sort configuration"""
        if not sort_order:
            return [("_id", DESCENDING)]
            
        sort_criteria = [
            (sort.field, ASCENDING if sort.direction == SortDirection.ASC else DESCENDING)
            for sort in sort_order
            if self.document.model_fields.get(sort.field)
        ]
        
        return sort_criteria or [("_id", DESCENDING)]

    def build_filter_condition(self, filter_dict: Dict[str, Any], operator: LogicalOperator = LogicalOperator.AND) -> Dict[str, Any]:
        """Build MongoDB filter from filter dictionary"""
        if not isinstance(filter_dict, dict):
            return {}
        
        if "operator" in filter_dict and "conditions" in filter_dict:
            mongo_sub_filters = [
                self.build_filter_condition(cond)
                for cond in filter_dict["conditions"]
            ]
            return {logical_operator_map[filter_dict["operator"]]: mongo_sub_filters}

        if all(key in filter_dict for key in ["field", "operator", "value"]):
            try:
                comp_operator = Operator(filter_dict["operator"].lower())
                return apply_condition(
                    self.document,
                    comp_operator,
                    filter_dict["field"],
                    filter_dict["value"]
                )
            except ValueError:
                raise BadRequestError(f"Invalid comparison operator: {filter_dict['operator']}")
                
        raise BadRequestError(f"Invalid filter structure: {filter_dict}")

    async def delete(self, id: Union[str, ObjectId], collection_name: Optional[str] = None) -> bool:
        """Delete a document by id"""
        try:
            object_id = ObjectId(id) if isinstance(id, str) else id
            
            if collection_name:
                collection = self.get_collection(collection_name)
                result = await collection.delete_one({"_id": object_id})
                if result.deleted_count == 0:
                    raise NotFoundError(detail="Document not found")
            else:
                result = await self.document.get(object_id)
                if not result:
                    raise NotFoundError(detail="Document not found")
                await result.delete()
                
            return True
            
        except Exception as e:
            await self._handle_mongo_error("delete document", e)

    async def get_unique_values(self, schema: FindUniqueByFieldInput, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Get unique values for a field with pagination and search"""
        try:
            if not schema.field_name:
                raise BadRequestError(detail="Field name is required")

            collection = self.get_collection(collection_name) if collection_name else self.document.get_motor_collection()
            
            pipeline = []
            
            if schema.search:
                pipeline.append({
                    "$match": {
                        schema.field_name: {"$regex": f".*{schema.search}.*", "$options": "i"}
                    }
                })
            
            pipeline.append({"$group": {"_id": f"${schema.field_name}"}})
            
            if schema.ordering:
                pipeline.append({
                    "$sort": {
                        "_id": ASCENDING if schema.ordering == "asc" else DESCENDING
                    }
                })
            
            count_pipeline = pipeline + [{"$count": "total"}]
            count_result = await collection.aggregate(count_pipeline).to_list(length=1)
            total_count = count_result[0]["total"] if count_result else 0
            
            skip = ((schema.page or 1) - 1) * (schema.page_size or 10)
            pipeline.extend([
                {"$skip": skip},
                {"$limit": schema.page_size or 10}
            ])
            
            results = await collection.aggregate(pipeline).to_list(length=None)
            values = [r["_id"] for r in results]
            
            return {
                "founds": values,
                "search_options": {
                    "page": schema.page or 1,
                    "page_size": schema.page_size or 10,
                    "ordering": schema.ordering or "asc",
                    "total_count": total_count
                }
            }
            
        except Exception as e:
            await self._handle_mongo_error("get unique values", e)

    async def add_field(self, column: AddColumnField, collection_name: Optional[str] = None) -> bool:
        """Add a new field to all documents in the collection"""
        try:
            collection = self.get_collection(collection_name) if collection_name else self.document.get_motor_collection()
            
            await collection.update_many(
                {column.column_field: {"$exists": False}},
                {"$set": {column.column_field: column.column_default or self.get_default_for_type(column.column_type)}},
                hint="_id_"
            )
            
            return True
            
        except Exception as e:
            await self._handle_mongo_error("add field", e)

    async def delete_field(self, column_name: str, collection_name: Optional[str] = None) -> bool:
        """Delete a field from all documents in the collection"""
        try:
            collection = self.get_collection(collection_name) if collection_name else self.document.get_motor_collection()
            
            result = await collection.update_many(
                {},
                {"$unset": {column_name: ""}}
            )
            
            if result.modified_count == 0:
                raise NotFoundError(detail=f"Field {column_name} not found")
                
            return True
            
        except Exception as e:
            await self._handle_mongo_error("delete field", e)

    async def create_collection(self, collection_data: CreateCollectionSchema) -> bool:
        """Create a new collection with default values"""
        try:
            collection = self.db[collection_data.collection_name]
            dafault_fields = collection_data.default_values or {}
            print("dafault_fields",dafault_fields)
            print("base_fields",self.get_base_document_fields())
            full_doc = {**self.get_base_document_fields(), **dafault_fields}
            await collection.insert_one(full_doc)
            return True
            
        except Exception as e:
            await self._handle_mongo_error("create collection", e)

    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        try:
            await self.db.drop_collection(collection_name)
            return True
            
        except Exception as e:
            await self._handle_mongo_error("delete collection", e)

    async def rename_collection(self, old_name: str, new_name: str) -> bool:
        """Rename a collection in MongoDB"""
        try:
            # Get full collection names
            full_old = f"{self.db.name}.{old_name}"
            full_new = f"{self.db.name}.{new_name}"

            admin_db = self.db.client.admin

            await admin_db.command({
                "renameCollection": full_old,
                "to": full_new,
                "dropTarget": False 
            })

            return True
        except Exception as e:
            await self._handle_mongo_error("rename collection", e)

    async def get_collection_names(self) -> List[str]:
        """Get all collection names"""
        return await self.db.list_collection_names()

    @staticmethod
    def get_default_for_type(field_type: FieldTypeEnum) -> Any:
        """Get default value for a field type"""
        default_values = {
            FieldTypeEnum.STR: "",
            FieldTypeEnum.INT: 0,
            FieldTypeEnum.BOOL: False,
            FieldTypeEnum.FLOAT: 0.0,
            FieldTypeEnum.LIST: [],
            FieldTypeEnum.DICT: {},
            FieldTypeEnum.DATETIME: datetime.now()
        }
        return default_values.get(field_type)

