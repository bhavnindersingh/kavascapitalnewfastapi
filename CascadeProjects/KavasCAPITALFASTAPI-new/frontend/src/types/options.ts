// Stock information
export interface StockInfo {
    symbol: string;
    name: string;
    ltp: number;
    change: number;
    volume: number;
    oi: number;
    lotSize: number;
    future: number;
    vix: number;
}

// Option data
export interface OptionData {
    strike: number;
    instrument_token: number;
    ltp: number;
    change: number;
    volume: number;
    oi: number;
    oiChange: number;
    iv: number;
    bidQty: number;
    askQty: number;
    expiry: string;
}

// Strike data
export interface StrikeData {
    strike: number;
    strikePrice: number;
    call?: OptionData;
    put?: OptionData;
}

// Complete option chain data
export interface OptionChainData {
    stockInfo: StockInfo;
    strikes: StrikeData[];
}

// Market data from WebSocket
export interface MarketData {
    instrument_token: number;
    last_price: number;
    change: number;
    volume: number;
    oi: number;
    oiChange: number;
    iv: number;
    bidQty: number;
    askQty: number;
    timestamp: string;
}

// WebSocket message types
export type WSMessageType = 'MARKET_DATA' | 'OPTION_CHAIN' | 'ERROR' | 'pong';

// WebSocket message
export interface WSMessage {
    type: WSMessageType;
    data?: MarketData | OptionChainData;
    error?: string;
}

// API Response Types
export interface OptionChain {
    stockInfo: StockInfo;
    strikes: StrikeData[];
    expiryDates?: string[];
}
