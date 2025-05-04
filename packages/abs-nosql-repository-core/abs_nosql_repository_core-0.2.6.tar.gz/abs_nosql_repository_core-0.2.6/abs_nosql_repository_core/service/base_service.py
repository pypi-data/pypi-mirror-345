from ..repository import BaseRepository
from ..schema import ListFilter,FindUniqueByFieldInput, AddColumnField


class BaseService:
    def __init__(self, repository: BaseRepository):
        self.repository = repository

    async def create(self, data: dict) -> any:
        return await self.repository.create(data)
    
    async def get_all(self,find:ListFilter) -> list[any]:
        return await self.repository.get_all(find)
    
    async def get_by_id(self, id: str) -> any:
        return await self.repository.get_by_id(id)

    async def update(self, id: str, data: dict) -> any:
        return await self.repository.update(id, data)
    
    async def delete(self, id: str) -> any:
        return await self.repository.delete(id)

    async def get_unique_values(self, schema: FindUniqueByFieldInput) -> list[any]:
        return await self.repository.get_unique_values(schema)
    
    async def add_field(self, column: AddColumnField):
        return await self.repository.add_field(column)
    
    async def bulk_create(self, data: list[any]) -> list[any]:
        return await self.repository.bulk_create(data)
