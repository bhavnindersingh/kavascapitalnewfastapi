export interface MarketData {
    instrument_token: number;
    timestamp: string;
    last_price: number;
    volume: number;
    buy_quantity: number;
    sell_quantity: number;
    oi?: number;
}

export interface MarketDepth {
    buys: Array<{
        buy_quantity: number;
        buy_price: number;
    }>;
    sells: Array<{
        sell_quantity: number;
        sell_price: number;
    }>;
}

export interface OptionData {
    instrument_token: number;
    strike: number;
    expiry: string;
    last_price: number;
    volume: number;
    oi: number;
    iv: number;
    delta: number;
    theta: number;
    change: number;
}

export interface OptionChainData {
    expiry_dates: string[];
    strikes: number[];
    spot_price: number;
    options: {
        [key: string]: OptionData;
    };
}
