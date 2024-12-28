from typing import Dict, List, Optional
from kiteconnect import KiteConnect
from app.core.config import get_settings
from app.schemas.kite_schemas import KiteQuote, MarketDepth
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class KiteRepository:
    _instance = None
    _access_token = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KiteRepository, cls).__new__(cls)
            settings = get_settings()
            try:
                cls._instance.kite = KiteConnect(api_key=settings.KITE_API_KEY)
                logger.info(f"KiteConnect initialized with API key: {settings.KITE_API_KEY}")
                if cls._access_token:
                    cls._instance.kite.set_access_token(cls._access_token)
            except Exception as e:
                logger.error(f"Error initializing KiteConnect: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error initializing KiteConnect: {str(e)}")
        return cls._instance

    @classmethod
    def set_access_token(cls, token: str):
        try:
            if cls._instance and cls._instance.kite:
                cls._instance.kite.set_access_token(token)
                logger.info("Access token set successfully")
                cls._access_token = token
            else:
                raise Exception("KiteConnect not initialized")
        except Exception as e:
            logger.error(f"Error setting access token: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error setting access token: {str(e)}")

    def validate_token(self) -> bool:
        """Validate if the current access token is valid"""
        if not self._access_token:
            logger.error("No access token set")
            return False
        try:
            profile = self.kite.profile()
            logger.info(f"Token validated successfully for user: {profile.get('user_name')}")
            return True
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            return False

    def get_instruments(self) -> List[Dict]:
        """Get list of available instruments"""
        try:
            return self.kite.instruments()
        except Exception as e:
            logger.error(f"Error fetching instruments: {str(e)}")
            raise HTTPException(status_code=400, detail="Failed to fetch instruments")

    def get_quote(self, instrument_tokens: List[int]) -> Dict[str, KiteQuote]:
        """Get market quotes for instruments"""
        try:
            quotes = self.kite.quote(instrument_tokens)
            return {str(token): KiteQuote(**quote) for token, quote in quotes.items()}
        except Exception as e:
            logger.error(f"Error fetching quotes: {str(e)}")
            raise HTTPException(status_code=400, detail="Failed to fetch quotes")

    def get_ohlc(self, instrument_tokens: List[int]) -> Dict:
        """Get OHLC data for instruments"""
        try:
            return self.kite.ohlc(instrument_tokens)
        except Exception as e:
            logger.error(f"Error fetching OHLC data: {str(e)}")
            raise HTTPException(status_code=400, detail="Failed to fetch OHLC data")
