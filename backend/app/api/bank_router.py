from fastapi import APIRouter, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import List
from app.services.plaid_service import PlaidService
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User  # assume you have a User model
from app.models.user_tokens import UserToken  # maps user_id→plaid access_token

router = APIRouter()

plaid = PlaidService()


class LinkTokenResp(BaseModel):
    link_token: str


class PubTokIn(BaseModel):
    public_token: str


class Transaction(BaseModel):
    account_id: str
    name:       str
    amount:     float
    date:       str
    currency:   str


class TxnsResp(BaseModel):
    transactions: List[Transaction]


@router.post("/plaid/create_link_token", response_model=LinkTokenResp)
async def create_link_token(user_id: str, db: AsyncSession = Depends(get_db)):
    # ensure user exists...
    token = await run_in_threadpool(plaid.create_link_token, user_id)
    return LinkTokenResp(link_token=token)


@router.post("/plaid/exchange_public_token")
async def exchange_public(
    data: PubTokIn, user_id: str, db: AsyncSession = Depends(get_db)
):
    access = await run_in_threadpool(plaid.exchange_public_token, data.public_token)
    # persist in your UserToken table
    db.add(UserToken(user_id=user_id, access_token=access))
    await db.commit()
    return {"access_token": access}


@router.get("/plaid/transactions", response_model=TxnsResp)
async def get_txns(
    user_id: str,
    start_date: str,
    end_date: str,
    db: AsyncSession = Depends(get_db)
):
    # lookup access_token
    tok = await db.get(UserToken, user_id)
    if not tok:
        raise HTTPException(404, "No Plaid token")
    txns = await run_in_threadpool(
        plaid.get_transactions, tok.access_token, start_date, end_date
    )
    return TxnsResp(transactions=[Transaction(**t) for t in txns])
