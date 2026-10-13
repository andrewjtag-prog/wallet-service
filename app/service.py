from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Wallet
from app.repository import get_wallet_for_update


class WalletNotFoundError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


async def change_balance(
    session: AsyncSession,
    wallet_id: UUID,
    operation_type: str,
    amount: Decimal,
) -> Decimal:
    async with session.begin():
        wallet: Wallet | None = await get_wallet_for_update(
            session, wallet_id
        )
        if wallet is None:
            raise WalletNotFoundError()

        if operation_type == "DEPOSIT":
            wallet.balance += amount
        else:
            if wallet.balance < amount:
                raise InsufficientFundsError()
            wallet.balance -= amount

        return wallet.balance