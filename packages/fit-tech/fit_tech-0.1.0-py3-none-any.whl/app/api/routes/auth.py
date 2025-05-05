from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any

from app.core.schemas.user import UserCreate, User, Token
from app.core.services.user import UserService
from app.api.dependencies import get_user_service

router = APIRouter(tags=["auth"])

@router.post("/signup", response_model=User)
async def signup(
    user_in: UserCreate, 
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Регистрация нового пользователя
    """
    try:
        user = await user_service.create(obj_in=user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Аутентификация пользователя и получение токена доступа
    """
    auth_result = await user_service.authenticate(
        email=form_data.username, 
        password=form_data.password
    )
    
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "access_token": auth_result["access_token"], 
        "token_type": auth_result["token_type"]
    }
