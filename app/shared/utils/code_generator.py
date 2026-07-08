from uuid import uuid4


def generate_pipeline_run_code() -> str:

    return (
        "prun_"
        f"{uuid4().hex}"
    )


def generate_pipeline_step_run_code() -> str:

    return (
        "psrun_"
        f"{uuid4().hex}"
    )