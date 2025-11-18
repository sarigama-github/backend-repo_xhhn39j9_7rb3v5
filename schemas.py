"""
Database Schemas for the fundraiser app

Each Pydantic model maps to a MongoDB collection with the lowercase name of the class.
- Investor -> "investor"
- Contribution -> "contribution"
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

class Investor(BaseModel):
    """VIP Investor sign-up schema (collection: investor)"""
    full_name: str = Field(..., min_length=2, max_length=100, description="Investor full name")
    email: EmailStr = Field(..., description="Contact email")
    wallet_address: Optional[str] = Field(None, max_length=120, description="Crypto wallet address (optional)")
    country: Optional[str] = Field(None, max_length=80, description="Country of residence")
    consent: bool = Field(..., description="Agrees to VIP terms")
    referral_source: Optional[str] = Field(None, description="How did they hear about us")

class Contribution(BaseModel):
    """Contribution schema (collection: contribution)"""
    investor_email: EmailStr = Field(..., description="Email used to match investor")
    amount: float = Field(..., gt=0, description="Contribution amount in USD equivalent")
    method: Literal['crypto','fiat'] = Field('crypto', description="Payment method")
    tx_hash: Optional[str] = Field(None, description="Blockchain transaction hash if crypto")
    note: Optional[str] = Field(None, max_length=300, description="Optional note")
