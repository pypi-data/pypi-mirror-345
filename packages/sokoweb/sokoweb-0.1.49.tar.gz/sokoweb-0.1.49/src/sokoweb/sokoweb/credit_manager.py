# credit_manager.py
import asyncio
import logging

from .database import async_session
from .db_models import NodeCredit

logger = logging.getLogger(__name__)


class CreditManager:
    """
    Manages credits for nodes, storing credits persistently in the database.
    """

    def __init__(self):
        self.credit_lock = asyncio.Lock()  # Async lock for thread-safe operations
        self.processed_requests = (
            set()
        )  # Track request_ids to ensure credits are awarded only once per request

    async def add_credit_once(self, node_id, request_id, amount=1):
        """
        Add credits to a node, ensuring credits are awarded only once per request.

        Args:
            node_id (str): The unique identifier of the node.
            request_id (str): The unique identifier of the request.
            amount (int): Amount of credits to add.
        """
        async with self.credit_lock:
            if request_id in self.processed_requests:
                logger.debug(
                    f"Skipping duplicate credit award for node {node_id}, request_id {request_id}"
                )
                return

            async with async_session() as session:
                # Retrieve or create NodeCredit record
                node_credit = await session.get(NodeCredit, node_id)
                if node_credit is None:
                    node_credit = NodeCredit(node_id=node_id, credits=0.0)
                    session.add(node_credit)

                node_credit.credits += amount
                await session.commit()

            self.processed_requests.add(request_id)
            logger.debug(
                f"Added {amount} credits to node {node_id}. Total credits: {node_credit.credits}"
            )

    async def deduct_credits(self, node_id, amount):
        """
        Deduct credits from a node's account.

        Args:
            node_id (str): The unique identifier of the node.
            amount (int): Amount of credits to deduct.

        Returns:
            bool: True if deduction was successful, False otherwise.
        """
        async with self.credit_lock:
            async with async_session() as session:
                node_credit = await session.get(NodeCredit, node_id)
                if node_credit and node_credit.credits >= amount:
                    node_credit.credits -= amount
                    await session.commit()
                    logger.debug(
                        f"Deducted {amount} credits from node {node_id}. Remaining credits: {node_credit.credits}"
                    )
                    return True
                else:
                    current_credits = node_credit.credits if node_credit else 0
                    logger.debug(
                        f"Node {node_id} does not have enough credits to deduct {amount}. Current credits: {current_credits}"
                    )
                    return False

    async def get_credits(self, node_id):
        """
        Get the current credit balance for a node.

        Args:
            node_id (str): The unique identifier of the node.

        Returns:
            float: The current credit balance.
        """
        async with self.credit_lock:
            async with async_session() as session:
                node_credit = await session.get(NodeCredit, node_id)
                return node_credit.credits if node_credit else 0.0