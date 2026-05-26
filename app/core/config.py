from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    PROJECT_NAME: str = "AI ERP Backend"

    API_VERSION: str = "1.0.0"

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000"
    ]

    SECRET_KEY: str

    OPENAI_API_KEY: str

    MISTRAL_API_KEY: str

    GROQ_API_KEY: str

    DATABASE_URL: str

    DEEPGRAM_API_KEY: str

    REDIS_HOST: str
    
    REDIS_PORT: int



    class Config:

        env_file = ".env"


settings = Settings()