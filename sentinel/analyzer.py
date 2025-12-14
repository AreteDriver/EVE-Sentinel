"""Main Sentinel analyzer that coordinates all analysis modules."""

from datetime import datetime
from typing import Optional
from sentinel.data_sources.base import DataSource
from sentinel.models.analysis_result import AnalysisResult, RiskScore
from sentinel.analyzers import (
    AltDetector,
    MoneyLaunderingDetector,
    ContractAnalyzer,
    HistoryAnalyzer,
    SpyDetector,
)
from sentinel.outputs import TimelineGenerator, QuestionGenerator, GraphGenerator


class SentinelAnalyzer:
    """
    Main Sentinel intelligence analysis engine.
    
    Coordinates all analysis modules and produces comprehensive
    recruitment vetting reports.
    """
    
    def __init__(self, data_source: DataSource):
        """
        Initialize the analyzer.
        
        Args:
            data_source: Data source implementing the DataSource interface
        """
        self.data_source = data_source
        
        # Initialize analyzers
        self.alt_detector = AltDetector()
        self.money_laundering_detector = MoneyLaunderingDetector()
        self.contract_analyzer = ContractAnalyzer()
        self.history_analyzer = HistoryAnalyzer()
        self.spy_detector = SpyDetector()
        
        # Initialize output generators
        self.timeline_generator = TimelineGenerator()
        self.question_generator = QuestionGenerator()
        self.graph_generator = GraphGenerator()
    
    def analyze_character(self, character_id: int) -> Optional[AnalysisResult]:
        """
        Perform comprehensive analysis of a character.
        
        Args:
            character_id: EVE Online character ID
            
        Returns:
            AnalysisResult with complete risk assessment, or None if character not found
        """
        # Fetch character data
        char_info = self.data_source.get_character_info(character_id)
        if not char_info:
            return None
        
        corp_history = self.data_source.get_corporation_history(character_id)
        transactions = self.data_source.get_transactions(character_id, limit=1000)
        contracts = self.data_source.get_contracts(character_id, limit=500)
        contacts = self.data_source.get_contacts(character_id)
        
        # Run all analyzers
        all_flags = []
        
        # Alt relationship detection
        potential_alts = self.alt_detector.analyze(
            char_info,
            transactions,
            contacts,
            self.data_source.search_characters_by_pattern
        )
        
        # Money laundering detection
        ml_flags, ml_risk = self.money_laundering_detector.analyze(transactions)
        all_flags.extend(ml_flags)
        
        # Contract analysis
        contract_flags, contract_risk = self.contract_analyzer.analyze(contracts)
        all_flags.extend(contract_flags)
        
        # Corporation/Alliance history analysis
        history_flags, history_risk = self.history_analyzer.analyze(
            corp_history,
            self.data_source.get_alliance_info
        )
        all_flags.extend(history_flags)
        
        # Spy indicator detection
        spy_flags, spy_risk = self.spy_detector.analyze(
            char_info,
            corp_history,
            contacts
        )
        all_flags.extend(spy_flags)
        
        # Calculate alt relationship risk based on high-probability alts
        alt_risk = min(
            sum(alt.probability * 20 for alt in potential_alts if alt.probability > 0.5),
            100.0
        )
        
        # Calculate overall risk score (weighted average)
        overall_risk = self._calculate_overall_risk(
            alt_risk, ml_risk, contract_risk, history_risk, spy_risk
        )
        
        # Create risk score breakdown
        risk_score = RiskScore(
            overall=overall_risk,
            alt_relationship_risk=alt_risk,
            money_laundering_risk=ml_risk,
            contract_risk=contract_risk,
            history_risk=history_risk,
            spy_risk=spy_risk
        )
        
        # Separate hard and soft flags
        hard_flags = [f for f in all_flags if f.severity.value == "hard"]
        soft_flags = [f for f in all_flags if f.severity.value == "soft"]
        
        # Generate timeline
        timeline = self.timeline_generator.generate(
            corp_history,
            transactions,
            contracts,
            all_flags
        )
        
        # Generate alt network graph
        alt_graph = None
        if potential_alts:
            alt_graph = self.graph_generator.generate(
                character_id,
                char_info.character_name,
                potential_alts
            )
        
        # Generate recruiter questions and notes
        questions, notes = self.question_generator.generate(
            all_flags,
            potential_alts,
            len(corp_history),
            overall_risk
        )
        
        # Build final result
        result = AnalysisResult(
            character_id=character_id,
            character_name=char_info.character_name,
            analyzed_at=datetime.now().isoformat(),
            risk_score=risk_score,
            overall_risk_score=overall_risk,
            hard_flags=hard_flags,
            soft_flags=soft_flags,
            potential_alts=potential_alts,
            alt_network_graph=alt_graph,
            timeline=timeline,
            recruiter_questions=questions,
            recruiter_notes=notes,
            metadata={
                "corporation": char_info.corporation_name,
                "alliance": char_info.alliance_name,
                "security_status": char_info.security_status,
                "corp_history_count": len(corp_history),
                "transaction_count": len(transactions),
                "contract_count": len(contracts),
            }
        )
        
        return result
    
    def _calculate_overall_risk(
        self,
        alt_risk: float,
        ml_risk: float,
        contract_risk: float,
        history_risk: float,
        spy_risk: float
    ) -> float:
        """
        Calculate weighted overall risk score.
        
        Weights:
        - History risk: 30% (most important for recruitment)
        - Spy risk: 25%
        - Alt risk: 20%
        - Money laundering: 15%
        - Contract risk: 10%
        """
        weights = {
            'history': 0.30,
            'spy': 0.25,
            'alt': 0.20,
            'ml': 0.15,
            'contract': 0.10
        }
        
        overall = (
            history_risk * weights['history'] +
            spy_risk * weights['spy'] +
            alt_risk * weights['alt'] +
            ml_risk * weights['ml'] +
            contract_risk * weights['contract']
        )
        
        return min(overall, 100.0)
