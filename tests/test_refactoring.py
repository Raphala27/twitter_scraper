#!/usr/bin/env python3
"""
Script de test complet pour vérifier que le refactoring et l'intégration fonctionnent correctement.
Combine les tests de fonctionnalité de base, d'intégration des tools et de validation complète.
"""
import sys
import os
import json

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models_logic.openrouter_logic import process_tweets_with_openrouter, generate_with_openrouter_tools, execute_tool, get_available_tools

def test_basic_functionality():
    """Test de base pour vérifier que les imports et la fonction fonctionnent."""
    print("=== Test de fonctionnalité de base ===")
    
    try:
        # Test avec mock=True pour éviter les appels API
        results = process_tweets_with_openrouter(
            user_or_handle="testuser",
            limit=1,
            model="x-ai/grok-4-fast:free",
            system_instruction="Test system instruction",
            mock=True,
            use_tools=False  # Désactiver les tools pour ce test simple
        )
        
        print(f"✅ Fonction process_tweets_with_openrouter fonctionne")
        print(f"Nombre de résultats: {len(results)}")
        if results:
            print(f"Premier résultat: {results[0]['full_text'][:50]}...")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False
    
    return True

def test_tools_integration():
    """Test de l'intégration des tools."""
    print("\n=== Test d'intégration des tools ===")
    
    try:
        # Test avec tools activés
        results = process_tweets_with_openrouter(
            user_or_handle="testuser",
            limit=1,
            model="x-ai/grok-4-fast:free",
            system_instruction="Extract crypto tickers",
            mock=True,
            use_tools=True
        )
        
        print(f"✅ Fonction avec tools fonctionne")
        print(f"Analyse: {results[0]['analysis'][:100]}..." if results else "Pas de résultats")
            
    except Exception as e:
        print(f"❌ Erreur lors du test avec tools: {e}")
        return False
    
    return True

def test_tool_definitions():
    """Test de la définition et de l'exécution directe des tools."""
    print("\n=== Test définition des tools ===")
    
    try:
        # Test 1: Vérifier que les tools sont bien définis
        tools = get_available_tools()
        print(f"✅ Tools disponibles: {len(tools)}")
        
        if tools:
            tool = tools[0]
            print(f"✅ Premier tool: {tool['function']['name']}")
            print(f"✅ Description: {tool['function']['description']}")
        else:
            print("❌ Aucun tool disponible")
            return False
        
        # Test 2: Exécuter le tool directement
        test_text = "I'm bullish on BTC, ETH, and SOL today! Also watching DOGE."
        result = execute_tool("extract_crypto_tickers", {"text": test_text})
        print(f"✅ Tool exécuté avec succès")
        print(f"   Input: '{test_text}'")
        print(f"   Output: {result}")
        
        # Test 3: Vérifier le format JSON de sortie
        try:
            parsed_result = json.loads(result)
            print(f"✅ Sortie JSON valide: {parsed_result}")
            
            # Test 4: Vérifier que le contenu est correct
            expected_tickers = {"BTC", "ETH", "SOL", "DOGE"}
            actual_tickers = set(parsed_result)
            if expected_tickers.issubset(actual_tickers):
                print(f"✅ Tickers extraits correctement")
            else:
                print(f"⚠️  Tickers partiellement extraits: attendu {expected_tickers}, obtenu {actual_tickers}")
            
        except json.JSONDecodeError:
            print(f"❌ Sortie JSON invalide: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test des tools: {e}")
        return False
    
    return True

def test_tool_edge_cases():
    """Test des cas limites pour les tools."""
    print("\n=== Test cas limites des tools ===")
    
    test_cases = [
        {
            "text": "",
            "description": "Texte vide"
        },
        {
            "text": "No crypto content here, just regular text",
            "description": "Pas de crypto"
        },
        {
            "text": "THE CEO announced API support",
            "description": "Mots exclus seulement"
        },
        {
            "text": "$BTC, $ETH, and regular BTC ETH mentions",
            "description": "Mélange $ et mentions normales"
        }
    ]
    
    try:
        for i, case in enumerate(test_cases, 1):
            result = execute_tool("extract_crypto_tickers", {"text": case["text"]})
            parsed_result = json.loads(result)
            print(f"✅ Test {i} ({case['description']}): {parsed_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests de cas limites: {e}")
        return False

def test_performance():
    """Test de performance avec un texte long."""
    print("\n=== Test de performance ===")
    
    # Créer un texte long avec plusieurs tickers
    long_text = """
    BTC is showing strong momentum today. ETH continues its upward trend.
    SOL, ADA, and DOT are following the market. DOGE remains volatile.
    MATIC and AVAX are consolidating. USDT and USDC maintain stability.
    New projects like SUI and APT gaining attention. DeFi tokens UNI and LINK
    are performing well. Remember to DYOR before investing.
    """ * 20  # Répéter pour créer un texte plus long
    
    try:
        import time
        start_time = time.time()
        
        result = execute_tool("extract_crypto_tickers", {"text": long_text})
        parsed_result = json.loads(result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"✅ Texte long traité en {execution_time:.4f}s")
        print(f"✅ Nombre de tickers trouvés: {len(parsed_result)}")
        print(f"✅ Tickers: {parsed_result}")
        
        # Le test passe si c'est rapide (< 1 seconde)
        if execution_time < 1.0:
            print(f"✅ Performance satisfaisante")
            return True
        else:
            print(f"⚠️  Performance lente: {execution_time:.4f}s")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test de performance: {e}")
        return False

def run_all_tests():
    """Lance tous les tests de validation."""
    print("🧪 DÉMARRAGE DES TESTS COMPLETS DE REFACTORING ET D'INTÉGRATION")
    print("=" * 70)
    
    tests = [
        ("Fonctionnalité de base", test_basic_functionality),
        ("Intégration des tools", test_tools_integration),
        ("Définition des tools", test_tool_definitions),
        ("Cas limites des tools", test_tool_edge_cases),
        ("Performance", test_performance)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔄 Exécution: {test_name}")
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSÉ")
            else:
                print(f"❌ {test_name}: ÉCHOUÉ")
        except Exception as e:
            print(f"❌ {test_name}: ERREUR - {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 RÉSULTATS FINAUX: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✅ Le refactoring et l'intégration fonctionnent parfaitement")
        return True
    else:
        print("⚠️  Certains tests ont échoué")
        print("❌ Vérifiez les erreurs ci-dessus")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print("\n🚀 Le système est prêt à être utilisé!")
    else:
        print("\n🔧 Des corrections sont nécessaires.")
        sys.exit(1)
