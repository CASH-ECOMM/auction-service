# Auction Service

gRPC-based microservice for managing auctions and bids in real-time.

## Quick Start

### 1. Setup Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your configuration (database credentials, gRPC port, etc.)

### 2. Running with CLI

**Install dependencies:**
```bash
uv sync
```

**Generate gRPC stubs:**
```bash
./generate_grpc.sh
```

**Run the service:**
```bash
uv run python -m app.main
```

Service will start on `localhost:50051`

### 3. Running with Docker

```bash
docker compose up
```

This starts both the auction service (on `localhost:50053`) and PostgreSQL database.

## Features

- **StartAuction** - Create a new auction with starting price and end time
- **PlaceBid** - Place a bid on an active auction
- **GetAuctionStatus** - Get current auction status with highest bidder
- **GetAuctionEnd** - Retrieve auction end time
- **GetAuctionWinner** - Get the winning bid and user after auction ends
- **GetBidHistory** - View all bids for a specific auction

## Tech Stack

- gRPC / Protocol Buffers
- SQLAlchemy (PostgreSQL)
- uv for dependency management
- Background auction closer worker