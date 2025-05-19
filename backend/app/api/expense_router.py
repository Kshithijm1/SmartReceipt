from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, extract
from app.db.session import get_db
from app.models.expense import Expense
from app.models.receipt import Receipt
from app.services.stripe_service import create_monthly_expense_report

router = APIRouter()


class ExportIn(BaseModel):
    user_id:             str
    month:               int
    year:                int
    stripe_customer_id:  str
    stripe_account_id:   str | None = None


class ExportOut(BaseModel):
    invoice_id:  str
    invoice_url: str


@router.post("/export", response_model=ExportOut)
async def export_report(data: ExportIn, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Expense, Receipt.uploaded_at)
        .join(Receipt, Expense.receipt_id == Receipt.id)
        .where(
            Receipt.user_id == data.user_id,
            extract("month", Receipt.uploaded_at) == data.month,
            extract("year", Receipt.uploaded_at) == data.year,
        )
    )
    res = await db.execute(stmt)
    rows = res.all()
    if not rows:
        raise HTTPException(404, "No expenses found")

    items = [
        {
            "description": f"{exp.category} @ {exp.merchant}",
            "amount":      exp.amount,
            "currency":    "usd",
        }
        for exp, _ in rows
    ]

    invoice = create_monthly_expense_report(
        items,
        customer       = data.stripe_customer_id,
        connected_account = data.stripe_account_id
    )

    return ExportOut(
        invoice_id  = invoice.id,
        invoice_url = getattr(invoice, "hosted_invoice_url", "")
    )
