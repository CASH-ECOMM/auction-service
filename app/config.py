from dotenv import load_dotenv
import os

# Load environment variables from .env file.
load_dotenv()

class Config:

    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/auction_db")

    GRPC_HOST = os.getenv("GRPC_HOST", "localhost")
    GRPC_PORT = os.getenv("GRPC_PORT", 50054)