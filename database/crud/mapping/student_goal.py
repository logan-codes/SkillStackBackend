# database/crud/student_goal.py
# TODO: Implement StudentGoal CRUD operations
from sqlalchemy.orm import Session
from database.models.mapping.student_goal import StudentGoal

class StudentGoalRepo():
    def __init__(self, db: Session):
        self.db = db
    def get_user_goals(self, uid: int ):
        return self.db.query(StudentGoal).filter(StudentGoal.user_id == uid).all()