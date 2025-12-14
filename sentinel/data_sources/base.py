"""Base data source interface for Sentinel."""

from abc import ABC, abstractmethod
from typing import List, Optional
from sentinel.models.data_models import (
    CharacterInfo,
    CorporationHistory,
    Transaction,
    Contract,
    Contact,
    AllianceInfo,
)


class DataSource(ABC):
    """
    Abstract base class for data sources.
    
    Implement this interface to connect Sentinel to your alliance's
    intel database views or internal APIs.
    """
    
    @abstractmethod
    def get_character_info(self, character_id: int) -> Optional[CharacterInfo]:
        """Get basic character information."""
        pass
    
    @abstractmethod
    def get_corporation_history(self, character_id: int) -> List[CorporationHistory]:
        """Get character's corporation employment history."""
        pass
    
    @abstractmethod
    def get_transactions(
        self, 
        character_id: int, 
        limit: Optional[int] = None
    ) -> List[Transaction]:
        """Get character's transaction history."""
        pass
    
    @abstractmethod
    def get_contracts(
        self, 
        character_id: int, 
        limit: Optional[int] = None
    ) -> List[Contract]:
        """Get character's contract history."""
        pass
    
    @abstractmethod
    def get_contacts(self, character_id: int) -> List[Contact]:
        """Get character's known contacts/associates."""
        pass
    
    @abstractmethod
    def get_alliance_info(self, alliance_id: int) -> Optional[AllianceInfo]:
        """Get alliance information."""
        pass
    
    @abstractmethod
    def search_characters_by_pattern(
        self, 
        pattern: str
    ) -> List[CharacterInfo]:
        """
        Search for characters matching a pattern.
        Used for alt detection (e.g., similar names).
        """
        pass
