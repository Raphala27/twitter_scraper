# Twitter Scraper Web App

## Déploiement sur Render

Ce projet est configuré pour être déployé sur [Render](https://render.com).

### Étapes de déploiement :

1. **Préparer le repository Git**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Créer un nouveau service sur Render**
   - Aller sur [render.com](https://render.com)
   - Se connecter et créer un nouveau "Web Service"
   - Connecter votre repository GitHub
   - Sélectionner la branche `main` (ou votre branche actuelle)

3. **Configuration du service**
   - **Name**: `twitter-scraper-ai`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Pricing**: Choisir le plan gratuit ou payant selon vos besoins

4. **Variables d'environnement**
   Dans les settings du service Render, ajouter les variables suivantes :
   ```
   OPENROUTER_API_KEY=votre_clé_openrouter
   COINGECKO_API_KEY=votre_clé_coingecko (optionnel)
   COINCAP_API_KEY=votre_clé_coincap (optionnel)
   TWITSCOUT_API_KEY=votre_clé_twitscout (optionnel)
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

5. **Déployer**
   - Cliquer sur "Create Web Service"
   - Render va automatiquement construire et déployer votre application
   - L'URL de votre application sera fournie une fois le déploiement terminé

### Structure des fichiers pour Render

Les fichiers suivants ont été créés/modifiés pour Render :

- `app.py` - Application Flask web
- `Procfile` - Commande de démarrage pour Render
- `runtime.txt` - Version de Python
- `requirements.txt` - Dépendances Python (mise à jour avec Flask)
- `templates/index.html` - Interface web
- `.env.example` - Variables d'environnement exemple

### Fonctionnalités web

L'application web offre :

- **Interface utilisateur** : Interface web simple pour tester l'analyse
- **API REST** : Endpoints pour intégration avec d'autres services
  - `GET /` - Interface web
  - `GET /health` - Health check
  - `POST /api/analyze` - Analyse complète
  - `GET /api/analyze/simple` - Test rapide
  - `GET /api/models` - Liste des modèles disponibles

### Mode démo

L'application fonctionne en mode démo même sans clés API :
- Mock data pour les tweets
- Mock data pour les prix crypto
- Analyse IA avec OpenRouter (clé requise)

### Tests locaux

Pour tester localement avant déploiement :

```bash
# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API

# Lancer l'application
python app.py
```

L'application sera disponible sur `http://localhost:5000`

### Troubleshooting

1. **Erreur de build** : Vérifier que `requirements.txt` est correct
2. **Erreur de démarrage** : Vérifier que `Procfile` et `app.py` sont présents
3. **Erreur d'API** : Vérifier les variables d'environnement dans Render
4. **Port issues** : Render définit automatiquement la variable PORT

### Monitoring

Une fois déployé, vous pouvez :
- Voir les logs en temps réel dans le dashboard Render
- Monitorer la performance de l'application
- Configurer des alertes et notifications

L'URL finale ressemblera à : `https://your-app-name.onrender.com`
