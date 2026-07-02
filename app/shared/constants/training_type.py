from enum import StrEnum


class TrainingType(StrEnum):

    PRETRAIN = "PRETRAIN"

    FINETUNE = "FINETUNE"

    CONTINUAL = "CONTINUAL"

    INSTRUCTION = "INSTRUCTION"

    RLHF = "RLHF"

    DPO = "DPO"

    PPO = "PPO"

    SFT = "SFT"

    LORA = "LORA"

    QLORA = "QLORA"

    EMBEDDING = "EMBEDDING"