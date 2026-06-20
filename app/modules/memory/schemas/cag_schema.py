from pydantic import BaseModel


class CAGEntry(
    BaseModel
):

    query: str

    response: str

    assistant_id: int