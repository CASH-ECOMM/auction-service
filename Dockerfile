FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
  gcc \
  postgresql-client \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY pyproject.toml uv.lock ./
COPY . .

# Install dependencies with uv
RUN uv sync --frozen

# Generate gRPC code from proto files
RUN chmod +x generate_grpc.sh && ./generate_grpc.sh

# Expose gRPC port
EXPOSE 50051

# Run the application
CMD ["uv", "run", "python", "-m", "app.main"]
