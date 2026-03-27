from fastapi import APIRouter, Depends
from core.auth import decode_bearer
from database.init_db import get_db
from database.crud.mapping.student_goal import StudentGoalRepo
from sqlalchemy.orm import Session

router= APIRouter()

@router.get("/")
def get_goals(
    ids: tuple = Depends(decode_bearer),
    db: Session = Depends(get_db)
):
    goal_db = StudentGoalRepo(db)
    try:
        res= goal_db.get_user_goals(ids[0])
        return res
    except:
        pass

