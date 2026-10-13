from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Wallet


async def get_wallet(
    session: AsyncSession, wallet_id: UUID
) -> Wallet | None:
    result = await session.execute(
        select(Wallet).where(Wallet.id == wallet_id)
    )
    return result.scalar_one_or_none()


async def get_wallet_for_update(
    session: AsyncSession, wallet_id: UUID
) -> Wallet | None:
    result = await session.execute(
        select(Wallet)
        .where(Wallet.id == wallet_id)
        .with_for_update()
    )
    return result.scalar_one_or_none()