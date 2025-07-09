from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.models import Base
from db.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Run on shutdown (if needed)
    # await engine.dispose()  # optional cleanup

app = FastAPI(title="PricePulse", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "PricePulse backend is running"}
