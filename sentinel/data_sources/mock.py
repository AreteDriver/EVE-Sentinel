"""Mock data source for testing and examples."""

from datetime import datetime, timedelta
from typing import List, Optional
from sentinel.data_sources.base import DataSource
from sentinel.models.data_models import (
    CharacterInfo,
    CorporationHistory,
    Transaction,
    Contract,
    Contact,
    AllianceInfo,
)


class MockDataSource(DataSource):
    """
    Mock data source for testing and demonstrations.
    
    Returns realistic sample data for EVE Online characters.
    """
    
    def __init__(self):
        """Initialize with some mock data."""
        self._characters = {
            12345: CharacterInfo(
                character_id=12345,
                character_name="John Doe",
                corporation_id=1001,
                corporation_name="Test Corporation",
                alliance_id=2001,
                alliance_name="Test Alliance",
                security_status=2.5,
            ),
            67890: CharacterInfo(
                character_id=67890,
                character_name="Jane Smith",
                corporation_id=1002,
                corporation_name="Another Corp",
                security_status=-5.0,
            ),
        }
    
    def get_character_info(self, character_id: int) -> Optional[CharacterInfo]:
        """Get basic character information."""
        return self._characters.get(character_id)
    
    def get_corporation_history(self, character_id: int) -> List[CorporationHistory]:
        """Get character's corporation employment history."""
        if character_id == 12345:
            return [
                CorporationHistory(
                    corporation_id=1001,
                    corporation_name="Test Corporation",
                    start_date=datetime.now() - timedelta(days=365),
                    end_date=None,
                ),
                CorporationHistory(
                    corporation_id=999,
                    corporation_name="Previous Corp",
                    start_date=datetime.now() - timedelta(days=730),
                    end_date=datetime.now() - timedelta(days=365),
                ),
            ]
        return []
    
    def get_transactions(
        self, 
        character_id: int, 
        limit: Optional[int] = None
    ) -> List[Transaction]:
        """Get character's transaction history."""
        base_transactions = [
            Transaction(
                transaction_id=1,
                date=datetime.now() - timedelta(days=1),
                client_id=67890,
                amount=1000000.0,
                description="Test transaction",
                journal_ref_type="player_trading",
            ),
            Transaction(
                transaction_id=2,
                date=datetime.now() - timedelta(days=2),
                client_id=99999,
                amount=5000000.0,
                description="Bounty prizes",
                journal_ref_type="bounty_prizes",
            ),
        ]
        if limit:
            return base_transactions[:limit]
        return base_transactions
    
    def get_contracts(
        self, 
        character_id: int, 
        limit: Optional[int] = None
    ) -> List[Contract]:
        """Get character's contract history."""
        base_contracts = [
            Contract(
                contract_id=1,
                issuer_id=character_id,
                assignee_id=67890,
                date_issued=datetime.now() - timedelta(days=5),
                contract_type="item_exchange",
                status="completed",
                price=500000.0,
            ),
        ]
        if limit:
            return base_contracts[:limit]
        return base_contracts
    
    def get_contacts(self, character_id: int) -> List[Contact]:
        """Get character's known contacts/associates."""
        return [
            Contact(
                contact_id=67890,
                contact_name="Jane Smith",
                contact_type="character",
                standing=10.0,
            ),
            Contact(
                contact_id=1002,
                contact_name="Another Corp",
                contact_type="corporation",
                standing=5.0,
            ),
        ]
    
    def get_alliance_info(self, alliance_id: int) -> Optional[AllianceInfo]:
        """Get alliance information."""
        if alliance_id == 2001:
            return AllianceInfo(
                alliance_id=2001,
                alliance_name="Test Alliance",
                ticker="TEST",
                date_founded=datetime.now() - timedelta(days=1000),
                is_hostile=False,
            )
        return None
    
    def search_characters_by_pattern(self, pattern: str) -> List[CharacterInfo]:
        """Search for characters matching a pattern."""
        results = []
        for char in self._characters.values():
            if pattern.lower() in char.character_name.lower():
                results.append(char)
        return results
