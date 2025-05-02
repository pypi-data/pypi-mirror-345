"""
marketplace.py

This module implements a marketplace for node operators to sell the credits they have earned
(via bandwidth provision) while preventing them from selling the initial 100 free credits.
Credits that are available for sale are defined as those beyond the free threshold (100 credits).

This module defines three endpoints:
  - POST /market/offer — for a node operator to list an offer.
  - GET /market/offers — to retrieve all active offers.
  - POST /market/buy/{offer_id} — for a buyer to purchase an offer.

When a buyer initiates a purchase, the system uses an escrow mechanism that initiates an M‑Pesa STK push (via mpesa.py).
A background task then polls the M‑Pesa payment status. On a successful payment, the operator’s corresponding (locked)
credits are deducted and transferred to the buyer.
"""

import time
import uuid
import asyncio
import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Security
from pydantic import BaseModel

# Import helper functions and types from your existing code.
# Adjust the import paths as required.
from .auth import get_current_user, add_credits_to_user, deduct_credits_from_user, DBUser
from .mpesa import initiate_stk_push, query_stk_status

# Set up a logger for the marketplace module.
logger = logging.getLogger(__name__)

# In‑memory global stores for marketplace offers, associated transaction records,
# and a dictionary to keep track of credits “locked” for sale.
marketplace_offers: Dict[str, Dict[str, Any]] = {}
marketplace_transactions: Dict[str, Dict[str, Any]] = {}
locked_credits: Dict[str, float] = {}  # keyed by operator username

# Define Pydantic models for input and output data.
class OfferCreate(BaseModel):
    """
    Model for creating a new credit sale offer.
    amount: The number of credits the operator wants to sell.
    price_per_credit: The price (in fiat currency) for each credit.
    """
    amount: float
    price_per_credit: float

class OfferOut(BaseModel):
    """
    Model for representing an active sale offer.
    """
    offer_id: str
    operator_username: str
    amount: float
    price_per_credit: float
    total_price: float
    timestamp: float

class PurchaseRequest(BaseModel):
    """
    Model for a buyer’s purchase request.
    The phone_number is used for initiating the M-Pesa payment.
    """
    phone_number: Optional[str] = None

# Create an APIRouter for marketplace endpoints.
router = APIRouter(prefix="/market", tags=["Marketplace"])

@router.get("/offers", response_model=List[OfferOut])
async def list_market_offers():
    """
    Retrieve the list of active credit sale offers from node operators.
    """
    return list(marketplace_offers.values())

@router.post("/offer", response_model=OfferOut)
async def create_market_offer(
    offer: OfferCreate,
    current_user: DBUser = Security(get_current_user, scopes=["credits:manage"])
):
    """
    Create a new marketplace offer for selling credits.

    Only credits beyond the free threshold (100 credits) are sellable.
    The credits for the offer are "locked" (i.e. reserved) so that multiple offers
    cannot claim the same earned credits.

    Args:
        offer: The offer details as provided by the operator.
        current_user: The logged-in operator (obtained via the security dependency).

    Returns:
        The newly created offer.
    """
    free_threshold = 100.0
    user_credits = current_user.credits  # total credits in the user record
    locked = locked_credits.get(current_user.username, 0.0)
    # Only credits above 100 (free allotment) minus already locked credits are sellable.
    sellable = max(user_credits - free_threshold - locked, 0.0)
    if offer.amount > sellable:
        raise HTTPException(
            status_code=400,
            detail="Insufficient sellable credits available. "
                   "You may only sell up to {:.2f} credits.".format(sellable)
        )
    # Lock the offered credits
    locked_credits[current_user.username] = locked + offer.amount

    offer_id = str(uuid.uuid4())
    total_price = offer.amount * offer.price_per_credit
    new_offer = {
        "offer_id": offer_id,
        "operator_username": current_user.username,
        "amount": offer.amount,
        "price_per_credit": offer.price_per_credit,
        "total_price": total_price,
        "timestamp": time.time()
    }
    marketplace_offers[offer_id] = new_offer
    logger.info(f"Offer {offer_id} created by operator {current_user.username}: "
                f"Selling {offer.amount} credits at {offer.price_per_credit} per credit.")
    return new_offer

