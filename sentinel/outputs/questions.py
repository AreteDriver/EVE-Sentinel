"""Recruiter question generation."""

from typing import List
from sentinel.models.analysis_result import Flag, AltRelationship


class QuestionGenerator:
    """Generates targeted recruiter questions based on analysis findings."""
    
    def generate(
        self,
        flags: List[Flag],
        potential_alts: List[AltRelationship],
        corp_history_count: int,
        risk_score: float
    ) -> tuple[List[str], List[str]]:
        """
        Generate recruiter questions and notes.
        
        Returns:
            Tuple of (questions, notes)
        """
        questions = []
        notes = []
        
        # Questions based on flags
        flag_categories = set(flag.category for flag in flags)
        
        if "money_laundering" in flag_categories:
            questions.append(
                "Can you explain the nature of your recent ISK transfers, particularly "
                "any large or unusual transactions?"
            )
            notes.append("Review transaction history carefully for money laundering patterns")
        
        if "suspicious_contracts" in flag_categories:
            questions.append(
                "We noticed some unusual contract activity. Can you provide context for "
                "any failed or high-value contracts?"
            )
        
        if "history_risk" in flag_categories:
            if corp_history_count >= 5:
                questions.append(
                    f"You've been in {corp_history_count} corporations. Can you walk us through "
                    "your employment history and reasons for leaving each corp?"
                )
                notes.append("Corp hopper - verify reasons for frequent changes")
        
        if "spy_indicator" in flag_categories:
            questions.append(
                "What attracted you to our corporation, and what are your long-term goals "
                "in EVE Online?"
            )
            notes.append("Potential spy indicators detected - thorough vetting required")
        
        # Questions about alts
        if potential_alts:
            high_prob_alts = [alt for alt in potential_alts if alt.probability > 0.6]
            if high_prob_alts:
                alt_names = ", ".join([alt.character_name for alt in high_prob_alts[:3]])
                questions.append(
                    f"Do you have any relationship with the following characters: {alt_names}?"
                )
                notes.append(f"Possible alts detected: {len(high_prob_alts)} high-probability matches")
        
        # General questions based on risk score
        if risk_score > 70:
            questions.append(
                "Can you provide references from previous corporations or alliances you've been in?"
            )
            notes.append(f"HIGH RISK (score: {risk_score:.0f}) - Request additional verification")
        elif risk_score > 40:
            notes.append(f"MODERATE RISK (score: {risk_score:.0f}) - Standard vetting procedures")
        
        # Hard flags get special attention
        hard_flags = [f for f in flags if f.severity.value == "hard"]
        if hard_flags:
            notes.append(
                f"HARD FLAGS DETECTED ({len(hard_flags)}): "
                + ", ".join([f.title for f in hard_flags[:3]])
            )
            questions.append(
                "We have some concerns based on your history. Can you address the following: "
                + "; ".join([f.title for f in hard_flags[:2]])
            )
        
        # Always ask about current activities
        questions.append(
            "What are your current primary activities in EVE (PvP, PvE, industry, etc.) "
            "and what timezone do you typically play in?"
        )
        
        return questions, notes
