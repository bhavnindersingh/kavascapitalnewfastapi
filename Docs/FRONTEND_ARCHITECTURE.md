# NIFTY 50 HFT System - Frontend Architecture

## 1. Project Structure 🏗️

```
frontend/
├── src/
│   ├── components/                 # Reusable UI Components
│   │   ├── OptionChain/           # Options Chain Components
│   │   │   ├── OptionChainGrid.tsx
│   │   │   ├── StrikeRow.tsx
│   │   │   ├── GreeksDisplay.tsx
│   │   │   └── ExpirySelector.tsx
│   │   ├── Charts/                # Chart Components
│   │   │   ├── SpotChart.tsx
│   │   │   ├── VolatilitySurface.tsx
│   │   │   ├── OIChart.tsx
│   │   │   └── DepthChart.tsx
│   │   ├── OrderBook/             # Order Book Components
│   │   │   ├── OrderBookDisplay.tsx
│   │   │   ├── DepthView.tsx
│   │   │   └── TradesView.tsx
│   │   └── common/                # Common UI Elements
│   │       ├── DataGrid.tsx
│   │       ├── LoadingSpinner.tsx
│   │       └── ErrorBoundary.tsx
│   ├── features/                  # Feature Modules
│   │   ├── optionChain/
│   │   │   ├── hooks/
│   │   │   │   ├── useOptionChainData.ts
│   │   │   │   └── useGreeksCalculation.ts
│   │   │   ├── store/
│   │   │   │   └── optionChainSlice.ts
│   │   │   └── utils/
│   │   │       └── optionHelpers.ts
│   │   ├── marketData/
│   │   │   ├── hooks/
│   │   │   │   ├── useMarketData.ts
│   │   │   │   └── useDepthData.ts
│   │   │   ├── store/
│   │   │   │   └── marketDataSlice.ts
│   │   │   └── utils/
│   │   │       └── dataTransforms.ts
│   │   └── analytics/
│   │       ├── hooks/
│   │       │   ├── useAnalytics.ts
│   │       │   └── useChartData.ts
│   │       └── store/
│   │           └── analyticsSlice.ts
│   ├── services/                  # API & WebSocket Services
│   │   ├── api/
│   │   │   ├── marketDataApi.ts
│   │   │   ├── optionsApi.ts
│   │   │   └── analyticsApi.ts
│   │   └── websocket/
│   │       ├── WebSocketManager.ts
│   │       └── messageHandlers.ts
│   ├── store/                    # Global State Management
│   │   ├── store.ts
│   │   └── rootReducer.ts
│   ├── types/                    # TypeScript Definitions
│   │   ├── marketData.ts
│   │   ├── options.ts
│   │   └── common.ts
│   └── utils/                    # Utility Functions
│       ├── formatting.ts
│       ├── calculations.ts
│       └── constants.ts
```

## 2. Kite Integration 🔌

### 2.1 Access Token Management
```typescript
// Token Management
interface KiteConfig {
    apiKey: string;
    accessToken: string;
}

const KiteConfigContext = createContext<KiteConfig | null>(null);

// Token Provider Component
export const KiteConfigProvider: React.FC = ({ children }) => {
    const [config, setConfig] = useState<KiteConfig | null>(null);

    const updateAccessToken = (token: string) => {
        setConfig(prev => ({
            ...prev!,
            accessToken: token
        }));
        localStorage.setItem('kite_access_token', token);
    };

    useEffect(() => {
        // Load saved token on startup
        const savedToken = localStorage.getItem('kite_access_token');
        if (savedToken) {
            setConfig({
                apiKey: "7vk95n09wix8psc8",
                accessToken: savedToken
            });
        }
    }, []);

    return (
        <KiteConfigContext.Provider value={config}>
            {children}
        </KiteConfigContext.Provider>
    );
};

// Access Token Input Component
const AccessTokenInput: React.FC = () => {
    const [token, setToken] = useState('');
    const { updateAccessToken } = useContext(KiteConfigContext);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (token) {
            updateAccessToken(token);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="Enter Kite Access Token"
            />
            <button type="submit">Update Token</button>
        </form>
    );
};
```