@router.post("/buy/{offer_id}")
async def buy_offer(
    offer_id: str,
    purchase_request: PurchaseRequest,
    background_tasks: BackgroundTasks,
    current_user: DBUser = Security(get_current_user, scopes=["credits:manage"])
):
    """
    Purchase a credit sale offer.

    This endpoint initiates an M-Pesa STK push payment for the total purchase price.
    A background task then polls the M-Pesa payment status. Once confirmed, the operator’s
    locked credits are officially deducted (using deduct_credits_from_user) and the buyer
    receives the credits (via add_credits_to_user). The offer is then removed from the marketplace.

    Args:
        offer_id: The unique identifier of the offer to buy.
        purchase_request: The purchase details (includes phone_number if not set on user).
        current_user: The buyer (obtained via security dependency).

    Returns:
        A message indicating that payment has been initiated along with the checkout_request_id.
    """
    if offer_id not in marketplace_offers:
        raise HTTPException(status_code=404, detail="Offer not found.")
    offer = marketplace_offers[offer_id]
    # Prevent an operator from buying their own offer.
    if offer["operator_username"] == current_user.username:
        raise HTTPException(status_code=400, detail="You cannot purchase your own offer.")
    phone_number = purchase_request.phone_number or current_user.phone_number
    if not phone_number:
        raise HTTPException(
            status_code=400,
            detail="Buyer phone number is required for payment initiation."
        )
    total_price = offer["total_price"]
    # Initiate M-Pesa payment using your existing mpesa.py initiate_stk_push function.
    payment_result = await initiate_stk_push(phone_number, total_price)
    checkout_request_id = payment_result.get("CheckoutRequestID")
    if not checkout_request_id:
        raise HTTPException(status_code=500, detail="Failed to initiate payment.")
    # Create a transaction record (using the checkout_request_id as transaction id)
    transaction = {
        "transaction_id": checkout_request_id,
        "offer_id": offer_id,
        "operator_username": offer["operator_username"],
        "buyer_username": current_user.username,
        "amount": offer["amount"],
        "total_price": total_price,
        "phone_number": phone_number,
        "status": "pending",
        "start_time": time.time()
    }
    marketplace_transactions[checkout_request_id] = transaction
    logger.info(f"Transaction {checkout_request_id} initiated for offer {offer_id}: "
                f"{offer['amount']} credits for {total_price}.")
    # Schedule background task to process (poll) the payment and complete the sale.
    background_tasks.add_task(process_market_transaction, checkout_request_id)
    return {
        "message": "Payment initiated. Please complete the payment on your phone.",
        "checkout_request_id": checkout_request_id
    }

async def process_market_transaction(transaction_id: str):
    """
    Background task to process the escrow transaction.

    The function polls the payment gateway via query_stk_status.
    On successful payment (ResultCode == "0"), it releases the locked credits,
    deducts the credits from the operator (using deduct_credits_from_user) and adds
    them to the buyer (using add_credits_to_user). If the payment is cancelled or fails,
    the locked credits are released back to the operator's available sellable credits.

    Args:
        transaction_id: The unique identifier for the transaction (checkout_request_id from M-Pesa).
    """
    transaction = marketplace_transactions.get(transaction_id)
    if not transaction:
        logger.error(f"Transaction {transaction_id} not found.")
        return
    operator_username = transaction["operator_username"]
    buyer_username = transaction["buyer_username"]
    amount = transaction["amount"]

    polling_interval = 10  # seconds
    timeout = 300          # seconds
    start_time = time.time()
    while time.time() - start_time < timeout:
        await asyncio.sleep(polling_interval)
        try:
            status_result = await query_stk_status(transaction_id)
        except Exception as e:
            logger.error(f"Error querying payment status for transaction {transaction_id}: {e}")
            continue

        if 'ResultCode' in status_result:
            result_code = status_result.get("ResultCode")
            if result_code == "0":
                # Payment successful. Release the locked credits.
                current_locked = locked_credits.get(operator_username, 0.0)
                locked_credits[operator_username] = max(current_locked - amount, 0.0)
                # Remove the offer from marketplace.
                offer_id = transaction["offer_id"]
                marketplace_offers.pop(offer_id, None)
                # Transfer credits: deduct from operator and add to buyer.
                await deduct_credits_from_user(operator_username, amount)
                await add_credits_to_user(buyer_username, amount)
                transaction["status"] = "completed"
                transaction["result_description"] = status_result.get("ResultDesc", "")
                logger.info(f"Transaction {transaction_id} completed: "
                            f"Transferred {amount} credits from {operator_username} to {buyer_username}.")
                return
            elif result_code in ["1032"]:
                # Transaction cancelled by user.
                transaction["status"] = "cancelled"
                transaction["result_description"] = status_result.get("ResultDesc", "")
                current_locked = locked_credits.get(operator_username, 0.0)
                locked_credits[operator_username] = max(current_locked - amount, 0.0)
                logger.info(f"Transaction {transaction_id} cancelled by user.")
                return
            else:
                # Payment failed.
                transaction["status"] = "failed"
                transaction["result_description"] = status_result.get("ResultDesc", "")
                current_locked = locked_credits.get(operator_username, 0.0)
                locked_credits[operator_username] = max(current_locked - amount, 0.0)
                logger.error(f"Transaction {transaction_id} failed with result code {result_code}.")
                return
        elif 'errorCode' in status_result:
            error_code = status_result.get("errorCode")
            error_message = status_result.get("errorMessage")
            if error_code == "500.001.1001" and error_message == "The transaction is being processed":
                continue
            else:
                transaction["status"] = "error"
                transaction["error_message"] = error_message
                current_locked = locked_credits.get(operator_username, 0.0)
                locked_credits[operator_username] = max(current_locked - amount, 0.0)
                logger.error(f"Transaction {transaction_id} encountered error: {error_message}")
                return
        else:
            transaction["status"] = "error"
            transaction["error_message"] = "Unrecognized response from payment gateway"
            current_locked = locked_credits.get(operator_username, 0.0)
            locked_credits[operator_username] = max(current_locked - amount, 0.0)
            logger.error(f"Transaction {transaction_id} failed: Unrecognized response.")
            return
    transaction["status"] = "timeout"
    current_locked = locked_credits.get(operator_username, 0.0)
    locked_credits[operator_username] = max(current_locked - amount, 0.0)
    logger.error(f"Transaction {transaction_id} timed out after {timeout} seconds.")