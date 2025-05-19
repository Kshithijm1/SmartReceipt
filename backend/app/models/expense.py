# backend/app/models/expense.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id", ondelete="CASCADE"))
    category = Column(String, nullable=False, index=True)
    merchant = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)

    receipt = relationship("Receipt", back_populates="expenses")
