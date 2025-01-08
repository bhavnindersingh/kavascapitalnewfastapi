from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.market_data import Instrument, TickData, MarketDepth, OHLCV
from app.repositories.base import BaseRepository
import logging

logger = logging.getLogger(__name__)

class MarketDataRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.tick_batch: List[Dict[str, Any]] = []
        self.depth_batch: List[Dict[str, Any]] = []
        self.batch_size = 1000  # Maximum number of records to batch before writing
        self.max_batch_age = timedelta(seconds=1)  # Maximum age of batch before writing
        self.last_batch_time = datetime.utcnow()

    async def add_tick(self, tick_data: Dict[str, Any]) -> None:
        """Add tick data to batch."""
        self.tick_batch.append(tick_data)
        await self._check_batch()

    async def add_market_depth(self, depth_data: Dict[str, Any]) -> None:
        """Add market depth data to batch."""
        self.depth_batch.append(depth_data)
        await self._check_batch()

    async def _check_batch(self) -> None:
        """Check if batch should be written to database."""
        current_time = datetime.utcnow()
        batch_age = current_time - self.last_batch_time
        
        if (len(self.tick_batch) >= self.batch_size or 
            len(self.depth_batch) >= self.batch_size or
            batch_age >= self.max_batch_age):
            await self._write_batch()

    async def _write_batch(self) -> None:
        """Write batched data to database."""
        try:
            if self.tick_batch:
                # Insert tick data
                stmt = insert(TickData).values(self.tick_batch)
                stmt = stmt.on_conflict_do_nothing()  # Skip duplicates
                await self.session.execute(stmt)
                self.tick_batch = []

            if self.depth_batch:
                # Insert market depth data
                stmt = insert(MarketDepth).values(self.depth_batch)
                stmt = stmt.on_conflict_do_nothing()  # Skip duplicates
                await self.session.execute(stmt)
                self.depth_batch = []

            await self.session.commit()
            self.last_batch_time = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error writing batch: {e}")
            await self.session.rollback()
            raise

    async def get_latest_tick(self, instrument_token: int) -> Optional[TickData]:
        """Get the latest tick for an instrument."""
        query = (
            select(TickData)
            .where(TickData.instrument_token == instrument_token)
            .order_by(TickData.timestamp.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_ticks(
        self,
        instrument_token: int,
        from_time: datetime,
        to_time: datetime
    ) -> List[TickData]:
        """Get tick data for an instrument within a time range."""
        query = (
            select(TickData)
            .where(
                and_(
                    TickData.instrument_token == instrument_token,
                    TickData.timestamp >= from_time,
                    TickData.timestamp <= to_time
                )
            )
            .order_by(TickData.timestamp)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_latest_depth(self, instrument_token: int) -> Optional[MarketDepth]:
        """Get the latest market depth for an instrument."""
        query = (
            select(MarketDepth)
            .where(MarketDepth.instrument_token == instrument_token)
            .order_by(MarketDepth.timestamp.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def calculate_ohlcv(
        self,
        instrument_token: int,
        interval: str,
        from_time: datetime,
        to_time: datetime
    ) -> None:
        """Calculate and store OHLCV data for the given interval."""
        # Define interval in seconds
        interval_seconds = {
            "1min": 60,
            "5min": 300,
            "15min": 900,
            "30min": 1800,
            "60min": 3600,
            "1day": 86400
        }.get(interval)

        if not interval_seconds:
            raise ValueError(f"Invalid interval: {interval}")

        # Calculate OHLCV using window functions
        query = select(
            TickData.instrument_token,
            func.date_trunc(interval, TickData.timestamp).label("interval_timestamp"),
            func.first_value(TickData.last_price).over(
                partition_by=func.date_trunc(interval, TickData.timestamp),
                order_by=TickData.timestamp
            ).label("open"),
            func.max(TickData.last_price).label("high"),
            func.min(TickData.last_price).label("low"),
            func.last_value(TickData.last_price).over(
                partition_by=func.date_trunc(interval, TickData.timestamp),
                order_by=TickData.timestamp
            ).label("close"),
            func.sum(TickData.last_quantity).label("volume")
        ).where(
            and_(
                TickData.instrument_token == instrument_token,
                TickData.timestamp >= from_time,
                TickData.timestamp <= to_time
            )
        ).group_by(
            TickData.instrument_token,
            func.date_trunc(interval, TickData.timestamp)
        )

        result = await self.session.execute(query)
        ohlcv_data = result.fetchall()

        # Store OHLCV data
        for row in ohlcv_data:
            ohlcv = OHLCV(
                instrument_token=row.instrument_token,
                timestamp=row.interval_timestamp,
                interval=interval,
                open=row.open,
                high=row.high,
                low=row.low,
                close=row.close,
                volume=row.volume
            )
            self.session.add(ohlcv)

        await self.session.commit()
