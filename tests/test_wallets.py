import asyncio
from decimal import Decimal
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select

from app.models import Wallet


@pytest_asyncio.fixture
async def wallet_id(session_factory) -> str:
    wid = uuid4()
    async with session_factory() as session:
        session.add(Wallet(id=wid, balance=Decimal("100.00")))
        await session.commit()
    return str(wid)


async def test_get_wallet_ok(client: AsyncClient, wallet_id: str):
    resp = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert resp.status_code == 200
    assert Decimal(resp.json()["balance"]) == Decimal("100.00")


async def test_get_wallet_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/wallets/{uuid4()}")
    assert resp.status_code == 404


async def test_deposit(client: AsyncClient, wallet_id: str):
    resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": 50},
    )
    assert resp.status_code == 200
    assert Decimal(resp.json()["balance"]) == Decimal("150.00")


async def test_withdraw_ok(client: AsyncClient, wallet_id: str):
    resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 30},
    )
    assert resp.status_code == 200
    assert Decimal(resp.json()["balance"]) == Decimal("70.00")


async def test_withdraw_insufficient(client: AsyncClient, wallet_id: str):
    resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 1000},
    )
    assert resp.status_code == 400


async def test_invalid_amount(client: AsyncClient, wallet_id: str):
    resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": 0},
    )
    assert resp.status_code == 422


async def test_invalid_operation(client: AsyncClient, wallet_id: str):
    resp = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "TRANSFER", "amount": 10},
    )
    assert resp.status_code == 422


async def test_concurrent_withdrawals(
    client: AsyncClient, session_factory
):
    wid = uuid4()
    async with session_factory() as session:
        session.add(Wallet(id=wid, balance=Decimal("50.00")))
        await session.commit()

    async def withdraw():
        return await client.post(
            f"/api/v1/wallets/{wid}/operation",
            json={"operation_type": "WITHDRAW", "amount": 1},
        )

    responses = await asyncio.gather(*[withdraw() for _ in range(100)])

    ok = sum(1 for r in responses if r.status_code == 200)
    failed = sum(1 for r in responses if r.status_code == 400)
    assert ok == 50
    assert failed == 50

    async with session_factory() as session:
        result = await session.execute(
            select(Wallet).where(Wallet.id == wid)
        )
        wallet = result.scalar_one()
        assert wallet.balance == Decimal("0.00")