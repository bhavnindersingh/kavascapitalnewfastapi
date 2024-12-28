import { WSMessage } from '../types/options';

class WebSocketService {
    private ws: WebSocket | null = null;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private reconnectTimeout = 3000; // 3 seconds
    private messageHandlers: ((message: WSMessage) => void)[] = [];
    private subscribedInstruments: Set<number> = new Set();
    private currentSymbol: string | null = null;
    private currentExpiry: string | null = null;

    constructor() {
        this.connect = this.connect.bind(this);
        this.disconnect = this.disconnect.bind(this);
        this.sendMessage = this.sendMessage.bind(this);
        this.addMessageHandler = this.addMessageHandler.bind(this);
        this.removeMessageHandler = this.removeMessageHandler.bind(this);
        this.subscribe = this.subscribe.bind(this);
        this.unsubscribe = this.unsubscribe.bind(this);
    }

    connect(symbol: string, expiry: string) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.disconnect();
        }

        const token = localStorage.getItem('kite_access_token');
        if (!token) {
            console.error('No access token found. Please login first.');
            return;
        }

        this.currentSymbol = symbol;
        this.currentExpiry = expiry;

        const wsUrl = `ws://localhost:8000/options/${symbol}/${expiry}?token=${token}`;
        console.log('Connecting to WebSocket:', wsUrl);
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
            // Subscribe to option chain updates
            this.sendMessage({
                type: 'subscribe'
            });
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.messageHandlers.forEach(handler => handler(message));
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                console.log(`Reconnecting... Attempt ${this.reconnectAttempts + 1}/${this.maxReconnectAttempts}`);
                this.reconnectAttempts++;
                setTimeout(() => {
                    if (this.currentSymbol && this.currentExpiry) {
                        this.connect(this.currentSymbol, this.currentExpiry);
                    }
                }, this.reconnectTimeout);
            }
        };
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.subscribedInstruments.clear();
        this.currentSymbol = null;
        this.currentExpiry = null;
    }

    sendMessage(message: any) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket is not connected');
        }
    }

    addMessageHandler(handler: (message: WSMessage) => void) {
        this.messageHandlers.push(handler);
    }

    removeMessageHandler(handler: (message: WSMessage) => void) {
        const index = this.messageHandlers.indexOf(handler);
        if (index !== -1) {
            this.messageHandlers.splice(index, 1);
        }
    }

    subscribe(instruments: number | number[]) {
        if (!instruments) {
            console.error('Instruments are required for subscription');
            return;
        }

        const instrumentArray = Array.isArray(instruments) ? instruments : [instruments];
        if (!instrumentArray.every(token => typeof token === 'number')) {
            console.error('Invalid instrument token(s)');
            return;
        }

        instrumentArray.forEach(token => this.subscribedInstruments.add(token));
        this.sendMessage({
            type: 'subscribe',
            instruments: instrumentArray
        });
        console.log(`Subscribed to instruments: ${instrumentArray.join(', ')}`);
    }

    unsubscribe(instruments: number | number[]) {
        if (!instruments) {
            console.error('Instruments are required for unsubscription');
            return;
        }

        const instrumentArray = Array.isArray(instruments) ? instruments : [instruments];
        if (!instrumentArray.every(token => typeof token === 'number')) {
            console.error('Invalid instrument token(s)');
            return;
        }

        instrumentArray.forEach(token => this.subscribedInstruments.delete(token));
        this.sendMessage({
            type: 'unsubscribe',
            instruments: instrumentArray
        });
        console.log(`Unsubscribed from instruments: ${instrumentArray.join(', ')}`);
    }
}

export const webSocketService = new WebSocketService();
