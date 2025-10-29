from datetime import datetime, timedelta
import logging

from psycopg2 import Timestamp

import app.proto.auction_service_pb2 as auction_service_pb2
import app.proto.auction_service_pb2_grpc as auction_service_pb2_grpc

from app.db.connection import SessionLocal
from app.models.auction_models import Auction, Bid

logger = logging.getLogger(__name__)



class AuctionService(auction_service_pb2_grpc.AuctionServiceServicer):

    def StartAuction(self, request, context):

        # Get the database
        db = SessionLocal()

        try:
            # Catch any unfilled requests.
            if not all(
                [
                request.user_id,
                request.catalogue_id,
                request.starting_amount,
                request.end_time
                ]
            ):
                return auction_service_pb2.StartAuctionResponse(
                    success=False,
                    message="Missing required fields to start auction."
                )

            # Check if the starting amount is positive.
            if request.starting_amount <= 0:
                return auction_service_pb2.StartAuctionResponse(
                    success=False,
                    message="Starting amount must be greater than zero."
                )

            # Check that the endtime is in the future.
            if request.end_time.ToDatetime() <= datetime.now():
                return auction_service_pb2.StartAuctionResponse(
                    success=False,
                    message="End time must be in the future."
                )

            # Create new Auction to add to the db.
            new_auction = Auction(
                catalogue_id = request.catalogue_id,
                start_time = datetime.now(),
                end_time = request.end_time.ToDatetime(),
                starting_amount = request.starting_amount,
                status = "OPEN"
            )

            db.add(new_auction)
            db.commit()
            db.refresh(new_auction)

            return auction_service_pb2.StartAuctionResponse(
                success=True,
                message="Auction started successfully."
            )

        except Exception as e:
            db.rollback()
            return auction_service_pb2.StartAuctionResponse(
                success=False,
                message=f"Start auction failed: {str(e)}"
            )
        finally:
            db.close()

    def PlaceBid(self, request, context):

        db = SessionLocal()

        try:
            if not all(
                [
                    request.user_id,
                    request.catalogue_id,
                    request.username,
                    request.amount
                ]
            ):
                return auction_service_pb2.PlaceBidResponse(
                    success=False,
                    message="Missing required fields to place bid."
                )

            auction = db.query(Auction).filter(Auction.catalogue_id == request.catalogue_id).first()

            if not auction:
                return auction_service_pb2.PlaceBidResponse(
                    success=False,
                    message="Auction not found."
                )

            if auction.end_time <= datetime.now():
                return auction_service_pb2.PlaceBidResponse(
                    success=False,
                    message="Auction has already ended."
                )

            # Find the highest bid in the auction.
            current_highest_bid = db.query(Bid).filter(Bid.id == auction.highest_bid).first()

            if current_highest_bid and request.amount <= current_highest_bid.amount:
                return auction_service_pb2.PlaceBidResponse(
                    success=False,
                    message="Bid amount must be higher than the current highest bid."
                )

            new_bid = Bid(
                user_id = request.user_id,
                username = request.username,
                amount = request.amount,
                auction_id = db.query(Auction).filter(Auction.catalogue_id == request.catalogue_id).first().catalogue_id,
                created=datetime.now()
            )

            db.add(new_bid)
            db.commit()
            db.refresh(new_bid)

            auction.highest_bid = new_bid.id
            db.commit()
            db.refresh(auction)

            return auction_service_pb2.PlaceBidResponse(
                success=True,
                message="Bid placed successfully.",
            )

        except Exception as e:
            db.rollback()
            return auction_service_pb2.PlaceBidResponse(
                success=False,
                message=f"Bid failed: {str(e)}"
            )
        finally:
            db.close()


    def GetAuctionEnd(self, request, context):
        db = SessionLocal()

        try:
            # Find the auction from the catalogue_id
            auction = db.query(Auction).filter(Auction.catalogue_id == request.catalogue_id).first()

            if not auction:
                return auction_service_pb2.GetAuctionEndResponse(
                    success=False,
                    message="Auction not found."
                )

            return auction_service_pb2.GetAuctionEndResponse(
                found=True,
                end_time = auction.end_time,
                message="Auction end time found successfully."
            )

        except Exception as e:
            db.rollback()
            return auction_service_pb2.GetAuctionEndResponse(
                success=False,
                message=f"An error occurred finding the end time for the auction: {str(e)}"
            )
        finally:
            db.close()


    def GetAuctionStatus(self, request, context):
        db = SessionLocal()

        try:
            auction = db.query(Auction).filter(Auction.catalogue_id == request.catalogue_id).first()

            if not auction:
                return auction_service_pb2.GetAuctionStatusResponse(
                    success=False,
                    message="Auction not found."
                )

            auction_amount = db.query(Bid).filter(Bid.id == auction.highest_bid).first()

            # If there are no bids, set the amount to the starting amount.
            if not auction_amount:
                auction_amount = auction.starting_amount
            else:
                auction_amount = auction_amount.amount

            # Check if the auction has ended and assign remaining time in seconds.
            if auction.status == "CLOSED":
                remaining_time_seconds = 0
            else:
                remaining_time_seconds = max(0, int((auction.end_time - datetime.now()).total_seconds()))

            return auction_service_pb2.GetAuctionStatusResponse(
                success=True,
                highest_bidder = auction.highest_bid,
                current_amount = auction_amount,
                remaining_time = remaining_time_seconds,
                message=auction.status
            )

        except Exception as e:
            return auction_service_pb2.GetAuctionStatusResponse(
                success=False,
                message=f"An error occurred finding the status of the auction: {str(e)}"
            )
        finally:
            db.close()

    def GetBidHistory(self, request, context):
        db = SessionLocal()

        try:

            if not all(
                [
                    request.catalogue_id
                ]
            ):
                return auction_service_pb2.GetBidHistoryResponse(
                    success=False,
                    message="Missing required fields to get bid history."
            )

            auction = db.query(Auction).filter(Auction.catalogue_id == request.catalogue_id).first()

            if not auction:
                return auction_service_pb2.GetBidHistoryResponse(
                    success=False,
                    message="Auction not found."
                )

            # Get a list of bids for the auction.
            bids = db.query(Bid).filter(Bid.auction_id == auction.catalogue_id).all()

            # Expand the bids list to return all the required data.
            bid_history = [
                auction_service_pb2.Bid(
                    bid_id=bid.id,
                    user_id=bid.user_id,
                    catalogue_id=bid.auction_id,
                    amount=bid.amount,
                    bid_time=bid.created
                ) for bid in bids
            ]

            return auction_service_pb2.GetBidHistoryResponse(
                success=True,
                bid_history=bid_history,
                message="Bid history retrieved successfully."
            )
        except Exception as e:
            db.rollback()
            return auction_service_pb2.GetBidHistoryResponse(
                success=False,
                message=f"An error occurred retrieving bid history: {str(e)}"
            )
        finally:
            db.close()

    def GetAuctionWinner(self, request, context):
        db = SessionLocal()

        try:
            auction = db.query(Auction).filter(Auction.catalogue_id == request.catalogue_id).first()

            if not auction:
                return auction_service_pb2.GetAuctionWinnerResponse(
                    found=False,
                    message="Auction not found."
                )

            if auction.status != "CLOSED":
                return auction_service_pb2.GetAuctionWinnerResponse(
                    found=False,
                    message="Auction is not yet closed."
                )

            winning_bid = db.query(Bid).filter(Bid.id == auction.highest_bid).first()

            if not winning_bid:
                return auction_service_pb2.GetAuctionWinnerResponse(
                    found=False,
                    message="No bids were placed on this auction."
                )

            return auction_service_pb2.GetAuctionWinnerResponse(
                found=True,
                winner_user_id = winning_bid.user_id,
                final_price = winning_bid.amount,
                message="Found auction winner."
            )

        except Exception as e:
            db.rollback()
            return auction_service_pb2.GetAuctionWinnerResponse(
                found=False,
                message=f"An error occurred finding the winner of the auction: {str(e)}"
            )
        finally:
            db.close()
