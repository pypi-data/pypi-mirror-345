from typing import List, Optional, Dict, Any, Union
from app.core.models.user import User
from app.core.schemas.user import UserCreate, UserUpdate
from app.db.repositories.user import UserRepository
from app.core.services.base import BaseService
from app.core.security import create_access_token
from datetime import timedelta
from app.core.config import settings

class UserService(BaseService[User, UserCreate, UserUpdate]):
    def __init__(self, repository: UserRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def get_by_email(self, *, email: str) -> Optional[User]:
        return await self.repository.get_by_email(email=email)
    
    async def get_by_username(self, *, username: str) -> Optional[User]:
        return await self.repository.get_by_username(username=username)
    
    async def create(self, *, obj_in: UserCreate) -> User:
        existing_user = await self.repository.get_by_email(email=obj_in.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        existing_user = await self.repository.get_by_username(username=obj_in.username)
        if existing_user:
            raise ValueError("Username already taken")
        
        return await self.repository.create(obj_in=obj_in)
    
    async def authenticate(self, *, email: str, password: str) -> Optional[Dict[str, Any]]:
        user = await self.repository.authenticate(email=email, password=password)
        if not user:
            return None
        if not await self.repository.is_active(user):
            return None
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    
    async def is_active(self, user: User) -> bool:
        return await self.repository.is_active(user)
    
    async def is_superuser(self, user: User) -> bool:
        return await self.repository.is_superuser(user)
