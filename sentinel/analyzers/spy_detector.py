"""Spy indicator detection."""

from typing import List
from sentinel.models.data_models import CharacterInfo, CorporationHistory, Contact
from sentinel.models.analysis_result import Flag, FlagSeverity


class SpyDetector:
    """Detects potential spy indicators."""
    
    def analyze(
        self,
        character_info: CharacterInfo,
        corp_history: List[CorporationHistory],
        contacts: List[Contact]
    ) -> tuple[List[Flag], float]:
        """
        Analyze for spy indicators.
        
        Returns:
            Tuple of (flags, risk_score)
        """
        flags = []
        risk_score = 0.0
        
        # Pattern 1: Negative security status
        if character_info.security_status < -2.0:
            flags.append(Flag(
                severity=FlagSeverity.SOFT,
                category="spy_indicator",
                title="Negative security status",
                description=f"Character has security status of {character_info.security_status:.1f}",
                confidence=0.4,
                evidence=[f"Security status: {character_info.security_status:.1f}"]
            ))
            risk_score += 10
        
        # Pattern 2: Recent rapid corp changes before application
        recent_hopping = self._detect_recent_rapid_changes(corp_history)
        if recent_hopping['detected']:
            flags.append(Flag(
                severity=FlagSeverity.SOFT,
                category="spy_indicator",
                title="Recent rapid corporation changes",
                description=f"{recent_hopping['count']} corporation changes in last {recent_hopping['days']} days",
                confidence=0.7,
                evidence=[f"Changed corps {recent_hopping['count']} times recently"]
            ))
            risk_score += 25
        
        # Pattern 3: Contacts in multiple competing organizations
        competing_contacts = self._detect_competing_contacts(contacts)
        if competing_contacts:
            flags.append(Flag(
                severity=FlagSeverity.SOFT,
                category="spy_indicator",
                title="Contacts in competing organizations",
                description=f"Has contacts in {len(competing_contacts)} different organizations",
                confidence=0.5,
                evidence=[f"Contact with {c['contact_name']}" for c in competing_contacts[:3]]
            ))
            risk_score += 15
        
        # Pattern 4: Very short total play time indicated by few corps
        if len(corp_history) == 1:
            first_corp = corp_history[0]
            if first_corp.end_date is None:
                from datetime import datetime
                days_played = (datetime.now() - first_corp.start_date).days
                if days_played < 30:
                    flags.append(Flag(
                        severity=FlagSeverity.SOFT,
                        category="spy_indicator",
                        title="Very new character",
                        description=f"Character created only {days_played} days ago",
                        confidence=0.6,
                        evidence=[f"Account age: {days_played} days"]
                    ))
                    risk_score += 20
        
        return flags, min(risk_score, 100.0)
    
    def _detect_recent_rapid_changes(self, corp_history: List[CorporationHistory]) -> dict:
        """Detect rapid recent corporation changes."""
        from datetime import datetime, timedelta
        
        if len(corp_history) < 3:
            return {'detected': False}
        
        # Check last 90 days
        cutoff = datetime.now() - timedelta(days=90)
        recent_changes = []
        
        for corp in corp_history:
            if corp.start_date >= cutoff:
                recent_changes.append(corp)
        
        if len(recent_changes) >= 3:
            return {
                'detected': True,
                'count': len(recent_changes),
                'days': 90
            }
        
        return {'detected': False}
    
    def _detect_competing_contacts(self, contacts: List[Contact]) -> List[dict]:
        """Detect contacts in multiple different organizations."""
        # This is a simplified version - in reality you'd check if contacts
        # are from competing alliances/corporations
        
        corp_contacts = [c for c in contacts if c.contact_type == "corporation"]
        alliance_contacts = [c for c in contacts if c.contact_type == "alliance"]
        
        competing = []
        
        # If they have contacts in multiple corps/alliances, flag it
        if len(corp_contacts) >= 3 or len(alliance_contacts) >= 2:
            for contact in corp_contacts[:3] + alliance_contacts[:2]:
                competing.append({
                    'contact_id': contact.contact_id,
                    'contact_name': contact.contact_name,
                    'contact_type': contact.contact_type
                })
        
        return competing
