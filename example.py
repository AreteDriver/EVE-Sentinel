#!/usr/bin/env python3
"""
Example usage of Sentinel intelligence analysis engine.

This demonstrates how to use Sentinel to analyze a character
and generate a recruitment vetting report.
"""

from sentinel import SentinelAnalyzer
from sentinel.data_sources import MockDataSource
import json


def print_analysis_report(result):
    """Print a formatted analysis report."""
    print("=" * 80)
    print(f"SENTINEL INTELLIGENCE REPORT")
    print("=" * 80)
    print(f"Character: {result.character_name} (ID: {result.character_id})")
    print(f"Corporation: {result.metadata.get('corporation', 'Unknown')}")
    print(f"Alliance: {result.metadata.get('alliance', 'Unknown')}")
    print(f"Analysis Date: {result.analyzed_at}")
    print("=" * 80)
    
    # Risk Score Summary
    print("\n--- RISK ASSESSMENT ---")
    print(f"Overall Risk Score: {result.overall_risk_score:.1f}/100")
    
    risk_level = "LOW"
    if result.overall_risk_score > 70:
        risk_level = "HIGH"
    elif result.overall_risk_score > 40:
        risk_level = "MODERATE"
    print(f"Risk Level: {risk_level}")
    
    print("\nRisk Breakdown:")
    print(f"  - History Risk: {result.risk_score.history_risk:.1f}/100")
    print(f"  - Spy Indicators: {result.risk_score.spy_risk:.1f}/100")
    print(f"  - Alt Relationship: {result.risk_score.alt_relationship_risk:.1f}/100")
    print(f"  - Money Laundering: {result.risk_score.money_laundering_risk:.1f}/100")
    print(f"  - Contract Risk: {result.risk_score.contract_risk:.1f}/100")
    
    # Flags
    if result.hard_flags:
        print("\n--- HARD FLAGS (DEFINITE CONCERNS) ---")
        for i, flag in enumerate(result.hard_flags, 1):
            print(f"{i}. [{flag.category}] {flag.title}")
            print(f"   {flag.description}")
            print(f"   Confidence: {flag.confidence:.0%}")
            if flag.evidence:
                print(f"   Evidence: {'; '.join(flag.evidence[:2])}")
    
    if result.soft_flags:
        print("\n--- SOFT FLAGS (SUSPICIOUS PATTERNS) ---")
        for i, flag in enumerate(result.soft_flags, 1):
            print(f"{i}. [{flag.category}] {flag.title}")
            print(f"   {flag.description}")
            print(f"   Confidence: {flag.confidence:.0%}")
    
    # Alt Analysis
    if result.potential_alts:
        print("\n--- POTENTIAL ALT CHARACTERS ---")
        for i, alt in enumerate(result.potential_alts[:5], 1):
            print(f"{i}. {alt.character_name} (ID: {alt.character_id})")
            print(f"   Probability: {alt.probability:.0%}")
            print(f"   Evidence: {'; '.join(alt.evidence[:2])}")
    
    # Timeline highlights
    if result.timeline:
        print("\n--- RECENT TIMELINE (last 10 events) ---")
        risk_events = [e for e in result.timeline if e.risk_indicator]
        for event in result.timeline[:10]:
            marker = "⚠️ " if event.risk_indicator else "• "
            print(f"{marker}{event.date[:10]} - {event.description}")
    
    # Recruiter Questions
    if result.recruiter_questions:
        print("\n--- RECOMMENDED QUESTIONS FOR RECRUIT ---")
        for i, question in enumerate(result.recruiter_questions, 1):
            print(f"{i}. {question}")
    
    # Recruiter Notes
    if result.recruiter_notes:
        print("\n--- NOTES FOR RECRUITER ---")
        for note in result.recruiter_notes:
            print(f"• {note}")
    
    print("\n" + "=" * 80)
    print("END OF REPORT")
    print("=" * 80)


def main():
    """Main example function."""
    print("Sentinel Intelligence Analysis Engine - Example\n")
    
    # Initialize with mock data source
    # In production, replace this with your actual data source
    data_source = MockDataSource()
    
    # Create analyzer
    analyzer = SentinelAnalyzer(data_source)
    
    # Analyze a character
    print("Analyzing character 12345...\n")
    result = analyzer.analyze_character(12345)
    
    if result is None:
        print("Character not found!")
        return
    
    # Print formatted report
    print_analysis_report(result)
    
    # Optionally export to JSON
    print("\n--- EXPORTING TO JSON ---")
    json_output = result.model_dump_json(indent=2)
    with open("/tmp/sentinel_report.json", "w") as f:
        f.write(json_output)
    print("Report exported to /tmp/sentinel_report.json")
    
    # If you have networkx and matplotlib installed, you can visualize the alt network
    try:
        if result.alt_network_graph:
            from sentinel.outputs.graph import GraphGenerator
            graph_gen = GraphGenerator()
            print("\n--- GENERATING ALT NETWORK VISUALIZATION ---")
            graph_gen.visualize_graph(result.alt_network_graph, "/tmp/alt_network.png")
            print("Alt network graph saved to /tmp/alt_network.png")
    except ImportError:
        print("\n(Install networkx and matplotlib to generate alt network visualizations)")
    except Exception as e:
        print(f"\nCould not generate visualization: {e}")


if __name__ == "__main__":
    main()
