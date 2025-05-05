from typing import Generic, TypeVar, Type, List, Optional, Any, Dict, Union
from pydantic import BaseModel

from app.core.models.base import Base
from app.db.repositories.base import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, repository: BaseRepository):
        self.repository = repository
    
    async def get(self, id: Any) -> Optional[ModelType]:
        return await self.repository.get(id=id)
    
    async def get_multi(
        self, *, skip: int = 0, limit: int = 100, filters: Dict = None
    ) -> List[ModelType]:
        return await self.repository.get_multi(skip=skip, limit=limit, filters=filters)
    
    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        return await self.repository.create(obj_in=obj_in)
    
    async def update(
        self, *, id: Any, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        db_obj = await self.repository.get(id=id)
        if not db_obj:
            return None
        return await self.repository.update(db_obj=db_obj, obj_in=obj_in)
    
    async def delete(self, *, id: int) -> ModelType:
        return await self.repository.delete(id=id)
