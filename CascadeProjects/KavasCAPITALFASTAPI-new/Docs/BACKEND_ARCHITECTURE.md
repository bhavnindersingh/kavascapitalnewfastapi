# NIFTY 50 HFT System - Backend Architecture

## 1. Core Components 🏗️

### 1.1 System Layout
```
backend/
├── app/
│   ├── core/
│   │   ├── kite_feed/                  # Kite API Integration
│   │   │   ├── connection.py           # WebSocket connection management
│   │   │   ├── auth.py                # Kite authentication
│   │   │   ├── tick_handlers/
│   │   │   │   ├── spot_handler.py    # NIFTY spot processing
│   │   │   │   ├── option_handler.py  # Options processing
│   │   │   │   └── future_handler.py  # Futures processing
│   │   │   └── exceptions.py          # Custom exceptions
│   │   ├── processors/                # Data Processing
│   │   │   ├── greeks/
│   │   │   │   ├── black_scholes.py   # Options pricing
│   │   │   │   ├── implied_vol.py     # IV calculation
│   │   │   │   └── greeks.py          # Greeks calculation
│   │   │   ├── analytics/
│   │   │   │   ├── pcr.py             # Put-Call ratio
│   │   │   │   ├── oi_analysis.py     # OI analysis
│   │   │   │   └── volatility.py      # Volatility analysis
│   │   │   └── market_depth.py        # Order book processing
│   │   └── utils/
│   │       ├── validation.py          # Data validation
│   │       └── calculations.py        # Common calculations
│   ├── models/                        # Database Models
│   │   ├── instruments.py             # Instrument definitions
│   │   ├── market_data.py            # Market data model
│   │   └── analytics.py              # Analytics models
│   ├── schemas/                       # Pydantic Schemas
│   │   ├── market_data.py            # Market data validation
│   │   ├── options.py                # Options chain schemas
│   │   └── websocket.py              # WebSocket message schemas
│   ├── api/                          # API Routes
│   │   └── v1/
│   │       ├── market_data.py        # Market data endpoints
│   │       ├── options_chain.py      # Options chain endpoints
│   │       ├── analytics.py          # Analytics endpoints
│   │       └── websocket.py          # WebSocket endpoints
│   └── services/                     # Business Logic
│       ├── market_service.py         # Market data service
│       ├── options_service.py        # Options processing
│       └── analytics_service.py      # Analytics service
```

## 2. Kite API Integration 🔌

### 2.1 Connection Management
```python
class KiteTickerManager:
    def __init__(self, access_token: str):
        self.ticker = KiteTicker(
            api_key="7vk95n09wix8psc8",
            access_token=access_token
        )
        self.instrument_tokens = set()
        self.setup_handlers()

    def setup_handlers(self):
        self.ticker.on_connect = self.on_connect
        self.ticker.on_close = self.on_disconnect
        self.ticker.on_error = self.on_error
        self.ticker.on_message = self.on_ticks
        self.ticker.on_reconnect = self.on_reconnect
        self.ticker.on_noreconnect = self.on_noreconnect

    async def subscribe_symbols(self, instruments: List[Dict]):
        """
        Subscribe to option chain instruments
        instruments: List of dicts with strike, expiry, option_type
        """
        tokens = []
        for inst in instruments:
            # Format: NIFTY24DEC24500PE
            symbol = f"NIFTY{inst['expiry']}{inst['strike']}{inst['option_type']}"
            token = await self.get_instrument_token(symbol)
            if token:
                tokens.append(token)
                self.instrument_tokens.add(token)
        
        if tokens:
            self.ticker.subscribe(tokens)
            self.ticker.set_mode(self.ticker.MODE_FULL, tokens)

    async def on_ticks(self, ws, ticks: List[Dict]):
        """
        Process incoming ticks
        Mode FULL provides: LTP, Last Traded Quantity, Average Price, Volume,
        Best Bid/Offers, Total Buy/Sell quantities
        """
        for tick in ticks:
            token = tick['instrument_token']
            
            # Market Depth (Top 5 bids/asks)
            depth = {
                'buy': [
                    {
                        'price': tick[f'depth']['buy'][i]['price'],
                        'quantity': tick[f'depth']['buy'][i]['quantity'],
                        'orders': tick[f'depth']['buy'][i]['orders'],
                    }
                    for i in range(5)
                ],
                'sell': [
                    {
                        'price': tick[f'depth']['sell'][i]['price'],
                        'quantity': tick[f'depth']['sell'][i]['quantity'],
                        'orders': tick[f'depth']['sell'][i]['orders'],
                    }
                    for i in range(5)
                ]
            }

            # Process and cache tick data
            await self.process_tick({
                'instrument_token': token,
                'last_price': tick['last_price'],
                'last_quantity': tick['last_quantity'],
                'average_price': tick['average_price'],
                'volume': tick['volume'],
                'buy_quantity': tick['buy_quantity'],
                'sell_quantity': tick['sell_quantity'],
                'oi': tick['oi'],
                'oi_day_high': tick['oi_day_high'],
                'oi_day_low': tick['oi_day_low'],
                'depth': depth
            })

    async def process_tick(self, tick_data: Dict):
        """Process and distribute tick data"""
        # Update Redis cache
        await self.cache_manager.update_tick(tick_data)
        
        # Calculate Greeks if option tick
        if self.is_option_tick(tick_data['instrument_token']):
            greeks = await self.calculate_greeks(tick_data)
            tick_data['greeks'] = greeks
        
        # Broadcast to WebSocket clients
        await self.broadcaster.broadcast_tick(tick_data)
```

