"""Contract analysis for suspicious patterns."""

from typing import List
from sentinel.models.data_models import Contract
from sentinel.models.analysis_result import Flag, FlagSeverity


class ContractAnalyzer:
    """Analyzes contracts for suspicious patterns."""
    
    def analyze(self, contracts: List[Contract]) -> tuple[List[Flag], float]:
        """
        Analyze contracts for suspicious patterns.
        
        Returns:
            Tuple of (flags, risk_score)
        """
        flags = []
        risk_score = 0.0
        
        if not contracts:
            return flags, risk_score
        
        # Pattern 1: High-value failed contracts
        failed_high_value = self._detect_failed_high_value(contracts)
        if failed_high_value:
            flags.append(Flag(
                severity=FlagSeverity.SOFT,
                category="suspicious_contracts",
                title="High-value failed contracts",
                description=f"Found {len(failed_high_value)} high-value contracts that failed",
                confidence=0.6,
                evidence=[f"{c['type']} contract for {c['value']:,.0f} ISK failed" 
                         for c in failed_high_value[:3]]
            ))
            risk_score += min(len(failed_high_value) * 15, 35)
        
        # Pattern 2: Unusual contract patterns (courier with high collateral, low reward)
        unusual_courier = self._detect_unusual_courier(contracts)
        if unusual_courier:
            flags.append(Flag(
                severity=FlagSeverity.SOFT,
                category="suspicious_contracts",
                title="Unusual courier contracts",
                description=f"Found {len(unusual_courier)} courier contracts with suspicious collateral/reward ratios",
                confidence=0.7,
                evidence=[f"Collateral {c['collateral']:,.0f} ISK, reward {c['reward']:,.0f} ISK" 
                         for c in unusual_courier[:3]]
            ))
            risk_score += min(len(unusual_courier) * 10, 25)
        
        # Pattern 3: Rapid contract churning
        churning = self._detect_churning(contracts)
        if churning['detected']:
            flags.append(Flag(
                severity=FlagSeverity.SOFT,
                category="suspicious_contracts",
                title="Contract churning detected",
                description=f"Unusually high contract activity: {churning['rate']:.1f} contracts/day",
                confidence=0.65,
                evidence=churning['evidence']
            ))
            risk_score += 20
        
        return flags, min(risk_score, 100.0)
    
    def _detect_failed_high_value(self, contracts: List[Contract]) -> List[dict]:
        """Detect high-value contracts that failed."""
        failed = []
        
        for contract in contracts:
            if contract.status in ["failed", "deleted"]:
                total_value = contract.price + contract.reward + contract.collateral
                if total_value > 100000000:  # 100M ISK threshold
                    failed.append({
                        'type': contract.contract_type,
                        'value': total_value,
                        'status': contract.status
                    })
        
        return failed
    
    def _detect_unusual_courier(self, contracts: List[Contract]) -> List[dict]:
        """Detect courier contracts with unusual collateral/reward ratios."""
        unusual = []
        
        for contract in contracts:
            if contract.contract_type == "courier":
                if contract.collateral > 0 and contract.reward > 0:
                    ratio = contract.collateral / contract.reward
                    # Unusual if collateral is more than 50x the reward
                    if ratio > 50:
                        unusual.append({
                            'collateral': contract.collateral,
                            'reward': contract.reward,
                            'ratio': ratio
                        })
        
        return unusual
    
    def _detect_churning(self, contracts: List[Contract]) -> dict:
        """Detect rapid contract creation/completion."""
        if len(contracts) < 10:
            return {'detected': False}
        
        # Calculate time span
        sorted_contracts = sorted(contracts, key=lambda c: c.date_issued)
        if len(sorted_contracts) < 2:
            return {'detected': False}
            
        time_span = (sorted_contracts[-1].date_issued - sorted_contracts[0].date_issued).days
        if time_span == 0:
            return {'detected': False}
            
        contracts_per_day = len(contracts) / time_span
        
        # Flag if more than 5 contracts per day on average
        if contracts_per_day > 5:
            return {
                'detected': True,
                'rate': contracts_per_day,
                'evidence': [
                    f"{len(contracts)} contracts over {time_span} days",
                    f"Average {contracts_per_day:.1f} contracts per day"
                ]
            }
        
        return {'detected': False}
