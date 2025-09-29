#!/bin/bash

# Script de préparation pour le déploiement Render
# Usage: ./prepare_for_render.sh

echo "🚀 Préparation du projet Twitter Scraper pour Render"
echo "===================================================="

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "app.py" ]; then
    echo "❌ Erreur: app.py non trouvé. Assurez-vous d'être dans le bon répertoire."
    exit 1
fi

echo "📋 Vérification des fichiers requis pour Render..."

# Vérifier les fichiers critiques
files=("app.py" "Procfile" "requirements.txt" "runtime.txt")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file manquant"
        exit 1
    fi
done

# Vérifier le répertoire templates
if [ -d "templates" ]; then
    echo "✅ templates/"
else
    echo "❌ répertoire templates/ manquant"
    exit 1
fi

echo ""
echo "🔧 Test rapide de l'application..."

# Test d'import Python
python3 -c "import app; print('✅ Application Flask OK')" || {
    echo "❌ Erreur d'import de l'application"
    exit 1
}

echo ""
echo "📦 Ajout des fichiers au Git..."

# Ajouter tous les fichiers
git add .

echo ""
echo "📝 Création du commit..."

# Créer le commit
git commit -m "feat: Add Flask web app for Render deployment

- Add Flask web application (app.py) with REST API
- Add web interface (templates/index.html) 
- Add Render configuration (Procfile, runtime.txt)
- Update requirements.txt with Flask dependencies
- Add deployment documentation and test scripts
- Ready for Render deployment"

echo ""
echo "🎯 Statut Git après préparation:"
git status --short

echo ""
echo "✅ PROJET PRÊT POUR RENDER !"
echo "============================"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Pousser vers GitHub:     git push origin $(git branch --show-current)"
echo "2. Aller sur render.com"
echo "3. Créer un nouveau 'Web Service'"  
echo "4. Connecter votre repository GitHub"
echo "5. Configurer au minimum: OPENROUTER_API_KEY"
echo "6. Cliquer sur 'Create Web Service'"
echo ""
echo "🌐 Votre app sera disponible à l'URL fournie par Render"
echo "📖 Voir DEPLOY_TO_RENDER.md pour le guide détaillé"
