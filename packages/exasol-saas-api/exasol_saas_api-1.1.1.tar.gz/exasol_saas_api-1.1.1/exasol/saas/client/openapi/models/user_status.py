from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "active"
    DEACTIVATED = "deactivated"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
