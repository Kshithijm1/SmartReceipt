# backend/app/models/receipt.py
from sqlalchemy import Column, String, Integer, Enum, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from app.db.session import Base
import enum


class ReceiptStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # link to auth layer
    s3_key = Column(String, unique=True, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(ReceiptStatus), default=ReceiptStatus.PENDING)
    ocr_text = Column(JSON, nullable=True)
    table_data = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)

    line_items = relationship("LineItem", back_populates="receipt", cascade="all, delete")
    expenses = relationship("Expense", back_populates="receipt", cascade="all, delete")
