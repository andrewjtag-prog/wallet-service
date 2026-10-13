from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class OperationRequest(BaseModel):
    operation_type: Literal["DEPOSIT", "WITHDRAW"]
    amount: Decimal = Field(gt=0, max_digits=20, decimal_places=2)


class BalanceResponse(BaseModel):
    balance: Decimal