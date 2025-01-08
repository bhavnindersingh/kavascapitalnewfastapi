from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.sql import Select
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: Any) -> Optional[ModelType]:
        """Get a single record by id."""
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_attributes(self, **kwargs) -> Optional[ModelType]:
        """Get a single record by attribute values."""
        conditions = [getattr(self.model, k) == v for k, v in kwargs.items()]
        query = select(self.model).where(*conditions)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_multi(
        self, 
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        **kwargs
    ) -> List[ModelType]:
        """Get multiple records with optional filtering."""
        query = select(self.model)
        
        # Add filters
        if kwargs:
            conditions = [getattr(self.model, k) == v for k, v in kwargs.items()]
            query = query.where(*conditions)
        
        # Add ordering
        if order_by:
            if order_by.startswith("-"):
                query = query.order_by(getattr(self.model, order_by[1:]).desc())
            else:
                query = query.order_by(getattr(self.model, order_by))
        
        # Add pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def create_multi(self, objects: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple records."""
        db_objs = [self.model(**obj) for obj in objects]
        self.session.add_all(db_objs)
        await self.session.commit()
        for obj in db_objs:
            await self.session.refresh(obj)
        return db_objs

    async def update(
        self,
        *,
        id: Any,
        obj_in: Dict[str, Any]
    ) -> Optional[ModelType]:
        """Update a record by id."""
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(**obj_in)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalars().first()

    async def delete(self, *, id: Any) -> bool:
        """Delete a record by id."""
        query = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        await self.session.commit()
        return bool(result.rowcount)

    async def execute_query(self, query: Select) -> List[ModelType]:
        """Execute a custom query."""
        result = await self.session.execute(query)
        return result.scalars().all()
