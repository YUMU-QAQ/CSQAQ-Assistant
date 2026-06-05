"""FastAPI dependency injection."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db


# Re-export for convenience
get_db = get_db
