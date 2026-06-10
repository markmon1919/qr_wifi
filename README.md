# 🏗️ System Architecture

## High-Level Architecture

```mermaid
flowchart TB

    USER[📱 User Device]
    PORTAL[🌐 Captive Portal]
    API[⚡ FastAPI Core]
    REDIS[(Redis)]
    MONGO[(MongoDB)]
    ENGINE[⏱️ Consumption Engine]
    ROUTER[📡 MikroTik Router]

    USER --> PORTAL
    PORTAL --> API

    API --> REDIS
    API --> MONGO

    ENGINE --> REDIS
    ENGINE --> MONGO

    ROUTER --> API
    API --> ROUTER
```

---

## Production Deployment Topology

```mermaid
flowchart LR

    subgraph ClientNetwork
        CLIENT1[Phone]
        CLIENT2[Laptop]
        CLIENT3[Tablet]
    end

    subgraph Router
        MIKROTIK[MikroTik Hotspot]
    end

    subgraph VPS
        PORTAL[Portal]
        API[FastAPI]
        ENGINE[Consumption Engine]
        REDIS[(Redis)]
        MONGO[(MongoDB)]
    end

    CLIENT1 --> MIKROTIK
    CLIENT2 --> MIKROTIK
    CLIENT3 --> MIKROTIK

    MIKROTIK --> PORTAL

    PORTAL --> API

    API --> REDIS
    API --> MONGO

    ENGINE --> REDIS
    ENGINE --> MONGO

    MIKROTIK --> API
```

---

## Authentication Flow

```mermaid
sequenceDiagram

    participant User
    participant Portal
    participant API
    participant MongoDB
    participant Redis
    participant Router

    User->>Portal: Enter Mobile Number

    Portal->>API: Login Request

    API->>MongoDB: Check Wallet

    alt Wallet Available

        API->>Redis: Store Session
        API->>Redis: Store MAC Mapping

        API-->>Portal: Login Success

        Portal-->>User: Internet Access

    else No Balance

        API-->>Portal: Login Failed

    end

    Router->>API: Verify MAC

    API-->>Router: Allow / Block
```

---

## Wallet Consumption Architecture

```mermaid
flowchart TB

    WALLET[Wallet Balance]

    WALLET --> MOBILE[Mobile Number]

    MOBILE --> DEV1[Device 1]
    MOBILE --> DEV2[Device 2]
    MOBILE --> DEV3[Device 3]

    DEV1 --> ENGINE
    DEV2 --> ENGINE
    DEV3 --> ENGINE

    ENGINE --> DRAIN[Wallet Deduction]

    DRAIN --> WALLET
```

---

## Shared Wallet Logic

```mermaid
flowchart LR

    W[3600 Seconds]

    W --> A[1 Device]
    W --> B[2 Devices]
    W --> C[3 Devices]

    A --> A1[Drain Rate x1]
    B --> B1[Drain Rate x2]
    C --> C1[Drain Rate x3]
```

### Rule

```text
More devices ≠ more time

More devices = faster consumption
of the same wallet balance.
```

---

## Redis Session Model

```mermaid
flowchart TB

    MOBILE[09171234567]

    MOBILE --> D1[MAC 1]
    MOBILE --> D2[MAC 2]
    MOBILE --> D3[MAC 3]

    D1 --> REDIS[(Redis)]
    D2 --> REDIS
    D3 --> REDIS

    REDIS --> SESSION[Active Session Store]
```

---

## MongoDB Data Model

```mermaid
erDiagram

    WALLET {
        string mobile
        number seconds
    }

    TRANSACTIONS {
        string mobile
        string type
        number seconds
        date timestamp
    }

    USERS {
        string mobile
        date created_at
    }

    USERS ||--|| WALLET : owns
    USERS ||--o{ TRANSACTIONS : generates
```

---

## Request Lifecycle

```mermaid
flowchart LR

    A[Device Connects]

    A --> B[Captive Portal]

    B --> C[Login API]

    C --> D[Wallet Check]

    D --> E{Balance Available?}

    E -->|Yes| F[Create Session]

    E -->|No| G[Deny Access]

    F --> H[Allow Internet]

    H --> I[Consumption Engine]

    I --> J[Deduct Wallet]
```

---

## Future ISP v7 Architecture

```mermaid
flowchart TB

    USERS[Users]

    USERS --> ROUTER[MikroTik]

    ROUTER --> PORTAL[Portal]

    PORTAL --> API[FastAPI]

    API --> REDIS[(Redis)]
    API --> MONGO[(MongoDB)]

    API --> BILLING[Billing Engine]

    API --> SMS[SMS OTP]

    API --> GCASH[GCash Webhook]

    API --> DASHBOARD[Admin Dashboard]

    DASHBOARD --> REPORTS[Revenue Reports]

    ROUTER --> QOS[Queue Trees]

    QOS --> USERS
```




TP-Link Archer C6 WiFi
        ↓
User connects
        ↓
DNS resolves normally (but blocked internet)
        ↓
User forced to portal page
        ↓
Flask Portal (7777)
        ↓
FastAPI (8000 login check)
        ↓
Redis session + MongoDB wallet