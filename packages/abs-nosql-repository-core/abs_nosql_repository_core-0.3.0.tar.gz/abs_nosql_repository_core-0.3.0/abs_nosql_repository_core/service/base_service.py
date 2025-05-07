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
    
    async def get_by_id(self, id: str, collection_name: str = None) -> any:
        return await self.repository.get_by_attr("id", id, collection_name)

    async def update(self, id: str, data: dict, collection_name: str = None) -> any:
        return await self.repository.update(id, data, collection_name)
    
    async def delete(self, id: str, collection_name: str = None) -> any:
        return await self.repository.delete(id, collection_name)

    async def get_unique_values(self, schema: FindUniqueByFieldInput, collection_name: str = None) -> list[any]:
        return await self.repository.get_unique_values(schema, collection_name)
    
    async def add_field(self, column: AddColumnField, collection_name: str = None):
        return await self.repository.add_field(column, collection_name)
    
    async def get_by_attr(self, attr: str, value: any, collection_name: str = None) -> any:
        return await self.repository.get_by_attr(attr, value, collection_name)