from kiteconnect import KiteConnect
from config.kite_config import get_kite_settings
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class KiteService:
    def __init__(self):
        self.settings = get_kite_settings()
        self.kite = KiteConnect(api_key=self.settings.api_key)
        if self.settings.access_token:
            self.kite.set_access_token(self.settings.access_token)

    def get_login_url(self) -> str:
        """Generate login URL for Kite Connect"""
        return self.kite.login_url()

    async def set_access_token(self, request_token: str) -> dict:
        """Exchange request token for access token"""
        try:
            data = self.kite.generate_session(
                request_token=request_token,
                api_secret=self.settings.api_secret
            )
            access_token = data["access_token"]
            self.kite.set_access_token(access_token)
            return {"access_token": access_token}
        except Exception as e:
            logger.error(f"Error generating access token: {str(e)}")
            raise HTTPException(status_code=400, detail="Failed to generate access token")

    def validate_token(self) -> bool:
        """Validate if the current access token is valid"""
        try:
            self.kite.profile()
            return True
        except:
            return False

    def get_instruments(self):
        """Get list of tradeable instruments"""
        try:
            return self.kite.instruments()
        except Exception as e:
            logger.error(f"Error fetching instruments: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch instruments")

    def get_quote(self, instrument_tokens: list):
        """Get market quotes for instruments"""
        try:
            return self.kite.quote(instrument_tokens)
        except Exception as e:
            logger.error(f"Error fetching quotes: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch quotes")
