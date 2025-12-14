"""Corporation/Alliance history risk analysis."""

from typing import List
from datetime import datetime, timedelta
from sentinel.models.data_models import CorporationHistory, AllianceInfo
from sentinel.models.analysis_result import Flag, FlagSeverity


class HistoryAnalyzer:
    """Analyzes corporation and alliance history for risk indicators."""
    
    def analyze(
        self,
        corp_history: List[CorporationHistory],
        get_alliance_info_func
    ) -> tuple[List[Flag], float]:
        """
        Analyze corporation/alliance history for risks.
        
        Returns:
            Tuple of (flags, risk_score)
        """
        flags = []
        risk_score = 0.0
        
        if not corp_history:
            return flags, risk_score
        
        # Pattern 1: Corp hopping (many short-term employments)
        corp_hopping = self._detect_corp_hopping(corp_history)
        if corp_hopping['detected']:
            severity = FlagSeverity.HARD if corp_hopping['count'] > 10 else FlagSeverity.SOFT
            flags.append(Flag(
                severity=severity,
                category="history_risk",
                title="Frequent corporation changes",
                description=f"Changed corporations {corp_hopping['count']} times, average tenure {corp_hopping['avg_days']:.0f} days",
                confidence=min(corp_hopping['count'] * 0.08, 0.9),
                evidence=[f"{corp_hopping['count']} corporations in employment history"]
            ))
            risk_score += min(corp_hopping['count'] * 5, 50)
        
        # Pattern 2: Employment in hostile/enemy alliances
        hostile_history = self._detect_hostile_history(corp_history, get_alliance_info_func)
        if hostile_history:
            flags.append(Flag(
                severity=FlagSeverity.HARD,
                category="history_risk",
                title="Employment in hostile alliance",
                description=f"Previously employed in {len(hostile_history)} known hostile alliance(s)",
                confidence=1.0,
                evidence=[f"Employed in {h['alliance_name']}" for h in hostile_history]
            ))
            risk_score += 60
        
        # Pattern 3: Employment in deleted/disbanded corporations
        deleted_corps = self._detect_deleted_corps(corp_history)
        if deleted_corps:
            flags.append(Flag(
                severity=FlagSeverity.SOFT,
                category="history_risk",
                title="Employment in deleted corporations",
                description=f"Employed in {len(deleted_corps)} corporation(s) that no longer exist",
                confidence=0.6,
                evidence=[f"{c['corp_name']} (deleted)" for c in deleted_corps[:3]]
            ))
            risk_score += min(len(deleted_corps) * 10, 30)
        
        # Pattern 4: Very recent corp join
        recent_join = self._detect_recent_join(corp_history)
        if recent_join:
            flags.append(Flag(
                severity=FlagSeverity.SOFT,
                category="history_risk",
                title="Very recent corporation join",
                description=f"Joined current corporation only {recent_join['days']} days ago",
                confidence=0.5,
                evidence=[f"Current tenure: {recent_join['days']} days"]
            ))
            risk_score += 15
        
        return flags, min(risk_score, 100.0)
    
    def _detect_corp_hopping(self, corp_history: List[CorporationHistory]) -> dict:
        """Detect frequent corporation changes."""
        if len(corp_history) < 3:
            return {'detected': False}
        
        # Calculate average tenure
        total_days = 0
        count = 0
        
        for corp in corp_history:
            if corp.end_date:
                days = (corp.end_date - corp.start_date).days
                total_days += days
                count += 1
        
        if count == 0:
            return {'detected': False}
        
        avg_days = total_days / count
        
        # Flag if average tenure is less than 90 days and more than 5 corps
        if avg_days < 90 and len(corp_history) >= 5:
            return {
                'detected': True,
                'count': len(corp_history),
                'avg_days': avg_days
            }
        
        return {'detected': False}
    
    def _detect_hostile_history(self, corp_history: List[CorporationHistory], get_alliance_info_func) -> List[dict]:
        """Detect employment in hostile alliances."""
        hostile = []
        
        # This would need alliance IDs from corp history
        # For now, this is a placeholder showing the pattern
        # In a real implementation, you'd query alliance info for each corp
        
        return hostile
    
    def _detect_deleted_corps(self, corp_history: List[CorporationHistory]) -> List[dict]:
        """Detect employment in corporations that no longer exist."""
        deleted = []
        
        for corp in corp_history:
            if corp.is_deleted:
                deleted.append({
                    'corp_id': corp.corporation_id,
                    'corp_name': corp.corporation_name
                })
        
        return deleted
    
    def _detect_recent_join(self, corp_history: List[CorporationHistory]) -> dict:
        """Detect very recent corporation join."""
        if not corp_history:
            return None
        
        # Find current corporation (no end_date)
        current = None
        for corp in corp_history:
            if corp.end_date is None:
                current = corp
                break
        
        if not current:
            return None
        
        days_in_corp = (datetime.now() - current.start_date).days
        
        # Flag if joined within last 7 days
        if days_in_corp <= 7:
            return {
                'days': days_in_corp,
                'corp_name': current.corporation_name
            }
        
        return None
