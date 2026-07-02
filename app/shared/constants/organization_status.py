from enum import StrEnum


class OrganizationStatus(StrEnum):

    ACTIVE = "ACTIVE"

    INACTIVE = "INACTIVE"

    SUSPENDED = "SUSPENDED"

    ARCHIVED = "ARCHIVED"