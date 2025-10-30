import time
from datetime import datetime
from app.db.connection import SessionLocal
from app.models.auction_models import Auction
from app.services.auction_service import AuctionService

# Seperate worker to close expired auctions
def close_expired_auctions():

    # Continuously run the function
    while True:
        db = SessionLocal()
        try:
            # Add expired auctions from the 10 second interval to expired.
            expired = (db.query(Auction).filter(Auction.end_time <= datetime.now(), Auction.status != "CLOSED")
                       .with_for_update(skip_locked=True).all())

            # Go through all the expired auctions and set their status to CLOSED
            for auction in expired:
                auction.status = "CLOSED"
                print(f"Auction {auction.id} closed at {datetime.now()}")

            db.commit()
        finally:
            db.close()
        time.sleep(10) # Check every 10 seconds

if __name__ == "__main__":
    close_expired_auctions()

