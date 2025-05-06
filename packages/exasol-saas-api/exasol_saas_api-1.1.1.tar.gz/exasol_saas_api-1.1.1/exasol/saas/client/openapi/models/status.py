from enum import Enum


class Status(str, Enum):
    CREATING = "creating"
    DELETED = "deleted"
    DELETING = "deleting"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    RUNNING = "running"
    SCALING = "scaling"
    STARTING = "starting"
    STOPPED = "stopped"
    STOPPING = "stopping"
    TOCREATE = "tocreate"
    TODELETE = "todelete"
    TOSCALE = "toscale"
    TOSTART = "tostart"
    TOSTOP = "tostop"

    def __str__(self) -> str:
        return str(self.value)
