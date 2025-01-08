from fastapi import APIRouter, HTTPException, Depends
from app.services.kite_service import KiteService
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter()
kite_service = KiteService()

@router.get("/expiry-dates/{symbol}")
async def get_expiry_dates(symbol: str) -> List[str]:
    """Get available expiry dates for a symbol"""
    try:
        expiry_dates = await kite_service.get_expiry_dates(symbol)
        return expiry_dates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chain/{symbol}/{expiry}")
async def get_option_chain(symbol: str, expiry: str) -> Dict[str, Any]:
    """Get option chain data for a symbol and expiry"""
    try:
        # Get instrument info for the symbol
        instrument = await kite_service.get_instrument_info(symbol)
        if not instrument:
            raise HTTPException(status_code=404, detail="Symbol not found")

        # Get option chain data
        chain_data = await kite_service.get_option_chain(symbol, expiry)
        
        # Format the response
        response = {
            "stockInfo": {
                "name": symbol,
                "ltp": instrument.get("last_price", 0),
                "change": instrument.get("change", 0),
                "lotSize": instrument.get("lot_size", 0),
                "future": instrument.get("futures_price", 0),
                "vix": instrument.get("vix", 0)
            },
            "strikes": []
        }

        # Add strike prices with call and put options
        for strike in chain_data:
            strike_data = {
                "strikePrice": strike["strike_price"],
                "call": {
                    "instrument_token": strike["CE"]["instrument_token"],
                    "ltp": strike["CE"]["last_price"],
                    "oi": strike["CE"]["oi"],
                    "oiChange": strike["CE"]["oi_change"],
                    "volume": strike["CE"]["volume"],
                    "iv": strike["CE"]["iv"],
                    "change": strike["CE"]["change"],
                    "bidQty": strike["CE"]["bid_quantity"],
                    "askQty": strike["CE"]["ask_quantity"]
                },
                "put": {
                    "instrument_token": strike["PE"]["instrument_token"],
                    "ltp": strike["PE"]["last_price"],
                    "oi": strike["PE"]["oi"],
                    "oiChange": strike["PE"]["oi_change"],
                    "volume": strike["PE"]["volume"],
                    "iv": strike["PE"]["iv"],
                    "change": strike["PE"]["change"],
                    "bidQty": strike["PE"]["bid_quantity"],
                    "askQty": strike["PE"]["ask_quantity"]
                }
            }
            response["strikes"].append(strike_data)

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
