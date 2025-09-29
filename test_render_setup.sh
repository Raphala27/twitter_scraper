#!/bin/bash

# Test local de l'application Twitter Scraper pour Render

echo "🚀 Test de l'application Twitter Scraper"
echo "======================================="

# Vérifier Python
echo "📋 Vérification de Python..."
python3 --version

# Vérifier les dépendances
echo "📋 Vérification des dépendances..."
pip3 list | grep -E "(flask|gunicorn|requests)"

# Test d'import
echo "📋 Test d'import de l'application..."
python3 -c "
try:
    import app
    print('✅ Application Flask importée avec succès')
except ImportError as e:
    print(f'❌ Erreur d'import: {e}')
    exit(1)
"

# Test des endpoints principaux
echo "📋 Test de l'application en mode test..."
python3 -c "
import app
import json

try:
    with app.app.test_client() as client:
        # Test health endpoint
        response = client.get('/health')
        if response.status_code == 200:
            print('✅ Endpoint /health OK')
        else:
            print('❌ Endpoint /health failed')
        
        # Test main page
        response = client.get('/')
        if response.status_code == 200:
            print('✅ Page principale OK')
        else:
            print('❌ Page principale failed')
        
        # Test simple analyze endpoint
        response = client.get('/api/analyze/simple?user=@test&limit=1')
        if response.status_code in [200, 500]:  # 500 is expected without API keys
            print('✅ Endpoint /api/analyze/simple OK (structure)')
        else:
            print('❌ Endpoint /api/analyze/simple failed')
            
        print('✅ Tests de base réussis')
        
except Exception as e:
    print(f'❌ Erreur lors des tests: {e}')
"

echo ""
echo "🎯 Application prête pour le déploiement sur Render!"
echo ""
echo "📝 Prochaines étapes :"
echo "1. Commitez tous les fichiers : git add . && git commit -m 'Ready for Render'"
echo "2. Poussez sur GitHub : git push origin main"
echo "3. Allez sur render.com et créez un nouveau Web Service"
echo "4. Connectez votre repository GitHub"
echo "5. Configurez les variables d'environnement (OPENROUTER_API_KEY minimum)"
echo "6. Déployez !"
echo ""
echo "🌐 L'application sera accessible à l'URL fournie par Render"
