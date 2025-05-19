# backend/app/schemas/receipt.py
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

from app.models.receipt import ReceiptStatus


class LineItemIn(BaseModel):
    description: str
    quantity: float
    unit_price: float
    total_price: float


class ExpenseIn(BaseModel):
    category: str
    merchant: str
    amount: float


class ReceiptCreate(BaseModel):
    user_id: str
    s3_key: str


class ReceiptOut(BaseModel):
    id: int
    user_id: str
    s3_key: str
    uploaded_at: datetime
    status: ReceiptStatus
    line_items: Optional[List[LineItemIn]]
    expenses: Optional[List[ExpenseIn]]

    class Config:
        orm_mode = True
