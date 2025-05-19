# backend/app/api/router.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
import boto3

from app.schemas.receipt import ReceiptCreate, ReceiptOut
from app.db.session import get_db
from app.models.receipt import Receipt, ReceiptStatus
from app.tasks.process_receipt import process_receipt_task
from app.core.config import settings

router = APIRouter()


@router.post("/receipts/upload", response_model=ReceiptOut, status_code=202)
async def upload_receipt(
    user_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # 1) save metadata record
    s3_key = f"receipts/{user_id}/{uuid4()}.png"
    new = Receipt(user_id=user_id, s3_key=s3_key, status=ReceiptStatus.PENDING)
    db.add(new)
    await db.commit()
    await db.refresh(new)

    # 2) push raw bytes to S3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    await file.seek(0)
    s3.upload_fileobj(file.file, settings.AWS_S3_BUCKET, s3_key)

    # 3) enqueue Celery task
    process_receipt_task.delay(receipt_id=new.id, s3_key=s3_key)

    return new


@router.get("/receipts/{receipt_id}", response_model=ReceiptOut)
async def get_receipt(receipt_id: int, db: AsyncSession = Depends(get_db)):
    rec = await db.get(Receipt, receipt_id)
    if not rec:
        raise HTTPException(404, "Receipt not found")
    return rec
