export class WebSocketManager {
    private ws: WebSocket | null = null;
    private reconnectTimer: number | null = null;
    private messageHandlers = new Map<string, (data: any) => void>();
    private url: string;
    private clientId: string;

    constructor(url: string, clientId: string) {
        this.url = url;
        this.clientId = clientId;
    }

    public connect() {
        if (this.ws?.readyState === WebSocket.OPEN) {
            return;
        }

        this.ws = new WebSocket(`${this.url}/ws/${this.clientId}`);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            if (this.reconnectTimer) {
                clearTimeout(this.reconnectTimer);
                this.reconnectTimer = null;
            }
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                const handler = this.messageHandlers.get(message.type);
                if (handler) {
                    handler(message.data);
                }
            } catch (error) {
                console.error('Error processing WebSocket message:', error);
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.scheduleReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.ws?.close();
        };
    }

    public subscribe(instruments: string[]) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'subscribe',
                instruments
            }));
        }
    }

    public addMessageHandler(type: string, handler: (data: any) => void) {
        this.messageHandlers.set(type, handler);
    }

    public removeMessageHandler(type: string) {
        this.messageHandlers.delete(type);
    }

    private scheduleReconnect() {
        if (!this.reconnectTimer) {
            this.reconnectTimer = window.setTimeout(() => {
                this.connect();
            }, 5000);
        }
    }

    public disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
    }
}
