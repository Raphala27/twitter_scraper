#!/usr/bin/env python3
"""
Position simulation example - analyze tweets and simulate trading performance.
"""

import subprocess
import sys

def position_simulation_example():
    """
    Example 2: Complete analysis with position simulation
    """
    print("🚀 Example 2: Position Simulation")
    print("=" * 50)
    
    # Use the main scraper with simulation
    cmd = [
        sys.executable, "scraper.py",
        "@trader",
        "--limit", "3",
        "--mock",  # Use mock data
        "--simulate",
        "--sim-hours", "2",
        "--no-tools"  # Use simple mode for example
    ]
    
    try:
        # Run the scraper with simulation
        result = subprocess.run(cmd, cwd="..", capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Simulation completed successfully!")
            print("\n📊 Output:")
            print(result.stdout)
        else:
            print("❌ Simulation failed:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error running simulation: {e}")

def mock_vs_real_example():
    """
    Example 3: Comparison between mock and real data modes
    """
    print("\n🚀 Example 3: Mock vs Real Data")
    print("=" * 50)
    
    examples = [
        {
            "name": "Mock Mode (No API calls)",
            "cmd": ["python", "../scraper.py", "@trader", "--limit", "2", "--mock"]
        },
        {
            "name": "Real Data Mode (Requires API keys)",
            "cmd": ["python", "../scraper.py", "@trader", "--limit", "2"]
        }
    ]
    
    for example in examples:
        print(f"\n📋 {example['name']}:")
        print(f"Command: {' '.join(example['cmd'])}")
        print("Note: For real data mode, ensure .env file contains valid API keys")

if __name__ == "__main__":
    position_simulation_example()
    mock_vs_real_example()
