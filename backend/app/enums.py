from enum import Enum

class Role(str, Enum):
    USER = "user"
    VOLUNTEER = "volunteer"
    MODERATOR = "moderator"

class Status(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"