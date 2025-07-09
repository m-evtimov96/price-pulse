from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import declarative_base


DATABASE_URL = "sqlite+aiosqlite:///./dev.db"  # Update to PostgreSQL later

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base(cls=AsyncAttrs)

# Dependency for FastAPI or general usage
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
