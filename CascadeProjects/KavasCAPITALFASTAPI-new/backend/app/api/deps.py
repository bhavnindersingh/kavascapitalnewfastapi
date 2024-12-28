from typing import Generator, AsyncGenerator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.kite_service import KiteService
from app.repositories.kite_repository import KiteRepository

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session

def get_kite_repository() -> KiteRepository:
    return KiteRepository()

def get_kite_service(
    repository: KiteRepository = Depends(get_kite_repository)
) -> KiteService:
    return KiteService()  # KiteService is a singleton, no need to pass repository
