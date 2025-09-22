#!/usr/bin/env python3
"""
Custom analysis example - advanced usage with custom prompts and analysis.
"""

import subprocess
import sys

def custom_prompt_example():
    """
    Example 4: Using custom system prompts for specialized analysis
    """
    print("🚀 Example 4: Custom Analysis Prompts")
    print("=" * 50)
    
    # Different analysis focuses
    analysis_types = [
        {
            "name": "Risk Analysis",
            "prompt": "Focus on risk assessment and position sizing in trading signals.",
            "description": "Analyzes risk factors and leverage usage"
        },
        {
            "name": "Technical Analysis",
            "prompt": "Extract technical analysis indicators and chart patterns from trading posts.",
            "description": "Focuses on technical indicators and patterns"
        },
        {
            "name": "Sentiment Analysis", 
            "prompt": "Analyze market sentiment and trader confidence levels from social media posts.",
            "description": "Evaluates market mood and confidence"
        }
    ]
    
    for analysis in analysis_types:
        print(f"\n📊 {analysis['name']}:")
        print(f"Description: {analysis['description']}")
        print(f"Command example:")
        cmd = [
            "python", "scraper.py",
            "@trader", 
            "--limit", "3",
            "--mock",
            "--system", f'"{analysis["prompt"]}"'
        ]
        print(f"  {' '.join(cmd)}")

def json_output_example():
    """
    Example 5: JSON output for programmatic processing
    """
    print("\n🚀 Example 5: JSON Output for Integration")
    print("=" * 50)
    
    print("For programmatic processing, use JSON output:")
    print("Command: python scraper.py @trader --limit 3 --mock --json")
    print("\nThis outputs structured JSON that can be:")
    print("• Parsed by other applications")
    print("• Stored in databases")
    print("• Used for further analysis")
    print("• Integrated into trading systems")

def performance_testing_example():
    """
    Example 6: Performance testing with different parameters
    """
    print("\n🚀 Example 6: Performance Testing")
    print("=" * 50)
    
    test_scenarios = [
        {
            "name": "Quick Test",
            "params": "--limit 2 --sim-hours 1",
            "use_case": "Fast testing during development"
        },
        {
            "name": "Standard Analysis", 
            "params": "--limit 5 --sim-hours 6",
            "use_case": "Regular trading analysis"
        },
        {
            "name": "Deep Analysis",
            "params": "--limit 10 --sim-hours 24", 
            "use_case": "Comprehensive performance evaluation"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📈 {scenario['name']}:")
        print(f"  Use case: {scenario['use_case']}")
        print(f"  Command: python scraper.py @trader {scenario['params']} --mock --simulate")

if __name__ == "__main__":
    custom_prompt_example()
    json_output_example() 
    performance_testing_example()