### 2.2 Simplified WebSocket Management
```typescript
class WebSocketManager {
    private ws: WebSocket | null = null;
    private reconnectTimer: number | null = null;
    private messageHandlers = new Map<string, (data: any) => void>();

    constructor(private url: string) {
        this.connect();
    }

    private connect() {
        this.ws = new WebSocket(this.url);
        this.setupEventHandlers();
    }

    private setupEventHandlers() {
        if (!this.ws) return;

        this.ws.onopen = () => {
            console.log('Connected to WebSocket');
            this.clearReconnectTimer();
        };

        this.ws.onclose = () => {
            console.log('WebSocket connection closed');
            this.scheduleReconnect();
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const handler = this.messageHandlers.get(data.type);
            if (handler) handler(data);
        };
    }

    private scheduleReconnect() {
        if (this.reconnectTimer) return;
        this.reconnectTimer = window.setTimeout(() => {
            this.connect();
        }, 3000);
    }

    private clearReconnectTimer() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
    }

    public subscribe(type: string, handler: (data: any) => void) {
        this.messageHandlers.set(type, handler);
    }

    public unsubscribe(type: string) {
        this.messageHandlers.delete(type);
    }
}
```

### 2.3 Consolidated Redux Store
```typescript
// Single slice for market data
interface MarketState {
    ticks: Record<string, TickData>;
    depth: Record<string, DepthData>;
    vix: VIXData | null;
    status: 'idle' | 'loading' | 'succeeded' | 'failed';
    error: string | null;
}

const marketSlice = createSlice({
    name: 'market',
    initialState: {
        ticks: {},
        depth: {},
        vix: null,
        status: 'idle',
        error: null
    } as MarketState,
    reducers: {
        updateTick(state, action: PayloadAction<TickData>) {
            state.ticks[action.payload.symbol] = action.payload;
        },
        updateDepth(state, action: PayloadAction<DepthData>) {
            state.depth[action.payload.symbol] = action.payload;
        },
        updateVIX(state, action: PayloadAction<VIXData>) {
            state.vix = action.payload;
        },
        setStatus(state, action: PayloadAction<MarketState['status']>) {
            state.status = action.payload;
        },
        setError(state, action: PayloadAction<string>) {
            state.error = action.payload;
            state.status = 'failed';
        }
    }
});
```

### 2.4 Real-time Data Management

