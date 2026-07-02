from enum import StrEnum


class ModelStatus(StrEnum):

    DRAFT = "DRAFT"

    TRAINING = "TRAINING"

    READY = "READY"

    DEPLOYED = "DEPLOYED"

    DEPRECATED = "DEPRECATED"

    ARCHIVED = "ARCHIVED"