### Simplified Options Chain Processor
```python
class OptionsProcessor:
    def __init__(self):
        self.spot_price = None
        self.active_strikes = set()
        self.expiry_dates = set()
    
    async def process_option_tick(self, tick: Dict[str, Any]):
        """Single method for processing option ticks"""
        # Update spot price if needed
        if tick['instrument_type'] == 'SPOT':
            self.spot_price = tick['last_price']
            return
            
        # Process option tick
        option_data = {
            'strike': tick['strike'],
            'expiry': tick['expiry'],
            'type': tick['option_type'],
            'ltp': tick['last_price'],
            'volume': tick['volume'],
            'oi': tick['oi']
        }
        
        # Calculate Greeks only when needed
        if self.should_calculate_greeks(tick):
            option_data['greeks'] = self.calculate_greeks(
                option_type=tick['option_type'],
                strike=tick['strike'],
                spot=self.spot_price,
                time_to_expiry=self.get_time_to_expiry(tick['expiry'])
            )
        
        return option_data
    
    def should_calculate_greeks(self, tick: Dict[str, Any]) -> bool:
        """Determine if Greeks calculation is needed"""
        return (
            self.spot_price is not None
            and tick['volume'] > 0  # Only for active options
            and tick['strike'] in self.active_strikes
        )
```

### Consolidated Error Handling
```python
class TradingSystemError(Exception):
    """Base exception for all trading system errors"""
    def __init__(self, message: str, error_code: str, severity: str):
        self.message = message
        self.error_code = error_code
        self.severity = severity
        super().__init__(self.message)

class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger('trading_system')
    
    async def handle_error(self, error: Exception) -> None:
        """Central error handling logic"""
        if isinstance(error, TradingSystemError):
            await self.handle_trading_error(error)
        elif isinstance(error, WebSocketDisconnect):
            await self.handle_websocket_error(error)
        elif isinstance(error, DatabaseError):
            await self.handle_database_error(error)
        else:
            await self.handle_unknown_error(error)
    
    async def handle_trading_error(self, error: TradingSystemError) -> None:
        """Handle trading-specific errors"""
        self.logger.error(f"Trading error: {error.message} [{error.error_code}]")
        if error.severity == 'critical':
            await self.notify_admin(error)
    
    async def handle_websocket_error(self, error: WebSocketDisconnect) -> None:
        """Handle WebSocket disconnections"""
        self.logger.warning(f"WebSocket disconnected: {str(error)}")
        await self.attempt_reconnection()
    
    async def handle_database_error(self, error: DatabaseError) -> None:
        """Handle database errors"""
        self.logger.error(f"Database error: {str(error)}")
        await self.ensure_database_connection()
```

{{ ... }}
KITE_API_KEY=your_api_key
KITE_API_SECRET=your_api_secretKITE_API_KEY=your_api_key
KITE_API_SECRET=your_api_secret