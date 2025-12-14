"""Analysis result models."""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class FlagSeverity(str, Enum):
    """Severity levels for flags."""
    HARD = "hard"  # Definite red flags
    SOFT = "soft"  # Suspicious but not conclusive


class Flag(BaseModel):
    """A security or risk flag."""
    severity: FlagSeverity
    category: str  # e.g., "alt_detection", "money_laundering", "spy_indicator"
    title: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)  # 0.0 to 1.0
    evidence: List[str] = Field(default_factory=list)
    

class AltRelationship(BaseModel):
    """Potential alt character relationship."""
    character_id: int
    character_name: str
    probability: float = Field(ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)
    shared_behaviors: List[str] = Field(default_factory=list)


class TimelineEvent(BaseModel):
    """An event on the character's timeline."""
    date: str  # ISO format
    event_type: str
    description: str
    risk_indicator: bool = False
    

class RiskScore(BaseModel):
    """Risk score breakdown."""
    overall: float = Field(ge=0.0, le=100.0)
    alt_relationship_risk: float = Field(ge=0.0, le=100.0, default=0.0)
    money_laundering_risk: float = Field(ge=0.0, le=100.0, default=0.0)
    contract_risk: float = Field(ge=0.0, le=100.0, default=0.0)
    history_risk: float = Field(ge=0.0, le=100.0, default=0.0)
    spy_risk: float = Field(ge=0.0, le=100.0, default=0.0)
    

class AnalysisResult(BaseModel):
    """Complete analysis result for a character."""
    character_id: int
    character_name: str
    analyzed_at: str  # ISO format timestamp
    
    # Risk assessment
    risk_score: RiskScore
    overall_risk_score: float = Field(ge=0.0, le=100.0)
    
    # Flags
    hard_flags: List[Flag] = Field(default_factory=list)
    soft_flags: List[Flag] = Field(default_factory=list)
    
    # Alt analysis
    potential_alts: List[AltRelationship] = Field(default_factory=list)
    alt_network_graph: Optional[Dict[str, Any]] = None  # Graph data for visualization
    
    # Timeline
    timeline: List[TimelineEvent] = Field(default_factory=list)
    
    # Recruiter guidance
    recruiter_questions: List[str] = Field(default_factory=list)
    recruiter_notes: List[str] = Field(default_factory=list)
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
