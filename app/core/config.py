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

    RAG_SIMILARITY_THRESHOLD = 1.5

    RAG_MAX_CONTEXT_CHARS = 12000
    RAG_MAX_INGESTION_CHUNKS = 5000

    EMBEDDING_WORKER_BATCH_SIZE = 10

    PROVIDER_FAILURE_THRESHOLD = 3

    PROVIDER_COOLDOWN_SECONDS = 60



    class Config:

        env_file = ".env"


settings = Settings()