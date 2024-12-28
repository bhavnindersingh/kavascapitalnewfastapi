# NIFTY 50 Trading System Architecture

## 1. High-Level System Overview
```mermaid
graph TB
    Frontend[Frontend Layer] --> API[API Layer]
    API --> Services[Service Layer]
    Services --> Database[Database Layer]
    Services --> External[External Services]
    
    subgraph Frontend
        UI[User Interface] --> State[State Management]
        State --> WS[WebSocket Client]
    end
    
    subgraph API
        REST[REST Endpoints] --> Auth[Authentication]
        WSS[WebSocket Server] --> Auth
    end
    
    subgraph Services
        Trade[Trading Service] --> Market[Market Service]
        Market --> Analytics[Analytics Service]
    end
    
    subgraph Database
        PG[PostgreSQL] --> Redis[Redis Cache]
        Redis --> TS[TimescaleDB]
    end
    
    subgraph External
        Kite[Zerodha Kite] --> NSE[NSE Feed]
    end

    classDef frontend fill:#f9f,stroke:#333
    classDef api fill:#bbf,stroke:#333
    classDef service fill:#bfb,stroke:#333
    classDef db fill:#fbb,stroke:#333
    classDef external fill:#ddd,stroke:#333

    class Frontend,UI,State,WS frontend
    class API,REST,WSS,Auth api
    class Services,Trade,Market,Analytics service
    class Database,PG,Redis,TS db
    class External,Kite,NSE external
```

## 2. Data Flow
```mermaid
sequenceDiagram
    participant UI as Frontend
    participant API as FastAPI
    participant KWS as Kite WS
    participant DB as Database
    participant Cache as Redis

    UI->>API: Connect WebSocket
    API->>KWS: Subscribe Market Data
    
    loop Market Data
        KWS->>API: Send Tick
        API->>Cache: Update Cache
        API->>DB: Batch Insert
        API->>UI: Broadcast Update
    end

    par Trading Flow
        UI->>API: Place Order
        API->>KWS: Execute Trade
        KWS-->>API: Confirmation
        API-->>UI: Order Status
    end
```

## 3. Database Schema
```mermaid
erDiagram
    INSTRUMENTS ||--o{ MARKET_DATA : has
    INSTRUMENTS ||--o{ ORDERS : creates
    ORDERS ||--o{ POSITIONS : affects

    INSTRUMENTS {
        int token PK
        string symbol
        string type
        float strike
        timestamp expiry
    }

    MARKET_DATA {
        bigint id PK
        int token FK
        timestamp time
        float price
        int volume
    }

    ORDERS {
        bigint id PK
        int token FK
        float price
        int quantity
        string status
    }
```

## 4. Infrastructure
```mermaid
graph TB
    subgraph K8s[Kubernetes Cluster]
        API[API Pods] --> DB[Database]
        API --> Cache[Redis]
        API --> Monitor[Monitoring]
    end

    subgraph Network
        LB[Load Balancer] --> WAF[Web Firewall]
        WAF --> SSL[SSL/TLS]
    end

    K8s --> Network

    classDef k8s fill:#bbf,stroke:#333
    classDef net fill:#fbb,stroke:#333

    class K8s,API,DB,Cache,Monitor k8s
    class Network,LB,WAF,SSL net
```

## 5. Data Processing
```mermaid
flowchart TB
    Input[Market Data Input] --> Process[Processing]
    Process --> Storage[Storage]
    Process --> Cache[Cache]
    
    subgraph Process
        Valid[Validation] --> Norm[Normalization]
        Norm --> Filter[Filtering]
        Filter --> Agg[Aggregation]
    end

    Cache --> Output[Data Output]
    Storage --> Output

    classDef input fill:#f96,stroke:#333
    classDef process fill:#bbf,stroke:#333
    classDef storage fill:#bfb,stroke:#333
    classDef output fill:#f9f,stroke:#333

    class Input input
    class Process,Valid,Norm,Filter,Agg process
    class Storage,Cache storage
    class Output output
