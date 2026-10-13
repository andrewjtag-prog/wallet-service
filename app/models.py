from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    balance: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    __table_args__ = (
        CheckConstraint(
            "balance >= 0", name="ck_wallet_balance_non_negative"
        ),
    )