# Student Goal CRUD operations - Restored full workflow
from sqlalchemy.orm import Session
from database.models.mapping.student_goal import StudentGoal
from database.models.master.activity_master import ActivityMaster
from database.models.mapping.user_activity_mapping import UserActivityMapping
from database.models.mapping.users import User
from typing import List, Optional
from datetime import datetime


class StudentGoalRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_user_goals(self, user_id: int) -> List[StudentGoal]:
        return (
            self.db.query(StudentGoal)
            .filter(StudentGoal.user_id == user_id, StudentGoal.is_active == 1)
            .all()
        )

    def get_goal_by_id(self, goal_id: int) -> Optional[StudentGoal]:
        return (
            self.db.query(StudentGoal)
            .filter(StudentGoal.id == goal_id, StudentGoal.is_active == 1)
            .first()
        )

    def create_goal(
        self,
        user_id: int,
        activity_id: int,
        target_month: int = None,
    ) -> StudentGoal:
        activity = (
            self.db.query(ActivityMaster)
            .filter(ActivityMaster.id == activity_id)
            .first()
        )
        if not activity:
            return None

        goal = StudentGoal(
            user_id=user_id,
            activity_id=activity_id,
            target_month=target_month,
            is_active=1,
        )
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def create_goals_bulk(
        self,
        user_id: int,
        activity_ids: List[int],
    ) -> List[StudentGoal]:
        goals = []
        for activity_id in activity_ids:
            activity = (
                self.db.query(ActivityMaster)
                .filter(ActivityMaster.id == activity_id)
                .first()
            )
            if not activity:
                continue

            existing = (
                self.db.query(StudentGoal)
                .filter(
                    StudentGoal.user_id == user_id,
                    StudentGoal.activity_id == activity_id,
                    StudentGoal.is_active == 1,
                )
                .first()
            )
            if existing:
                continue

            goal = StudentGoal(
                user_id=user_id,
                activity_id=activity_id,
                is_active=1,
            )
            self.db.add(goal)
            goals.append(goal)

        self.db.commit()
        return goals

    def delete_goal(self, goal_id: int) -> bool:
        goal = self.get_goal_by_id(goal_id)
        if not goal:
            return False
        goal.is_active = 0
        self.db.commit()
        return True

    def delete_goals_bulk(self, goal_ids: List[int]) -> int:
        count = 0
        for goal_id in goal_ids:
            goal = self.get_goal_by_id(goal_id)
            if goal:
                goal.is_active = 0
                count += 1
        self.db.commit()
        return count

    def get_all_goals(self) -> List[StudentGoal]:
        return self.db.query(StudentGoal).filter(StudentGoal.is_active == 1).all()

    def get_user_goals_paginated(
        self, user_id: int, skip: int = 0, limit: int = 10
    ) -> List[StudentGoal]:
        return (
            self.db.query(StudentGoal)
            .filter(StudentGoal.user_id == user_id, StudentGoal.is_active == 1)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_user_goals(self, user_id: int) -> int:
        return (
            self.db.query(StudentGoal)
            .filter(StudentGoal.user_id == user_id, StudentGoal.is_active == 1)
            .count()
        )

    def get_goal_summary(self, user_id: int) -> dict:
        goals = self.get_user_goals(user_id)

        total_target_tokens = 0
        total_current_tokens = 0
        goal_details = []

        for goal in goals:
            activity = (
                self.db.query(ActivityMaster)
                .filter(ActivityMaster.id == goal.activity_id)
                .first()
            )

            if activity:
                target_token = activity.base_token
                total_target_tokens += target_token

                # Get completed activities for this user/activity
                completed = (
                    self.db.query(UserActivityMapping)
                    .filter(
                        UserActivityMapping.user_id == user_id,
                        UserActivityMapping.activity_id == goal.activity_id,
                        UserActivityMapping.status == 3,  # Completed
                        UserActivityMapping.is_active == 1,
                    )
                    .first()
                )
                current_token = activity.base_token if completed else 0
                total_current_tokens += current_token

                goal_details.append(
                    {
                        "id": goal.id,
                        "activity_id": goal.activity_id,
                        "activity_name": activity.activity_name,
                        "target_tokens": target_token,
                        "current_tokens": current_token,
                        "target_month": goal.target_month,
                        "is_completed": completed is not None,
                    }
                )

        return {
            "total_goals": len(goals),
            "minimum_required": 16,
            "minimum_met": len(goals) >= 16,
            "total_target_tokens": total_target_tokens,
            "total_current_tokens": total_current_tokens,
            "remaining_tokens": total_target_tokens - total_current_tokens,
            "goals": goal_details,
        }
