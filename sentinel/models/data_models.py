"""Data models for Sentinel analysis."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CharacterInfo(BaseModel):
    """Basic character information."""
    character_id: int
    character_name: str
    corporation_id: int
    corporation_name: str
    alliance_id: Optional[int] = None
    alliance_name: Optional[str] = None
    security_status: float = 0.0
    
    
class CorporationHistory(BaseModel):
    """Corporation employment history record."""
    corporation_id: int
    corporation_name: str
    start_date: datetime
    end_date: Optional[datetime] = None
    is_deleted: bool = False  # If the corp no longer exists
    

class Transaction(BaseModel):
    """ISK or item transaction record."""
    transaction_id: int
    date: datetime
    client_id: int
    amount: float
    description: Optional[str] = None
    is_personal: bool = True
    journal_ref_type: Optional[str] = None  # e.g., "player_trading", "bounty_prizes"
    

class Contract(BaseModel):
    """Contract information."""
    contract_id: int
    issuer_id: int
    assignee_id: int
    date_issued: datetime
    date_expired: Optional[datetime] = None
    date_completed: Optional[datetime] = None
    contract_type: str  # "item_exchange", "courier", "auction"
    status: str  # "outstanding", "completed", "failed", "deleted"
    price: float = 0.0
    reward: float = 0.0
    collateral: float = 0.0
    

class Contact(BaseModel):
    """Known contact/associate."""
    contact_id: int
    contact_name: str
    contact_type: str = "character"  # "character", "corporation", "alliance"
    standing: float = 0.0  # -10 to +10
    

class AllianceInfo(BaseModel):
    """Alliance information."""
    alliance_id: int
    alliance_name: str
    ticker: str
    date_founded: Optional[datetime] = None
    executor_corp_id: Optional[int] = None
    is_hostile: bool = False  # Flag for known hostile/enemy alliances
