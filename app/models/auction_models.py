from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
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

    # Highest bid to be stored once the auction is over with foreign key
    highest_bid = Column(Integer, ForeignKey("bids.id", ondelete="CASCADE"))

    # Define relationship with Bid table
    bids = relationship("Bid", back_populates="platform")

class Bid(Base):

    __tablename__ = "bids"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Amount bid on an item
    amount = Column(Numeric(10,2), nullable=False)

    # Time when the bid was created
    created = Column(DateTime, default=datetime.now())

    # Foreign keys to connect the bid to the item being bid on and the user, as well as the auction platform
    auction_id = Column(Integer, ForeignKey("auctions.id", ondelete="CASCADE"), nullable=False)
    catalogue_id = Column(Integer, ForeignKey("catalogues.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Define relationships with the corresponding tables
    platform = relationship("Auction", back_populates="bids")
    item = relationship("Catalogue", back_populates="bid_on")
    bidder = relationship("User", back_populates="user")

class Catalogue(Base):

    __tablename__ = "catalogues"

    id = Column(Integer, primary_key=True)

    bid_on = relationship("Bid", back_populates="item")

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    user = relationship("Bid", back_populates="bidder")
    in_session = relationship("Session", back_populates="current_session")

class Session(Base):

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)

    # Store session expiry
    expires_at = Column(DateTime, nullable=False)

    # Relate the session to a user
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    current_session = relationship("User", back_populates="in_session")