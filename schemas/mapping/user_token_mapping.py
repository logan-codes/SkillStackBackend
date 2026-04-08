# schemas/mapping/user_token_mapping.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TokenTransactionResponse(BaseModel):
    id: int
    user_id: int
    token_amount: int
    transaction_type: str
    description: Optional[str]
    reference_id: Optional[int]
    created_date: datetime

    class Config:
        from_attributes = True


class TokenSummaryResponse(BaseModel):
    total_tokens: int
    earned: int
    spent: int
    breakdown: dict


class TokenHistoryResponse(BaseModel):
    transactions: list[TokenTransactionResponse]
    total_count: int
    page: int
    limit: int
