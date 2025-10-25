from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.connection import Base
from datetime import datetime

class Auction(Base):

    __tablename__ = "auctions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Start and end times for the auction.
    start_time = Column(DateTime, default=datetime.now(), nullable=False)
    end_time = Column(DateTime, nullable=False)

    # Highest current bid to be stored
    highest_bid = Column(Integer, ForeignKey("bids.id", ondelete="CASCADE"))

    # Define relationship with Bid table
    bids = relationship("Bid", back_populates="platform")

class Bid(Base):

    __tablename__ = "bids"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)

    user_first_name = Column(String, nullable=False)
    user_last_name = Column(String, nullable=False)

    # Amount bid on an item
    amount = Column(Integer, nullable=False)

    # Time when the bid was created
    created = Column(DateTime, default=datetime.now())

    # Foreign keys to connect the bid to the item being bid on and the user, as well as the auction platform
    auction_id = Column(Integer, ForeignKey("auctions.id", ondelete="CASCADE"), nullable=False)

    # Define relationships with the corresponding tables
    platform = relationship("Auction", back_populates="bids")