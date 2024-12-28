export interface MarketData {
    instrument_token: number;
    timestamp: string;
    last_price: number;
    volume: number;
    buy_quantity?: number;
    sell_quantity?: number;
    open?: number;
    high?: number;
    low?: number;
    close?: number;
    change?: number;
    oi?: number;
    oi_day_high?: number;
    oi_day_low?: number;
}

export interface DepthData {
    instrument_token: number;
    timestamp: string;
    depth_level: number;
    buy_price: number;
    buy_quantity: number;
    buy_orders: number;
    sell_price: number;
    sell_quantity: number;
    sell_orders: number;
}

export interface MarketDepth {
    buys: DepthData[];
    sells: DepthData[];
}
