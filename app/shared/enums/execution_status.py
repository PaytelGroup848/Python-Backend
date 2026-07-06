from enum import StrEnum


class ExecutionStatus(StrEnum):

    PENDING = "PENDING"

    RUNNING = "RUNNING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"