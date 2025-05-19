import logging
import stripe
from app.core.config import settings

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_API_KEY
stripe.enable_telemetry = True

def create_monthly_expense_report(
    items: list[dict],
    customer: str,
    connected_account: str | None = None
) -> stripe.Invoice:
    """
    Creates Stripe Invoice with each expense as an InvoiceItem.
    items: [
      {"description": str, "amount": float, "currency": "usd"},
      ...
    ]
    """
    created_items = []
    acct_kw = {"stripe_account": connected_account} if connected_account else {}

    for it in items:
        ci = stripe.InvoiceItem.create(
            customer=customer,
            amount=int(it["amount"]*100),  # cents
            currency=it.get("currency","usd"),
            description=it["description"],
            **acct_kw
        )
        created_items.append(ci)

    invoice = stripe.Invoice.create(
        customer=customer,
        auto_advance=True,
        **acct_kw
    )
    return invoice
