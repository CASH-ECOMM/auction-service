# auction-service

A gRPC-based auction service for managing bids and auctions.

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- PostgreSQL (running locally or via Docker)

## Running the App

```bash
# Generate gRPC code from proto files
./generate_grpc.sh

# Start the server
uv run python -m app.main
```

The gRPC server will start on `localhost:50051`.