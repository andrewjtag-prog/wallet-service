from fastapi import FastAPI

from app.api import router as wallets_router

app = FastAPI(title="Wallet Service")

app.include_router(wallets_router)