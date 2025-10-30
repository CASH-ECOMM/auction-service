import grpc
from concurrent import futures
import logging
import signal
import sys

# Import generated gRPC code
from app.proto import auction_service_pb2_grpc
from app.services.auction_service import AuctionService
from app.db.connection import init_db
from app.config import Config
from app.workers import auction_closer
from app.workers.auction_closer import close_expired_auctions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def serve():
    """Start the gRPC server"""

    # Initialize database
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        sys.exit(1)

    # Create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add UserService to server
    auction_service_pb2_grpc.add_AuctionServiceServicer_to_server(
        AuctionService(), server
    )

    # Bind server to address
    server_address = f"{Config.GRPC_HOST}:{Config.GRPC_PORT}"
    server.add_insecure_port(server_address)

    # Start server
    server.start()
    logger.info(f"UserService gRPC server started on {server_address}")
    #logger.info(f"Environment: {Config.ENVIRONMENT}")
    logger.info(f"Database: {Config.DATABASE_URL}")

    # Start the auction closer
    close_expired_auctions()

    # Handle graceful shutdown
    def handle_shutdown(signum, frame):
        logger.info("Received shutdown signal. Stopping server...")
        server.stop(grace=5)
        logger.info("Server stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Wait for termination
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Server interrupted. Shutting down...")
        server.stop(grace=5)


if __name__ == "__main__":
    serve()
