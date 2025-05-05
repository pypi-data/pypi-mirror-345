from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas.workout import WorkoutCreate, WorkoutUpdate, Workout
from app.core.services.workout import WorkoutService
from app.api.dependencies import get_workout_service, CurrentUser
from app.core.security import get_current_user
from app.core.models.user import User

router = APIRouter()

@router.post("/", response_model=Workout, status_code=status.HTTP_201_CREATED)
async def create_workout(
    current_user: CurrentUser,
    workout_in: WorkoutCreate,
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Создать новую тренировку для текущего пользователя
    """
    workout_data = workout_in.dict()
    workout_data["user_id"] = current_user.id
    
    workout = await workout_service.create_with_exercises(workout_in=workout_in, user_id=current_user.id)
    return workout

@router.get("/", response_model=List[Workout])
async def get_workouts(
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    completed: Optional[bool] = None,
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Получить список тренировок текущего пользователя с возможностью фильтрации
    """
    workouts = await workout_service.get_multi_by_user(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        type=type,
        completed=completed
    )
    return workouts

@router.get("/{workout_id}", response_model=Workout)
async def get_workout(
    current_user: CurrentUser,
    workout_id: int,
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Получить детали конкретной тренировки
    """
    workout = await workout_service.get_with_exercises(id=workout_id)
    if not workout or workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    return workout

@router.put("/{workout_id}", response_model=Workout)
async def update_workout(
    current_user: CurrentUser,
    workout_id: int,
    workout_in: WorkoutUpdate,
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Обновить тренировку
    """
    workout = await workout_service.get(id=workout_id)
    if not workout or workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    workout = await workout_service.update(id=workout_id, obj_in=workout_in)
    return workout

@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    current_user: CurrentUser,
    workout_id: int,
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Удалить тренировку
    """
    workout = await workout_service.get(id=workout_id)
    if not workout or workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    await workout_service.delete(id=workout_id)
    return None