```typescript
// Efficient WebSocket data handling with rate limiting
class TickDataManager {
    private tickBuffer: Map<string, KiteOptionTick> = new Map();
    private updateCallbacks: Set<(data: Map<string, KiteOptionTick>) => void> = new Set();
    private batchSize: number = 50;  // Number of updates to batch
    private updateInterval: number = 100;  // Milliseconds between updates
    private updateTimeout: NodeJS.Timeout | null = null;

    constructor() {
        // Start the update loop
        this.startUpdateLoop();
    }

    private startUpdateLoop() {
        setInterval(() => {
            if (this.tickBuffer.size > 0) {
                this.flushUpdates();
            }
        }, this.updateInterval);
    }

    addTick(symbol: string, tick: KiteOptionTick) {
        this.tickBuffer.set(symbol, tick);
        
        if (this.tickBuffer.size >= this.batchSize) {
            this.flushUpdates();
        }
    }

    private flushUpdates() {
        // Notify all subscribers with the current batch
        this.updateCallbacks.forEach(callback => {
            callback(new Map(this.tickBuffer));
        });
        
        // Clear the buffer
        this.tickBuffer.clear();
    }

    subscribe(callback: (data: Map<string, KiteOptionTick>) => void) {
        this.updateCallbacks.add(callback);
        return () => this.updateCallbacks.delete(callback);
    }
}

// Option Chain State Management
class OptionChainState {
    private static instance: OptionChainState;
    private dataManager: TickDataManager;
    private optionData: Map<string, OptionData> = new Map();
    private subscribers: Map<string, Set<(data: OptionData) => void>> = new Map();

    private constructor() {
        this.dataManager = new TickDataManager();
        this.dataManager.subscribe(this.handleTickBatch.bind(this));
    }

    static getInstance(): OptionChainState {
        if (!OptionChainState.instance) {
            OptionChainState.instance = new OptionChainState();
        }
        return OptionChainState.instance;
    }

    private handleTickBatch(ticks: Map<string, KiteOptionTick>) {
        ticks.forEach((tick, symbol) => {
            // Update option data
            const currentData = this.optionData.get(symbol) || this.createEmptyOptionData(symbol);
            const updatedData = this.updateOptionData(currentData, tick);
            this.optionData.set(symbol, updatedData);

            // Notify subscribers
            const symbolSubscribers = this.subscribers.get(symbol);
            if (symbolSubscribers) {
                symbolSubscribers.forEach(callback => callback(updatedData));
            }
        });
    }

    private updateOptionData(current: OptionData, tick: KiteOptionTick): OptionData {
        return {
            ...current,
            lastPrice: tick.last_price,
            volume: tick.volume,
            oi: tick.oi,
            depth: tick.depth,
            timestamp: new Date().getTime()
        };
    }

    subscribe(symbol: string, callback: (data: OptionData) => void) {
        if (!this.subscribers.has(symbol)) {
            this.subscribers.set(symbol, new Set());
        }
        this.subscribers.get(symbol)!.add(callback);
        
        // Initial data
        const currentData = this.optionData.get(symbol);
        if (currentData) {
            callback(currentData);
        }

        return () => this.subscribers.get(symbol)?.delete(callback);
    }
}

// React Hook for Option Chain Data
function useOptionChainData(symbols: string[]) {
    const [data, setData] = useState<Map<string, OptionData>>(new Map());
    const optionChainState = useMemo(() => OptionChainState.getInstance(), []);

    useEffect(() => {
        const unsubscribes = symbols.map(symbol => 
            optionChainState.subscribe(symbol, (newData) => {
                setData(prev => new Map(prev).set(symbol, newData));
            })
        );

        return () => unsubscribes.forEach(unsub => unsub());
    }, [symbols]);

    return data;
}

// Option Chain Grid with Optimized Rendering
const OptionChainGrid: React.FC<{
    spotPrice: number;
    strikes: number[];
    expiry: string;
}> = memo(({ spotPrice, strikes, expiry }) => {
    const symbols = useMemo(() => 
        strikes.flatMap(strike => [
            `NIFTY${expiry}${strike}CE`,
            `NIFTY${expiry}${strike}PE`
        ]),
        [strikes, expiry]
    );

    const optionData = useOptionChainData(symbols);

    return (
        <div className="option-chain-grid">
            <div className="calls-section">
                {strikes.map(strike => (
                    <MemoizedOptionRow
                        key={`call-${strike}`}
                        data={optionData.get(`NIFTY${expiry}${strike}CE`)}
                        type="CE"
                    />
                ))}
            </div>
            <div className="strikes-section">
                {strikes.map(strike => (
                    <div key={strike} className="strike-price">
                        {strike}
                    </div>
                ))}
            </div>
            <div className="puts-section">
                {strikes.map(strike => (
                    <MemoizedOptionRow
                        key={`put-${strike}`}
                        data={optionData.get(`NIFTY${expiry}${strike}PE`)}
                        type="PE"
                    />
                ))}
            </div>
        </div>
    );
});

// Optimized Option Row Component
const OptionRow: React.FC<{
    data?: OptionData;
    type: 'CE' | 'PE';
}> = memo(({ data, type }) => {
    if (!data) return null;

    return (
        <div className={`option-row ${type.toLowerCase()}`}>
            <div>{data.lastPrice}</div>
            <div>{data.volume}</div>
            <div>{data.oi}</div>
            <MarketDepthTooltip depth={data.depth} />
        </div>
    );
}, (prev, next) => {
    // Custom comparison for memoization
    if (!prev.data || !next.data) return prev.data === next.data;
    return (
        prev.data.lastPrice === next.data.lastPrice &&
        prev.data.volume === next.data.volume &&
        prev.data.oi === next.data.oi
    );
});

const MemoizedOptionRow = memo(OptionRow);
```

## 3. Component Architecture 🎨

