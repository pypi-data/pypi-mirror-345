from typing import List, Optional
from app.core.models.workout import Workout
from app.core.models.workout_exercise import WorkoutExercise
from app.core.schemas.workout import WorkoutCreate, WorkoutUpdate, WorkoutExerciseCreate
from app.db.repositories.workout import WorkoutRepository
from app.core.services.base import BaseService

class WorkoutService(BaseService[Workout, WorkoutCreate, WorkoutUpdate]):
    def __init__(self, repository: WorkoutRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def get_with_exercises(self, id: int) -> Optional[Workout]:
        return await self.repository.get_with_exercises(id=id)
    
    async def get_multi_by_user(
        self, *, user_id: int, skip: int = 0, limit: int = 100, 
        type: Optional[str] = None, completed: Optional[bool] = None
    ) -> List[Workout]:
        return await self.repository.get_multi_by_user(
            user_id=user_id, skip=skip, limit=limit, 
            type=type, completed=completed
        )
    
    async def update_workout_exercises(
        self, *, workout_id: int, exercises: List[WorkoutExerciseCreate]
    ) -> Workout:
        workout = await self.repository.get_with_exercises(id=workout_id)
        if not workout:
            return None
        
        existing_exercises = {we.exercise_id: we for we in workout.workout_exercises}

        new_exercises = {e.exercise_id: e for e in exercises}

        for exercise_id, exercise_data in new_exercises.items():
            if exercise_id in existing_exercises:
                we = existing_exercises[exercise_id]
                for field, value in exercise_data.dict(exclude={"exercise_id"}).items():
                    setattr(we, field, value)
            else:
                we = WorkoutExercise(
                    workout_id=workout_id,
                    exercise_id=exercise_id,
                    **exercise_data.dict(exclude={"exercise_id"})
                )
                self.repository.db.add(we)

        for exercise_id, we in existing_exercises.items():
            if exercise_id not in new_exercises:
                self.repository.db.delete(we)
        
        await self.repository.db.commit()
        await self.repository.db.refresh(workout)
        return workout
    
    async def create_with_exercises(
        self,
        *,
        workout_in: WorkoutCreate,
        user_id: int
    ) -> Workout:
        data = workout_in.dict(exclude={"exercises"})
        data["user_id"] = user_id

        workout = Workout(**data)
        self.repository.db.add(workout)
        await self.repository.db.commit()
        await self.repository.db.refresh(workout)

        for ex in workout_in.exercises:
            we = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=ex.exercise_id,
                **ex.dict(exclude={"exercise_id"})
            )
            self.repository.db.add(we)

        await self.repository.db.commit()
        await self.repository.db.refresh(workout)
        return workout
