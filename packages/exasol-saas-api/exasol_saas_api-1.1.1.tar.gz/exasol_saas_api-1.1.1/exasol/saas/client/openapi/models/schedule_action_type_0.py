from enum import Enum


class ScheduleActionType0(str, Enum):
    ACTIONCLUSTERSCALE = "ActionClusterScale"
    ACTIONCLUSTERSTART = "ActionClusterStart"
    ACTIONCLUSTERSTOP = "ActionClusterStop"
    ACTIONDATABASEUPGRADE = "ActionDatabaseUpgrade"

    def __str__(self) -> str:
        return str(self.value)
