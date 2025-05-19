# backend/app/tasks/process_receipt.py
import io
from celery import shared_task
import boto3
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import AsyncSessionLocal
from app.models.receipt import Receipt, ReceiptStatus
from app.models.line_item import LineItem
from app.models.expense import Expense
from app.services.ocr_service import extract_text_from_image
from app.services.table_service import parse_line_items
from app.services.classification_service import classify_category, classify_merchant
from app.core.config import settings


@shared_task(bind=True, name="process_receipt_task")
def process_receipt_task(self, receipt_id: int, s3_key: str):
    session: AsyncSession = AsyncSessionLocal()
    try:
        # 1) mark processing
        session.sync_session.execute(
            Receipt.__table__.update().where(Receipt.id == receipt_id)
            .values(status=ReceiptStatus.PROCESSING)
        )
        session.sync_session.commit()

        # 2) fetch image bytes
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        obj = s3.get_object(Bucket=settings.AWS_S3_BUCKET, Key=s3_key)
        image_bytes = obj["Body"].read()

        # 3) OCR
        text = extract_text_from_image(image_bytes)

        # 4) naive table-detection: assume processor returns table cells
        #    (in real prod, use LayoutLM2 or Pix2Struct for layout)
        # 5) parse line items
        #    here we simulate table dict – replace with real detection
        table = {"cells": text.split(), "coordinates": [], "num_rows": 0, "num_columns": 0}
        items = parse_line_items(table)

        # 6) classify & persist
        session.add_all([
            LineItem(
                receipt_id=receipt_id,
                description=i["description"],
                quantity=i["quantity"],
                unit_price=i["unit_price"],
                total_price=i["total_price"],
            ) for i in items
        ])

        # 7) simple expense summary
        total_amount = sum(i["total_price"] for i in items)
        merchant = classify_merchant(text, ["Starbucks", "Tim Hortons", "Amazon"])["labels"][0]
        category = classify_category(text)["label"]

        session.add(
            Expense(
                receipt_id=receipt_id,
                merchant=merchant,
                category=category,
                amount=total_amount,
            )
        )

        # 8) update receipt
        session.sync_session.execute(
            Receipt.__table__.update().where(Receipt.id == receipt_id)
            .values(status=ReceiptStatus.COMPLETED, ocr_text=text, metadata={"total": total_amount})
        )
        session.sync_session.commit()

    except Exception as e:
        # mark failed
        session.sync_session.execute(
            Receipt.__table__.update().where(Receipt.id == receipt_id)
            .values(status=ReceiptStatus.FAILED)
        )
        session.sync_session.commit()
        raise e
    finally:
        session.close()
