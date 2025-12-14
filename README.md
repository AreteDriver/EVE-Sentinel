# Sentinel - EVE Online Intelligence Analysis Engine

Sentinel is a read-only intelligence analysis engine for EVE Online recruitment vetting. It consumes existing alliance intel data (DB views or internal APIs) to perform deep analysis and provide actionable intelligence for recruitment decisions.

## Features

- **Alt Relationship Detection**: Identify possible alternate characters through behavioral patterns, transaction history, and network analysis
- **Money Laundering Detection**: Detect suspicious financial patterns and unusual ISK flows
- **Contract Analysis**: Flag suspicious contracts and trading patterns
- **Corporation/Alliance History Risk Analysis**: Evaluate risks based on character employment history
- **Spy Indicator Detection**: Identify potential spies through behavioral and historical indicators

## Output

Sentinel provides:
- **Risk Scores**: Explainable, weighted risk assessments
- **Flags**: Hard flags (definite issues) and soft flags (suspicious patterns)
- **Alt Probability Graphs**: Visual network analysis of potential alt relationships
- **Timelines**: Historical event timelines for analysis
- **Recruiter Questions**: Auto-generated targeted questions based on findings

## Architecture

Sentinel is designed as a **read-only analysis engine**:
- No authentication or permission system
- No direct ESI token handling
- Consumes data from existing alliance intel sources (database views or internal APIs)
- Pure analysis and reporting

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from sentinel import SentinelAnalyzer
from sentinel.data_sources import MockDataSource

# Initialize with your data source
data_source = MockDataSource()  # Replace with your DB/API connector
analyzer = SentinelAnalyzer(data_source)

# Analyze a character
result = analyzer.analyze_character(character_id=12345)

# Get the risk report
print(f"Overall Risk Score: {result.overall_risk_score}")
print(f"Hard Flags: {result.hard_flags}")
print(f"Soft Flags: {result.soft_flags}")

# Generate recruiter questions
for question in result.recruiter_questions:
    print(f"- {question}")
```

## Data Source Integration

Sentinel requires a data source that provides:
- Character information (name, corporation history, etc.)
- Transaction history
- Contract data
- Known associates/contacts
- Corporation/Alliance information

See `sentinel/data_sources/base.py` for the interface specification.

## License

MIT License - see LICENSE file for details.