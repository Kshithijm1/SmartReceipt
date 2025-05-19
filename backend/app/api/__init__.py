from fastapi import APIRouter
from app.api.router import router as receipts_router
from app.api.bank_router import router as bank_router
from app.api.expenses_router import router as exp_router

api_router = APIRouter()
api_router.include_router(receipts_router, prefix="/receipts", tags=["receipts"])
api_router.include_router(bank_router,    prefix="/bank",     tags=["bank"])
api_router.include_router(exp_router,     prefix="/finance",  tags=["finance"])
