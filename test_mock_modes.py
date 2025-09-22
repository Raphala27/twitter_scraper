#!/usr/bin/env python3
"""
Tests des différents modes mock
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {description}")
    print(f"📝 Commande: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ SUCCÈS")
            # Afficher seulement les lignes importantes
            lines = result.stdout.split('\n')
            for line in lines:
                if any(keyword in line for keyword in ['CONTENU DES TWEETS', 'ANALYSE CONSOLIDÉE', 'RÉSULTATS PERFORMANCES', 'RÉSUMÉ GLOBAL', 'Capital total', 'P&L total', 'ROI']):
                    print(line)
        else:
            print("❌ ERREUR")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    print("🚀 TESTS DES MODES MOCK")
    
    # Test 1: Mock scraping uniquement
    run_command(
        "python3 scraper.py @trader --limit 2 --mock-scraping --no-tools",
        "Mock scraping uniquement (sans simulation)"
    )
    
    # Test 2: Mock positions uniquement (nécessite vraies données Twitter)
    # Note: Ce test échouerait sans vraie API Twitter, donc on le commente
    # run_command(
    #     "python3 scraper.py @trader --limit 2 --mock-positions --simulate --sim-hours 1",
    #     "Mock positions uniquement (avec vraies données Twitter)"
    # )
    
    # Test 3: Les deux modes mock
    run_command(
        "python3 scraper.py @trader --limit 2 --mock-scraping --mock-positions --simulate --sim-hours 1 --no-tools",
        "Les deux modes mock (scraping + positions)"
    )
    
    # Test 4: Mode mock global (équivalent au test 3)
    run_command(
        "python3 scraper.py @trader --limit 2 --mock --simulate --sim-hours 1 --no-tools",
        "Mode mock global (--mock)"
    )
    
    print(f"\n{'='*60}")
    print("✅ TOUS LES TESTS TERMINÉS")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
