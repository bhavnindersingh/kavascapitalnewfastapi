from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, and_, or_, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.market_data import Instrument, OptionsChain
from app.repositories.base import BaseRepository
import logging

logger = logging.getLogger(__name__)

class InstrumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_instrument(self, instrument_data: Dict[str, Any]) -> Instrument:
        """Insert or update instrument data."""
        stmt = insert(Instrument).values(**instrument_data)
        stmt = stmt.on_conflict_do_update(
            index_elements=['instrument_token'],
            set_=instrument_data
        )
        await self.session.execute(stmt)
        await self.session.commit()
        
        # Fetch and return the updated instrument
        query = select(Instrument).where(Instrument.instrument_token == instrument_data['instrument_token'])
        result = await self.session.execute(query)
        return result.scalars().first()

    async def bulk_upsert_instruments(self, instruments: List[Dict[str, Any]]) -> None:
        """Bulk insert or update instrument data."""
        if not instruments:
            return

        stmt = insert(Instrument).values(instruments)
        stmt = stmt.on_conflict_do_update(
            index_elements=['instrument_token'],
            set_={
                'exchange_token': stmt.excluded.exchange_token,
                'tradingsymbol': stmt.excluded.tradingsymbol,
                'name': stmt.excluded.name,
                'last_price': stmt.excluded.last_price,
                'expiry': stmt.excluded.expiry,
                'strike': stmt.excluded.strike,
                'tick_size': stmt.excluded.tick_size,
                'lot_size': stmt.excluded.lot_size,
                'instrument_type': stmt.excluded.instrument_type,
                'segment': stmt.excluded.segment,
                'exchange': stmt.excluded.exchange,
                'underlying': stmt.excluded.underlying
            }
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_active_instruments(self, instrument_type: Optional[str] = None) -> List[Instrument]:
        """Get all active instruments, optionally filtered by type."""
        query = select(Instrument).where(Instrument.is_active == True)
        if instrument_type:
            query = query.where(Instrument.instrument_type == instrument_type)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_options_chain(
        self,
        underlying: str,
        expiry: Optional[datetime] = None
    ) -> List[Instrument]:
        """Get options chain for an underlying."""
        query = select(Instrument).where(
            and_(
                Instrument.underlying == underlying,
                or_(
                    Instrument.instrument_type == 'CE',
                    Instrument.instrument_type == 'PE'
                )
            )
        )
        
        if expiry:
            query = query.where(Instrument.expiry == expiry)
        else:
            # Get the nearest expiry if not specified
            subquery = (
                select(func.min(Instrument.expiry))
                .where(
                    and_(
                        Instrument.underlying == underlying,
                        Instrument.expiry > datetime.now()
                    )
                )
            )
            query = query.where(Instrument.expiry == subquery)

        query = query.order_by(Instrument.strike)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_futures(
        self,
        underlying: str,
        expiry: Optional[datetime] = None
    ) -> List[Instrument]:
        """Get futures for an underlying."""
        query = select(Instrument).where(
            and_(
                Instrument.underlying == underlying,
                Instrument.instrument_type == 'FUT'
            )
        )
        
        if expiry:
            query = query.where(Instrument.expiry == expiry)
        
        query = query.order_by(Instrument.expiry)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_instrument_by_symbol(
        self,
        tradingsymbol: str,
        exchange: str
    ) -> Optional[Instrument]:
        """Get instrument by trading symbol and exchange."""
        query = select(Instrument).where(
            and_(
                Instrument.tradingsymbol == tradingsymbol,
                Instrument.exchange == exchange
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def update_option_greeks(
        self,
        instrument_token: int,
        greeks_data: Dict[str, float]
    ) -> None:
        """Update options chain with calculated Greeks."""
        stmt = (
            insert(OptionsChain)
            .values(
                instrument_token=instrument_token,
                timestamp=datetime.utcnow(),
                **greeks_data
            )
            .on_conflict_do_update(
                index_elements=['instrument_token'],
                set_=greeks_data
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()
