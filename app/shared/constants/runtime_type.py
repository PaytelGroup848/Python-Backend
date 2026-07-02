from enum import StrEnum


class RuntimeType(StrEnum):

    LOCAL = "LOCAL"

    SINGLE_GPU = "SINGLE_GPU"

    MULTI_GPU = "MULTI_GPU"

    DISTRIBUTED = "DISTRIBUTED"

    CPU = "CPU"

    TPU = "TPU"

    CUSTOM = "CUSTOM"