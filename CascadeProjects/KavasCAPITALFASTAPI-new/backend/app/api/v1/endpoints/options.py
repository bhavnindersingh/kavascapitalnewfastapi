from fastapi import APIRouter, Depends, HTTPException
from app.services.kite_service import KiteService
from datetime import datetime
from typing import List, Dict, Any
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()

def get_kite_service():
    return KiteService()

@router.get("/expiry-dates/{symbol}", response_model=List[str])
async def get_expiry_dates(
    symbol: str,
    kite_service: KiteService = Depends(get_kite_service)
) -> List[str]:
    """Get available expiry dates for a symbol"""
    try:
        logger.debug(f"Fetching expiry dates for symbol: {symbol}")
        
        # Get instruments for the symbol
        try:
            # Get NFO instruments asynchronously
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor() as pool:
                instruments = await loop.run_in_executor(pool, kite_service.get_instruments, "NFO")
        except Exception as e:
            logger.error(f"Error fetching instruments: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch instruments: {str(e)}"
            )
        
        # Filter instruments for the given symbol
        symbol_instruments = [
            inst for inst in instruments 
            if inst['name'] == symbol and inst['instrument_type'] in ['CE', 'PE']
        ]
        
        if not symbol_instruments:
            logger.error(f"No options found for symbol {symbol}")
            raise HTTPException(
                status_code=404,
                detail=f"No options found for symbol {symbol}"
            )
        
        # Extract unique expiry dates and format them
        expiry_dates = sorted(list(set(
            inst['expiry'].strftime("%Y-%m-%d") 
            for inst in symbol_instruments 
            if inst.get('expiry')
        )))
        
        logger.debug(f"Found {len(expiry_dates)} expiry dates for {symbol}")
        return expiry_dates

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing expiry dates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process expiry dates: {str(e)}"
        )

@router.get("/chain/{symbol}/{expiry}", response_model=Dict[str, Any])
async def get_option_chain(
    symbol: str,
    expiry: str,
    kite_service: KiteService = Depends(get_kite_service)
) -> Dict[str, Any]:
    """Get option chain data for a symbol and expiry date"""
    try:
        logger.debug(f"Fetching option chain for {symbol}, expiry: {expiry}")
        
        # Get instruments for the symbol
        try:
            instruments = await kite_service.get_instruments("NFO")
        except Exception as e:
            logger.error(f"Error fetching instruments: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch instruments: {str(e)}"
            )
        
        # Filter instruments for the given symbol and expiry
        options = [
            inst for inst in instruments 
            if inst['name'] == symbol 
            and inst['expiry'] == expiry
            and inst['instrument_type'] in ['CE', 'PE']
        ]
        
        if not options:
            logger.error(f"No options found for {symbol} with expiry {expiry}")
            raise HTTPException(
                status_code=404,
                detail=f"No options found for {symbol} with expiry {expiry}"
            )
        
        # Get spot price
        try:
            spot_quote = await kite_service.get_quote([f"NSE:{symbol}"])
            spot_price = spot_quote[f"NSE:{symbol}"]["last_price"]
            spot_change = spot_quote[f"NSE:{symbol}"].get('change', 0)
        except Exception as e:
            logger.error(f"Failed to get spot quote: {str(e)}")
            spot_price = 0
            spot_change = 0
        
        # Organize options by strike price
        strikes = {}
        for opt in options:
            strike = opt['strike']
            if strike not in strikes:
                strikes[strike] = {'strikePrice': strike, 'call': None, 'put': None}
            
            option_data = {
                'type': 'CALL' if opt['instrument_type'] == 'CE' else 'PUT',
                'instrument_token': opt['instrument_token'],
                'oi': 0,
                'change': 0,
                'ltp': 0,
                'iv': 0,
                'delta': 0,
                'gamma': 0,
                'theta': 0,
                'vega': 0,
            }
            
            if opt['instrument_type'] == 'CE':
                strikes[strike]['call'] = option_data
            else:
                strikes[strike]['put'] = option_data
        
        # Convert to sorted list
        strikes_list = sorted(
            [strike_data for strike_data in strikes.values()],
            key=lambda x: x['strikePrice']
        )
        
        return {
            'symbol': symbol,
            'expiry': expiry,
            'spotPrice': spot_price,
            'spotChange': spot_change,
            'strikes': strikes_list,
            'lastUpdated': datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing option chain: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process option chain: {str(e)}"
        )