# NIFTY Option Chain System Data Flow 🔄

## Overview

This document outlines the complete data flow architecture of our NIFTY option chain system, from market data ingestion to frontend display.

## 1. System Architecture Overview

```mermaid
graph TB
    KA[Kite API] -->|WebSocket| BE[Backend System]
    BE -->|Store| RD[(Redis)]
    BE -->|Store| PG[(PostgreSQL)]
    BE -->|WebSocket| FE[Frontend System]
    BE -->|REST API| FE
    
    subgraph Backend System
        WS[WebSocket Manager]
        DP[Data Processor]
        API[API Layer]
    end
    
    subgraph Frontend System
        WC[WebSocket Client]
        RC[REST Client]
        RX[Redux Store]
        UI[UI Components]
    end
    
    classDef primary fill:#f9f,stroke:#333,stroke-width:2px
    classDef storage fill:#bbf,stroke:#333,stroke-width:2px
    
    class KA,BE,FE primary
    class RD,PG storage
```

## 2. Backend Data Flow

### 2.1 Data Ingestion Layer
```mermaid
flowchart TB
    KW[Kite WebSocket] --> WM[WebSocket Manager]
    WM --> |Raw Data| MP[Market Processor]
    
    MP --> |Process| SD[Spot Data]
    MP --> |Process| OD[Option Data]
    MP --> |Process| VD[VIX Data]
    
    SD --> |Store| RD[(Redis)]
    OD --> |Store| RD
    VD --> |Store| RD
    
    SD --> |Archive| PG[(PostgreSQL)]
    OD --> |Archive| PG
    VD --> |Archive| PG
```

### 2.2 Storage Layer
```mermaid
flowchart LR
    subgraph Redis Hot Data
        RC[Current Option Chain]
        RM[Active Market Data]
        RT[Recent Ticks]
    end
    
    subgraph PostgreSQL Historical
        PH[Tick History]
        PE[EOD Data]
        PS[Market Statistics]
    end
```

### 2.3 API Layer
```mermaid
flowchart TB
    subgraph WebSocket Server
        WL[Live Market Updates]
        WO[Option Chain Updates]
        WT[Trade Notifications]
    end
    
    subgraph REST Endpoints
        RA[Authentication]
        RH[Historical Data]
        RN[Analytics]
    end
```

## 3. Frontend Data Flow

### 3.1 State Management
```mermaid
flowchart TB
    subgraph Redux Store
        MD[Market Data]
        OC[Option Chain]
        UP[User Preferences]
        US[UI State]
    end
    
    WS[WebSocket] --> MD & OC
    REST[REST API] --> UP & US
```

### 3.2 Component Data Flow
```mermaid
flowchart TB
    subgraph Market View
        SP[Spot Price]
        FP[Future Price]
        CH[Charts]
    end
    
    subgraph Option Chain
        SM[Strike Matrix]
        GK[Greeks]
        OI[OI Analysis]
    end
    
    RX[Redux Store] --> Market View & Option Chain
```

## 4. Real-time Update Cycle

```mermaid
sequenceDiagram
    participant KA as Kite API
    participant BE as Backend
    participant RD as Redis
    participant PG as PostgreSQL
    participant FE as Frontend
    
    KA->>BE: Stream Market Data
    BE->>RD: Update Hot Data
    BE->>FE: WebSocket Update
    BE->>PG: Archive Data
    FE->>FE: Update UI
```

## 5. Data Update States

### Market Hours (9:15 AM - 3:30 PM)
1. Kite WebSocket actively streams market data
2. Backend processes and stores in Redis
3. Real-time updates sent to Frontend
4. Periodic archival to PostgreSQL

### After Market Hours
1. Historical data served via REST API
2. Analytics processing runs
3. Data cleanup and archival
4. System maintenance

## 6. Error Handling

```mermaid
flowchart TB
    E[Error Occurs] --> T{Error Type}
    T -->|Connection| RC[Reconnect Strategy]
    T -->|Data| DH[Data Recovery]
    T -->|System| SH[System Recovery]
    
    RC --> |Success| N[Normal Flow]
    DH --> |Success| N
    SH --> |Success| N
    
    RC --> |Fail| F[Fallback Mode]
    DH --> |Fail| F
    SH --> |Fail| F
```

## 7. Key Points

### Performance
- Real-time data via WebSocket
- Hot data in Redis
- Historical data in PostgreSQL
- Efficient state management in Frontend

### Reliability
- Automatic reconnection
- Data validation
- Error recovery
- Fallback mechanisms

### Scalability
- Separate storage for hot and cold data
- Component-based frontend
- Modular backend services
- Clear separation of concerns
