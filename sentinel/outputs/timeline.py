"""Timeline generation for character analysis."""

from typing import List
from datetime import datetime
from sentinel.models.data_models import CorporationHistory, Transaction, Contract
from sentinel.models.analysis_result import TimelineEvent


class TimelineGenerator:
    """Generates timeline of significant events for a character."""
    
    def generate(
        self,
        corp_history: List[CorporationHistory],
        transactions: List[Transaction],
        contracts: List[Contract],
        flags: List
    ) -> List[TimelineEvent]:
        """
        Generate a timeline of significant events.
        
        Returns:
            Sorted list of timeline events (most recent first)
        """
        events = []
        
        # Add corporation changes
        for corp in corp_history:
            events.append(TimelineEvent(
                date=corp.start_date.isoformat(),
                event_type="corp_join",
                description=f"Joined {corp.corporation_name}",
                risk_indicator=False
            ))
            
            if corp.end_date:
                events.append(TimelineEvent(
                    date=corp.end_date.isoformat(),
                    event_type="corp_leave",
                    description=f"Left {corp.corporation_name}",
                    risk_indicator=corp.is_deleted  # Flag if corp was deleted
                ))
        
        # Add significant transactions (large amounts)
        if transactions:
            amounts = [abs(t.amount) for t in transactions]
            avg_amount = sum(amounts) / len(amounts) if amounts else 0
            threshold = avg_amount * 3  # 3x average
            
            for txn in transactions:
                if abs(txn.amount) > threshold:
                    events.append(TimelineEvent(
                        date=txn.date.isoformat(),
                        event_type="large_transaction",
                        description=f"Large transaction: {txn.amount:,.0f} ISK ({txn.journal_ref_type})",
                        risk_indicator=txn.journal_ref_type == "player_trading"
                    ))
        
        # Add contract events (only failed high-value ones as risk indicators)
        for contract in contracts:
            if contract.status in ["failed", "deleted"]:
                total_value = contract.price + contract.reward + contract.collateral
                if total_value > 50000000:  # 50M ISK
                    events.append(TimelineEvent(
                        date=contract.date_issued.isoformat(),
                        event_type="contract_failed",
                        description=f"Failed {contract.contract_type} contract ({total_value:,.0f} ISK)",
                        risk_indicator=True
                    ))
        
        # Add flag events
        for flag in flags:
            if hasattr(flag, 'severity') and flag.severity.value == "hard":
                # Add hard flags to timeline
                events.append(TimelineEvent(
                    date=datetime.now().isoformat(),
                    event_type="flag",
                    description=f"RISK FLAG: {flag.title}",
                    risk_indicator=True
                ))
        
        # Sort by date descending (most recent first)
        events.sort(key=lambda e: e.date, reverse=True)
        
        return events
