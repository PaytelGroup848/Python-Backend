from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)

from sqlalchemy.orm import (
    declarative_base
)

from app.core.config import (
    settings
)


DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://",
    "postgresql+asyncpg://"
)


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=15,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=300,
    pool_pre_ping=True,
    connect_args={
        "command_timeout": 30,
        "server_settings": {
            "tcp_keepalives_idle": "60",
            "tcp_keepalives_interval": "10",
            "tcp_keepalives_count": "5",
        },
    }
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


Base = declarative_base()


async def get_db():

    async with AsyncSessionLocal() as db:

        try:

            yield db

            await db.commit()

        except Exception:

            await db.rollback()

            raise

        finally:

            await db.close()