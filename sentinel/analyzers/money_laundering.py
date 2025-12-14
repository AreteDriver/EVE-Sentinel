"""Money laundering pattern detection."""

from typing import List
from collections import defaultdict
from datetime import timedelta
from sentinel.models.data_models import Transaction
from sentinel.models.analysis_result import Flag, FlagSeverity


class MoneyLaunderingDetector:
    """Detects suspicious financial patterns that may indicate money laundering."""
    
    def analyze(self, transactions: List[Transaction]) -> tuple[List[Flag], float]:
        """
        Analyze transactions for money laundering patterns.
        
        Returns:
            Tuple of (flags, risk_score)
        """
        flags = []
        risk_score = 0.0
        
        if not transactions:
            return flags, risk_score
        
        # Sort transactions by date
        sorted_txns = sorted(transactions, key=lambda t: t.date)
        
        # Pattern 1: Rapid round-trip transactions (ISK in, then immediately out)
        round_trips = self._detect_round_trips(sorted_txns)
        if round_trips:
            flags.append(Flag(
                severity=FlagSeverity.SOFT,
                category="money_laundering",
                title="Round-trip ISK transfers detected",
                description=f"Found {len(round_trips)} instances of ISK being received and then sent out rapidly",
                confidence=min(len(round_trips) * 0.2, 0.9),
                evidence=[f"{rt['in_amount']:,.0f} ISK in, {rt['out_amount']:,.0f} ISK out within {rt['time_diff']} hours" 
                         for rt in round_trips[:3]]
            ))
            risk_score += min(len(round_trips) * 15, 40)
        
        # Pattern 2: Structuring (many small transactions to avoid detection)
        structuring = self._detect_structuring(sorted_txns)
        if structuring['detected']:
            flags.append(Flag(
                severity=FlagSeverity.SOFT,
                category="money_laundering",
                title="Possible structuring detected",
                description=f"Multiple small transactions ({structuring['count']}) just below typical thresholds",
                confidence=structuring['confidence'],
                evidence=structuring['evidence']
            ))
            risk_score += 25
        
        # Pattern 3: Unusually large single transactions
        large_txns = self._detect_large_transactions(sorted_txns)
        if large_txns:
            flags.append(Flag(
                severity=FlagSeverity.SOFT,
                category="money_laundering",
                title="Unusually large transactions",
                description=f"Found {len(large_txns)} transactions significantly above average",
                confidence=0.5,
                evidence=[f"{t['amount']:,.0f} ISK ({t['times_avg']:.1f}x average)" for t in large_txns[:3]]
            ))
            risk_score += min(len(large_txns) * 10, 30)
        
        return flags, min(risk_score, 100.0)
    
    def _detect_round_trips(self, transactions: List[Transaction]) -> List[dict]:
        """Detect rapid in-then-out ISK transfers."""
        round_trips = []
        
        for i in range(len(transactions) - 1):
            txn_in = transactions[i]
            if txn_in.amount <= 0:
                continue
                
            # Look for matching outgoing transaction within 24 hours
            for j in range(i + 1, min(i + 10, len(transactions))):
                txn_out = transactions[j]
                if txn_out.amount >= 0:
                    continue
                    
                time_diff = (txn_out.date - txn_in.date).total_seconds() / 3600
                if time_diff > 24:
                    break
                    
                # Check if amounts are similar (within 10%)
                if abs(txn_in.amount + txn_out.amount) / txn_in.amount < 0.1:
                    round_trips.append({
                        'in_amount': txn_in.amount,
                        'out_amount': abs(txn_out.amount),
                        'time_diff': round(time_diff, 1)
                    })
                    break
        
        return round_trips
    
    def _detect_structuring(self, transactions: List[Transaction]) -> dict:
        """Detect structuring patterns (many small transactions)."""
        if len(transactions) < 10:
            return {'detected': False}
        
        # Group by day
        daily_txns = defaultdict(list)
        for txn in transactions:
            day = txn.date.date()
            if txn.journal_ref_type == "player_trading":
                daily_txns[day].append(txn)
        
        # Look for days with many small, similar-sized transactions
        suspicious_days = []
        for day, txns in daily_txns.items():
            if len(txns) >= 5:
                amounts = [abs(t.amount) for t in txns]
                avg = sum(amounts) / len(amounts)
                
                # Check if transactions are similar in size (low variance)
                variance = sum((a - avg) ** 2 for a in amounts) / len(amounts)
                std_dev = variance ** 0.5
                
                if std_dev / avg < 0.3:  # Low variance relative to mean
                    suspicious_days.append({
                        'day': day,
                        'count': len(txns),
                        'avg_amount': avg
                    })
        
        if suspicious_days:
            return {
                'detected': True,
                'count': sum(d['count'] for d in suspicious_days),
                'confidence': min(len(suspicious_days) * 0.25, 0.85),
                'evidence': [f"{d['count']} similar transactions on {d['day']}" for d in suspicious_days[:3]]
            }
        
        return {'detected': False}
    
    def _detect_large_transactions(self, transactions: List[Transaction]) -> List[dict]:
        """Detect unusually large transactions."""
        if len(transactions) < 5:
            return []
        
        amounts = [abs(t.amount) for t in transactions if t.journal_ref_type == "player_trading"]
        if not amounts:
            return []
            
        avg = sum(amounts) / len(amounts)
        threshold = avg * 5  # 5x average
        
        large_txns = []
        for txn in transactions:
            if abs(txn.amount) > threshold and txn.journal_ref_type == "player_trading":
                large_txns.append({
                    'amount': abs(txn.amount),
                    'times_avg': abs(txn.amount) / avg
                })
        
        return large_txns
