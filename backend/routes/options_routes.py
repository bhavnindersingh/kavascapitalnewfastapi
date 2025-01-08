from fastapi import APIRouter, Depends, HTTPException
from services.kite_service import KiteService
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd

router = APIRouter(prefix="/api/v1/options")

def get_kite_service():
    return KiteService()

@router.get("/expiry-dates/{symbol}")
async def get_expiry_dates(
    symbol: str,
    kite_service: KiteService = Depends(get_kite_service)
) -> List[str]:
    """Get available expiry dates for a symbol"""
    try:
        # Get instruments for the symbol
        instruments = kite_service.kite.instruments("NFO")
        
        # Filter instruments for the given symbol
        symbol_instruments = [
            inst for inst in instruments 
            if inst['name'] == symbol and inst['instrument_type'] in ['CE', 'PE']
        ]
        
        if not symbol_instruments:
            raise HTTPException(
                status_code=404,
                detail=f"No options found for symbol {symbol}"
            )
        
        # Extract unique expiry dates
        expiry_dates = sorted(list(set(
            inst['expiry'].strftime("%Y-%m-%d") 
            for inst in symbol_instruments
        )))
        
        return expiry_dates
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch expiry dates: {str(e)}"
        )

@router.get("/chain/{symbol}")
async def get_option_chain(
    symbol: str,
    expiry: str,
    kite_service: KiteService = Depends(get_kite_service)
) -> Dict[str, Any]:
    """Get option chain data for a symbol and expiry date"""
    try:
        # Convert expiry string to datetime
        expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
        
        # Get instruments for the symbol
        instruments = kite_service.kite.instruments("NFO")
        
        # Filter instruments for the given symbol and expiry
        options = [
            inst for inst in instruments 
            if inst['name'] == symbol 
            and inst['expiry'].date() == expiry_date
            and inst['instrument_type'] in ['CE', 'PE']
        ]
        
        if not options:
            raise HTTPException(
                status_code=404,
                detail=f"No options found for {symbol} with expiry {expiry}"
            )
        
        # Get spot price
        spot_quote = kite_service.kite.quote(f"NSE:{symbol}")
        spot_price = spot_quote[f"NSE:{symbol}"]["last_price"]
        
        # Organize options by strike price
        strikes = {}
        for opt in options:
            strike = opt['strike']
            if strike not in strikes:
                strikes[strike] = {'strikePrice': strike, 'call': None, 'put': None}
            
            option_data = {
                'type': 'CALL' if opt['instrument_type'] == 'CE' else 'PUT',
                'instrument_token': opt['instrument_token'],
                'oi': 0,  # Will be updated via WebSocket
                'change': 0,
                'ltp': 0,
                'iv': 0,
                'delta': 0,
                'gamma': 0,
                'theta': 0,
                'vega': 0,
                'volga': 0,
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
            'stockInfo': {
                'name': symbol,
                'ltp': spot_price,
                'change': spot_quote[f"NSE:{symbol}"].get('change', 0),
                'lotSize': options[0]['lot_size'],
                'future': spot_price,  # You might want to get actual future price
                'vix': 0,  # You might want to get actual VIX
            },
            'strikes': strikes_list,
            'timestamp': int(datetime.now().timestamp())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch option chain: {str(e)}"
        )