import logging
from typing import List, Dict
from plaid import Client
from plaid.errors import PlaidError
from app.core.config import settings

logger = logging.getLogger(__name__)

class PlaidService:
    def __init__(self):
        self.client = Client(
            client_id   = settings.PLAID_CLIENT_ID,
            secret      = settings.PLAID_SECRET,
            environment = settings.PLAID_ENVIRONMENT,
        )

    def create_link_token(self, user_id: str) -> str:
        """Generate a Link token for the frontend Plaid Link flow."""
        try:
            resp = self.client.LinkToken.create({
                "user":        {"client_user_id": user_id},
                "client_name": settings.PROJECT_NAME,
                "products":    ["transactions"],
                "country_codes": ["US","CA"],
                "language":    "en",
            })
            return resp["link_token"]
        except PlaidError as e:
            logger.exception("Plaid LinkToken.create failed")
            raise

    def exchange_public_token(self, public_token: str) -> str:
        """Swap front-end public_token for a long-lived access_token."""
        try:
            resp = self.client.Item.public_token.exchange(public_token)
            return resp["access_token"]
        except PlaidError as e:
            logger.exception("Plaid public_token.exchange failed")
            raise

    def get_transactions(
        self, access_token: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Fetch transactions in the given date range."""
        try:
            resp = self.client.Transactions.get(
                access_token,
                start_date,
                end_date,
                options={"count":500, "offset":0}
            )
            return resp["transactions"]
        except PlaidError as e:
            logger.exception("Plaid Transactions.get failed")
            raise
