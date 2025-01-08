# NIFTY 50 Trading System

A high-frequency trading system for NIFTY 50 options using FastAPI and Kite Connect.

## Detailed Repository Structure 📁

```
KavasCAPITALFASTAPI-new/
├── Docs/                                # Documentation
│   ├── BACKEND_ARCHITECTURE.md          # Backend architecture details
│   ├── DATABASE_SCHEMA.md               # Database schema documentation
│   ├── DATA_PIPELINE.md                 # Data pipeline documentation
│   ├── FRONTEND_ARCHITECTURE.md         # Frontend architecture details
│   └── MERMAID.md                       # Mermaid diagrams
│
├── backend/                             # Backend Application
│   ├── app/
│   │   ├── api/                         # API endpoints
│   │   │   ├── deps.py                  # Dependency injection
│   │   │   └── v1/
│   │   │       ├── api.py               # API router
│   │   │       └── endpoints/           # API endpoint modules
│   │   │           ├── kite.py          # Kite Connect endpoints
│   │   │           ├── market_data.py   # Market data endpoints
│   │   │           └── options.py       # Options chain endpoints
│   │   │
│   │   ├── core/                        # Core functionality
│   │   │   ├── config.py                # Configuration settings
│   │   │   └── websocket_manager.py     # WebSocket management
│   │   │
│   │   ├── db/                          # Database configurations
│   │   │   ├── base.py                  # Base DB setup
│   │   │   ├── session.py               # DB session management
│   │   │   └── init_db.py               # DB initialization
│   │   │
│   │   ├── models/                      # Database models
│   │   │   ├── market_data.py           # Market data models
│   │   │   ├── option_chain.py          # Option chain models
│   │   │   └── user.py                  # User models
│   │   │
│   │   ├── repositories/                # Data access layer
│   │   │   ├── base.py                  # Base repository
│   │   │   ├── market_data.py           # Market data repository
│   │   │   └── options.py               # Options repository
│   │   │
│   │   ├── schemas/                     # Pydantic schemas
│   │   │   ├── market_data.py           # Market data schemas
│   │   │   ├── options.py               # Options schemas
│   │   │   └── websocket.py             # WebSocket schemas
│   │   │
│   │   └── services/                    # Business logic
│   │       ├── kite_service.py          # Kite Connect service
│   │       ├── market_data_service.py   # Market data service
│   │       └── websocket_manager.py     # WebSocket service
│   │
│   ├── config/                          # Configuration files
│   │   └── settings.py                  # Global settings
│   │
│   ├── .env                             # Environment variables
│   ├── requirements.txt                 # Python dependencies
│   └── run.py                           # Server startup script
│
├── frontend/                            # Frontend Application
│   ├── src/
│   │   ├── components/                  # React components
│   │   │   ├── Analysis/
│   │   │   │   └── AnalyticsPanel.tsx   # Analytics component
│   │   │   │
│   │   │   ├── Auth/
│   │   │   │   └── LoginForm.tsx        # Authentication form
│   │   │   │
│   │   │   ├── Charts/
│   │   │   │   ├── DepthChart.tsx       # Market depth chart
│   │   │   │   ├── OIChart.tsx          # Open Interest chart
│   │   │   │   └── PriceChart.tsx       # Price movement chart
│   │   │   │
│   │   │   ├── OptionChain/
│   │   │   │   ├── OptionChainGrid.tsx  # Option chain display
│   │   │   │   ├── StockInfoHeader.tsx  # Stock info header
│   │   │   │   └── hooks/
│   │   │   │       └── useOptionData.ts # Option data hook
│   │   │   │
│   │   │   ├── OrderBook/
│   │   │   │   └── OrderBook.tsx        # Order book component
│   │   │   │
│   │   │   ├── Settings/
│   │   │   │   └── Settings.tsx         # Settings panel
│   │   │   │
│   │   │   ├── Strategy/
│   │   │   │   └── StrategyBuilder.tsx  # Strategy builder
│   │   │   │
│   │   │   ├── Trade/
│   │   │   │   └── TradePanel.tsx       # Trading panel
│   │   │   │
│   │   │   └── MainContent.tsx          # Main layout component
│   │   │
│   │   ├── features/                    # Feature modules
│   │   │   ├── auth/                    # Authentication
│   │   │   ├── market/                  # Market data
│   │   │   └── options/                 # Options trading
│   │   │
│   │   ├── hooks/                       # Custom React hooks
│   │   │   ├── useMarketData.ts         # Market data hook
│   │   │   ├── useWebSocket.ts          # WebSocket hook
│   │   │   └── useAuth.ts               # Authentication hook
│   │   │
│   │   ├── services/                    # API and WebSocket services
│   │   │   ├── api/
│   │   │   │   ├── kiteAPI.ts           # Kite API service
│   │   │   │   └── marketAPI.ts         # Market data API
│   │   │   │
│   │   │   └── websocket/
│   │   │       └── WebSocketManager.ts   # WebSocket management
│   │   │
│   │   ├── store/                       # Redux store
│   │   │   ├── slices/
│   │   │   │   ├── authSlice.ts         # Auth state
│   │   │   │   ├── marketSlice.ts       # Market data state
│   │   │   │   └── optionsSlice.ts      # Options state
│   │   │   │
│   │   │   └── index.ts                 # Store configuration
│   │   │
│   │   ├── types/                       # TypeScript types
│   │   │   ├── market.ts                # Market data types
│   │   │   ├── options.ts               # Options types
│   │   │   └── common.ts                # Common types
│   │   │
│   │   ├── App.tsx                      # Root component
│   │   ├── index.tsx                    # Entry point
│   │   └── theme.ts                     # MUI theme config
│   │
│   ├── public/                          # Static files
│   │   ├── index.html                   # HTML template
│   │   └── favicon.ico                  # Favicon
│   │
│   ├── .env                             # Frontend environment variables
│   ├── package.json                     # NPM dependencies
│   └── tsconfig.json                    # TypeScript configuration
│
└── requirements.txt                      # Global Python dependencies
```

## Features 🚀

- Real-time market data streaming via WebSocket
- Complete options chain management
- Advanced market depth tracking
- Interactive charts for price and OI analysis
- Time-series data storage with PostgreSQL
- High-performance caching with Redis
- Responsive Material-UI based frontend
- TypeScript for type safety
- Redux for state management
- WebSocket integration for live updates

## Prerequisites 📋

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Kite Connect API credentials
- Node.js 14+
- npm 6+

## Installation 🔧

1. Clone the repository:
```bash
git clone <repository-url>
cd KavasCAPITALFASTAPI-new
```

2. Set up backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up frontend:
```bash
cd frontend
npm install
```

4. Configure environment variables:
- Copy `backend/.env.example` to `backend/.env`
- Copy `frontend/.env.example` to `frontend/.env`
- Update the values in both .env files

## Running the Application 🚀

1. Start the backend server:
```bash
cd backend
python -m app.main
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

The application will be available at:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs

## API Documentation 📚

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development 👨‍💻

- Backend uses FastAPI with async support
- Frontend uses React with TypeScript
- WebSocket for real-time data
- Redux for state management
- Material-UI for components

## Testing 🧪

1. Backend tests:
```bash
cd backend
pytest
```

2. Frontend tests:
```bash
cd frontend
npm test
```

## Contributing 🤝

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