### 3.1 Option Chain Grid
```typescript
// Types
interface OptionData {
    symbol: string;        // e.g., "NIFTY24DEC24500PE"
    lastPrice: number;
    change: number;
    volume: number;
    oi: number;
    iv?: number;
    greeks?: {
        delta: number;
        gamma: number;
        theta: number;
        vega: number;
    };
}

interface MarketDepth {
    buyQuotes: Array<{
        price: number;
        quantity: number;
        orders: number;
    }>;
    sellQuotes: Array<{
        price: number;
        quantity: number;
        orders: number;
    }>;
}

// Option Chain Grid Component
const OptionChainGrid: React.FC = () => {
    const [selectedExpiry, setSelectedExpiry] = useState<string>();
    const [hoveredOption, setHoveredOption] = useState<string>();
    
    const { data: optionChain } = useOptionChainData(selectedExpiry);
    const { data: marketDepth } = useMarketDepth(hoveredOption);
    
    return (
        <div className="option-chain-container">
            <ExpirySelector 
                value={selectedExpiry}
                onChange={setSelectedExpiry}
            />
            <div className="option-chain-grid">
                <div className="calls-section">
                    {optionChain.strikes.map(strike => (
                        <OptionRow
                            key={strike}
                            data={optionChain.calls[strike]}
                            onMouseEnter={() => setHoveredOption(optionChain.calls[strike].symbol)}
                        />
                    ))}
                </div>
                <div className="strikes-section">
                    {optionChain.strikes.map(strike => (
                        <div key={strike} className="strike-price">
                            {strike}
                        </div>
                    ))}
                </div>
                <div className="puts-section">
                    {optionChain.strikes.map(strike => (
                        <OptionRow
                            key={strike}
                            data={optionChain.puts[strike]}
                            onMouseEnter={() => setHoveredOption(optionChain.puts[strike].symbol)}
                        />
                    ))}
                </div>
            </div>
            {hoveredOption && (
                <MarketDepthPopover
                    data={marketDepth}
                    position={mousePosition}
                />
            )}
        </div>
    );
};

// Market Depth Popover
const MarketDepthPopover: React.FC<{
    data: MarketDepth;
    position: { x: number; y: number };
}> = ({ data, position }) => {
    return (
        <div 
            className="market-depth-popover"
            style={{
                position: 'absolute',
                left: position.x,
                top: position.y
            }}
        >
            <div className="depth-section buy">
                <h4>Buy Quotes</h4>
                {data.buyQuotes.map((quote, idx) => (
                    <div key={idx} className="depth-row">
                        <span>{quote.price}</span>
                        <span>{quote.quantity}</span>
                        <span>{quote.orders}</span>
                    </div>
                ))}
            </div>
            <div className="depth-section sell">
                <h4>Sell Quotes</h4>
                {data.sellQuotes.map((quote, idx) => (
                    <div key={idx} className="depth-row">
                        <span>{quote.price}</span>
                        <span>{quote.quantity}</span>
                        <span>{quote.orders}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

// Styles
const styles = css`
    .option-chain-container {
        position: relative;
        width: 100%;
        overflow: auto;
    }

    .option-chain-grid {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        gap: 1px;
        background: #f5f5f5;
    }

    .market-depth-popover {
        position: absolute;
        background: white;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        padding: 8px;
        z-index: 1000;
        
        .depth-section {
            margin-bottom: 8px;
            
            &.buy {
                color: #0b7b3e;
            }
            
            &.sell {
                color: #d32f2f;
            }
        }
        
        .depth-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            font-size: 12px;
            padding: 2px 0;
        }
    }
`;
```

### 3.2 Real-time Charts
```typescript
// Chart Components with WebSocket Integration
const SpotPriceChart: React.FC = () => {
    const { data, isLoading } = useMarketData();
    const chartRef = useRef<ChartInstance>();
    
    useEffect(() => {
        if (data && chartRef.current) {
            updateChart(chartRef.current, data);
        }
    }, [data]);
    
    return (
        <div className="chart-container">
            <canvas ref={chartRef} />
        </div>
    );
};
```

## 4. Real-time Data Handling 📊

### 4.1 WebSocket Integration
```typescript
// WebSocket Hook
function useWebSocket<T>(
    channel: string,
    handler: (data: T) => void
): WebSocketStatus {
    useEffect(() => {
        const ws = WebSocketManager.getInstance();
        ws.subscribe(channel, handler);
        
        return () => {
            ws.unsubscribe(channel, handler);
        };
    }, [channel, handler]);
    
    return WebSocketManager.status;
}
```

### 4.2 Data Transformation
```typescript
// Market Data Transformer
class MarketDataTransformer {
    static transformOptionChain(data: RawOptionData): ProcessedOptionData {
        return {
            calls: this.processOptions(data.CE),
            puts: this.processOptions(data.PE),
            timestamp: data.timestamp
        };
    }
    
    private static processOptions(options: RawOption[]): ProcessedOption[] {
        return options.map(option => ({
            strike: option.strike_price,
            last_price: option.last_price,
            change: this.calculateChange(option),
            oi: option.oi,
            volume: option.volume,
            iv: option.iv
        }));
    }
}
```

## 5. Performance Optimizations 🚀

### 5.1 React Optimization
```typescript
// Memoization Strategy
const MemoizedOptionRow = React.memo(OptionRow, (prev, next) => {
    return (
        prev.strike === next.strike &&
        prev.data.last_price === next.data.last_price &&
        prev.data.oi === next.data.oi
    );
});

// Virtual Scrolling
const VirtualizedOptionChain: React.FC<Props> = ({ items }) => {
    return (
        <VirtualList
            height={800}
            itemCount={items.length}
            itemSize={35}
            width={1200}
        >
            {({ index, style }) => (
                <OptionRow
                    data={items[index]}
                    style={style}
                />
            )}
        </VirtualList>
    );
};
```

