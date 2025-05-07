from motor.motor_asyncio import AsyncIOMotorDatabase
from ..schema import AddColumnField, FieldTypeEnum, CreateCollectionSchema
from typing import Optional, Any, List, Dict
from datetime import datetime, UTC
from uuid import uuid4
from pymongo.errors import PyMongoError
from abs_exception_core.exceptions import NotFoundError, GenericHttpError, BadRequestError

class BaseCollectionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    def get_base_document_fields(self) -> Dict[str, Any]:
        """Get the base document fields"""
        return {
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

    async def add_field(self, column: AddColumnField, collection_name: Optional[str] = None) -> bool:
        """Add a new field to all documents in the collection"""
        try:
            collection = self.db[collection_name]
            
            await collection.update_many(
                {column.column_field: {"$exists": False}},
                {"$set": {column.column_field: column.column_default or self.get_default_for_type(column.column_type)}},
                hint="_id_"
            )

            if column.is_unique and column.column_type != FieldTypeEnum.DATETIME:
                await collection.create_index(column.column_field, unique=True)
            
            return True
            
        except Exception as e:
            await self._handle_mongo_error("add field", e)

    async def delete_field(self, column_name: str, collection_name: Optional[str] = None) -> bool:
        """Delete a field from all documents in the collection"""
        try:
            collection = self.db[collection_name]
            
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
        return default_values.get(field_type) or ""


