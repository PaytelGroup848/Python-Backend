from enum import StrEnum


class OrganizationRole(StrEnum):

    OWNER = "OWNER"

    ADMIN = "ADMIN"

    DEVELOPER = "DEVELOPER"

    ANALYST = "ANALYST"

    VIEWER = "VIEWER"