### 5.2 Data Management
```typescript
// Efficient Updates
class DataManager {
    private static instance: DataManager;
    private cache: Map<string, CachedData>;
    
    updateData(newData: MarketData) {
        // Update only changed values
        const cached = this.cache.get(newData.id);
        if (this.hasChanged(cached, newData)) {
            this.cache.set(newData.id, newData);
            this.notifySubscribers(newData.id);
        }
    }
    
    private hasChanged(old: CachedData, new: MarketData): boolean {
        return !old || old.price !== new.price || old.oi !== new.oi;
    }
}
```

## 6. UI/UX Design 🎨

### 6.1 Theme Configuration
```typescript
// Theme Configuration
const theme = {
    colors: {
        primary: '#1a73e8',
        secondary: '#7b1fa2',
        positive: '#0f9d58',
        negative: '#d93025',
        background: '#f8f9fa',
        text: '#202124'
    },
    typography: {
        fontFamily: 'Inter, system-ui, sans-serif',
        fontSize: {
            small: '12px',
            medium: '14px',
            large: '16px'
        }
    },
    spacing: {
        small: '8px',
        medium: '16px',
        large: '24px'
    }
};
```

### 6.2 Responsive Design
```typescript
// Responsive Grid Layout
const OptionChainGrid = styled.div`
    display: grid;
    grid-template-columns: 
        repeat(auto-fit, minmax(120px, 1fr));
    gap: ${props => props.theme.spacing.small};
    
    @media (max-width: 768px) {
        grid-template-columns: 1fr;
    }
`;
```

## 7. Error Handling & Recovery 🔧

### 7.1 Error Boundaries
```typescript
class ErrorBoundary extends React.Component<Props, State> {
    static getDerivedStateFromError(error: Error) {
        return { hasError: true, error };
    }
    
    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        logError(error, errorInfo);
    }
    
    render() {
        if (this.state.hasError) {
            return <ErrorFallback error={this.state.error} />;
        }
        return this.props.children;
    }
}
```

### 7.2 Connection Recovery
```typescript
// WebSocket Reconnection
class WebSocketReconnector {
    private retryCount: number = 0;
    private maxRetries: number = 5;
    
    async reconnect() {
        if (this.retryCount >= this.maxRetries) {
            throw new Error('Max retries exceeded');
        }
        
        const delay = Math.min(1000 * Math.pow(2, this.retryCount), 10000);
        await this.wait(delay);
        
        try {
            await this.connect();
            this.retryCount = 0;
        } catch (error) {
            this.retryCount++;
            await this.reconnect();
        }
    }
}
```

## 8. Testing Strategy 🧪

### 8.1 Component Testing
```typescript
// Component Test Example
describe('OptionChainGrid', () => {
    it('renders option chain data correctly', () => {
        const mockData = generateMockOptionData();
        const { getByText } = render(
            <OptionChainGrid data={mockData} />
        );
        
        expect(getByText('Strike')).toBeInTheDocument();
        expect(getByText('Call')).toBeInTheDocument();
        expect(getByText('Put')).toBeInTheDocument();
    });
});
```

### 8.2 Integration Testing
```typescript
// WebSocket Integration Test
describe('WebSocket Integration', () => {
    it('handles market data updates', async () => {
        const mockWebSocket = new MockWebSocket();
        const { result } = renderHook(() => 
            useMarketData(mockWebSocket)
        );
        
        act(() => {
            mockWebSocket.emit('message', mockMarketData);
        });
        
        expect(result.current.data).toEqual(mockMarketData);
    });
});
```

### 3.2 WebSocket Data Handling
```typescript
// Option Chain Data Hook
function useOptionChainData(expiry: string) {
    const [data, setData] = useState<OptionChainData>();
    
    useEffect(() => {
        const ws = new WebSocket(WS_URL);
        
        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === 'option_update') {
                setData(prev => ({
                    ...prev,
                    [message.strike]: {
                        ...prev[message.strike],
                        [message.optionType]: message.data
                    }
                }));
            }
        };
        
        return () => ws.close();
    }, [expiry]);
    
    return { data };
}

// Market Depth Hook
function useMarketDepth(symbol: string) {
    const [depth, setDepth] = useState<MarketDepth>();
    
    useEffect(() => {
        if (!symbol) return;
        
        const ws = new WebSocket(WS_URL);
        
        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === 'market_depth' && message.symbol === symbol) {
                setDepth(message.data);
            }
        };
        
        // Subscribe to market depth
        ws.send(JSON.stringify({
            type: 'subscribe_depth',
            symbol
        }));
        
        return () => ws.close();
    }, [symbol]);
    
    return { depth };
}
