from pydantic import BaseModel


class TranslationRequest(BaseModel):

    target_language: str