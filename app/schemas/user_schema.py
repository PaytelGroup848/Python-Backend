from pydantic import BaseModel

class UserResponse(BaseModel):

    id: int

    email: str

    role: str

    class Config:

        from_attributes = True