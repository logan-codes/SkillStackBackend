# database/models/master/__init__.py
# Master/Reference tables

from database.models.master.activity_master import ActivityMaster
from database.models.master.student_goal_master import StudentGoalMaster
from database.models.master.activity_type_master import ActivityTypeMaster
from database.models.master.application_config import ApplicationConfig
from database.models.master.event_master import EventMaster
from database.models.master.gender import Gender
from database.models.master.malpractice_master import MalpracticeMaster
from database.models.master.program_dept_master import ProgramDeptMaster
from database.models.master.roles import Role
from database.models.master.stage import Stage
from database.models.master.status import Status
from database.models.master.workflow import Workflow

__all__ = [
    "ActivityMaster",
    "StudentGoalMaster",
    "ActivityTypeMaster",
    "ApplicationConfig",
    "EventMaster",
    "Gender",
    "MalpracticeMaster",
    "ProgramDeptMaster",
    "Role",
    "Stage",
    "Status",
    "Workflow",
]
