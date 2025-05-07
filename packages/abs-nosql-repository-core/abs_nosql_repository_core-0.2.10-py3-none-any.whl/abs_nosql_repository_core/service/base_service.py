from ..repository import BaseRepository
from ..schema import ListFilter,FindUniqueByFieldInput, AddColumnField,CreateCollectionSchema

from bson import ObjectId


class BaseService:
    def __init__(self, repository: BaseRepository):
        self.repository = repository

    async def create(self, data: dict, collection_name: str = None) -> any:
        return await self.repository.create(data, collection_name)
    
    async def bulk_create(self, data: list[any], collection_name: str = None) -> list[any]:
        return await self.repository.bulk_create(data, collection_name)
    
    async def get_all(self,find:ListFilter, collection_name: str = None) -> list[any]:
        return await self.repository.get_all(find, collection_name)
    
    async def get_by_id(self, id: ObjectId, collection_name: str = None) -> any:
        return await self.repository.get_by_attr("_id", id, collection_name)

    async def update(self, id: ObjectId, data: dict, collection_name: str = None) -> any:
        return await self.repository.update(id, data, collection_name)
    
    async def delete(self, id: ObjectId, collection_name: str = None) -> any:
        return await self.repository.delete(id, collection_name)

    async def get_unique_values(self, schema: FindUniqueByFieldInput, collection_name: str = None) -> list[any]:
        return await self.repository.get_unique_values(schema, collection_name)
    
    async def add_field(self, column: AddColumnField, collection_name: str = None):
        return await self.repository.add_field(column, collection_name)
    
    async def delete_field(self, column_name: str, collection_name: str = None):
        return await self.repository.delete_field(column_name, collection_name)
    
    async def create_collection(self, create_collection: CreateCollectionSchema) -> bool:
        return await self.repository.create_collection(create_collection)
    
    async def delete_collection(self, collection_name: str) -> bool:
        return await self.repository.delete_collection(collection_name)
    
    async def get_collection_names(self) -> list[str]:
        return await self.repository.get_collection_names()
    
    async def rename_collection(self, old_name: str, new_name: str) -> bool:
        return await self.repository.rename_collection(old_name, new_name)
    
    async def get_by_attr(self, attr: str, value: any, collection_name: str = None) -> any:
        return await self.repository.get_by_attr(attr, value, collection_name)