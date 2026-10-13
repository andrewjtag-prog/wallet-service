from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repository import get_wallet
from app.schemas import BalanceResponse, OperationRequest
from app.service import (
    InsufficientFundsError,
    WalletNotFoundError,
    change_balance,
)

router = APIRouter(prefix="/api/v1/wallets", tags=["wallets"])


@router.get("/{wallet_uuid}", response_model=BalanceResponse)
async def read_wallet(
    wallet_uuid: UUID,
    session: AsyncSession = Depends(get_session),
) -> BalanceResponse:
    wallet = await get_wallet(session, wallet_uuid)
    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )
    return BalanceResponse(balance=wallet.balance)


@router.post(
    "/{wallet_uuid}/operation", response_model=BalanceResponse
)
async def wallet_operation(
    wallet_uuid: UUID,
    payload: OperationRequest,
    session: AsyncSession = Depends(get_session),
) -> BalanceResponse:
    try:
        balance = await change_balance(
            session,
            wallet_uuid,
            payload.operation_type,
            payload.amount,
        )
    except WalletNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )
    except InsufficientFundsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds",
        )
    return BalanceResponse(balance=balance)