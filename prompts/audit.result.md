# Audit raph

## 1) Vue d'ensemble

### But du projet

Le dépôt implémente plusieurs algorithmes de recommandation musicale (user-based, item-based, hybride) autour d'une base PostgreSQL locale.  
Références: [README.md](../README.md), [test.py](../test.py).

### Problème résolu

Produire des recommandations de morceaux à partir de:

- profil utilisateur,
- favoris utilisateur,
- similarité audio/metadata des morceaux,
- combinaison hybride user/item.

### Utilisateurs cibles

Principalement des développeurs/étudiants qui testent les approches via CLI locale (pas d'API/web app).  
Référence: [test.py](../test.py#L22).

### Maturité apparente

Prototype académique / POC:

- scripts orientés expérimentation,
- forte dépendance à une DB locale spécifique,
- pas d'industrialisation (CI/CD, tests automatiques, packaging).  
Références: [README.md](../README.md), [requirements.txt](../requirements.txt).

## 2) Architecture

### Style global

Architecture script-based monolithique (pas de microservices, pas de couches strictes), avec modules Python spécialisés par algorithme.

### Modules principaux

- Chargement DB/data: [load.py](../load.py)
- Fonctions math/similarité partagées: [basicsfunctions.py](../basicsfunctions.py)
- User-based profil: [reco_user_based_p1.py](../reco_user_based_p1.py)
- User-based favoris: [reco_user_based_p2.py](../reco_user_based_p2.py)
- User-based scoring écoute: [reco_user_based_p3.py](../reco_user_based_p3.py)
- Item-based Echonest: [reco_steph_echonest.py](../reco_steph_echonest.py)
- Item-based artiste/album: [reco_item_based_matheo.py](../reco_item_based_matheo.py)
- Item-based popularité+genres: [reco_item_based_mathieu.py](../reco_item_based_mathieu.py)
- Hybride: [hybride.py](../hybride.py)
- Orchestrateur CLI de démo: [test.py](../test.py)

### Dépendances internes / flux

`test.py` appelle directement chaque module de reco.  
`hybride.py` appelle `reco_user_based_p2` + `reco_steph_echonest`.  
Plusieurs modules chargent les données au niveau global (import-time), donc effets de bord immédiats.

### Points d'entrée

- Principal: `python test.py` (menu interactif)  
  Réf: [test.py](../test.py#L363)
- Scripts secondaires avec code de test embarqué (parfois non protégé par `if __name__ == "__main__"`), ex. [reco_steph_echonest.py](../reco_steph_echonest.py#L167), [hybride.py](../hybride.py#L91), [popu_ecoute.py](../popu_ecoute.py).

## 3) Technologies et dépendances

### Langage

- Python

### Librairies clés

- `psycopg2-binary` (PostgreSQL)
- `pandas`, `numpy` (data processing)
- `scikit-learn` (cosine similarity, scaling, binarization)
- `pycountry` (mapping code langue)  
Réf: [requirements.txt](../requirements.txt), [load.py](../load.py#L1).

### Outils de build / dépendances

- Pas de `pyproject.toml`, pas de setup packaging.
- Dépendances via `requirements.txt`.

### Services externes

- PostgreSQL local (`localhost:25000`) avec credentials codés en dur dans plusieurs fichiers.  
Réf: [load.py](../load.py#L5), [test.py](../test.py#L13).

## 4) Flux applicatifs

### Flux principal (CLI)

1. L'utilisateur choisit un algorithme dans le menu.
2. Le script récupère données user/tracks depuis PostgreSQL.
3. Il exécute l'algo ciblé (profil, favoris, item-based, hybride).
4. Il affiche des recommandations textuelles.  
Réf: [test.py](../test.py#L22).

### Authentification / autorisation / état

- Pas d'authentification applicative.
- Pas de gestion de session/état persisté applicatif.
- Seule "contrainte" métier: filtrage du contenu explicite via `explicit_ok` pour certaines recos.  
Réf: [reco_steph_echonest.py](../reco_steph_echonest.py#L83), [reco_user_based_p1.py](../reco_user_based_p1.py#L302).

## 5) Données

### Type de base

- PostgreSQL relationnelle.

### Entités/tables observées (via SQL du code)

`user`, `user_profile`, `track`, `track_echonest`, `artist`, `album`, `realiser`, `genre`, `contient_genres`, `ajoute_favori`, `user_ecoute`, `user_prefere_artiste`, `user_ajoute_album_favoris`, `user_parle`, `language`, etc.  
Réf: [load.py](../load.py), [reco_user_based_p1.py](../reco_user_based_p1.py), [reco_user_based_p2.py](../reco_user_based_p2.py).

### Transformations

- Normalisations/scaling (`MinMaxScaler`, `StandardScaler`)
- Encodage multi-label (`MultiLabelBinarizer`)
- Agrégations genres/langues et enrichissement DataFrames.  
Réf: [reco_steph_echonest.py](../reco_steph_echonest.py#L20), [reco_item_based_mathieu.py](../reco_item_based_mathieu.py#L27), [load.py](../load.py#L73).

### Migrations

- Aucune migration/versioning de schéma trouvée.

### Données locales

- CSV de démonstration: [musiques_user.csv](../musiques_user.csv).

## 6) DevOps et pipelines

- Aucun pipeline CI/CD détecté (pas de `.github/workflows`, GitLab CI, Jenkinsfile).
- Aucun Dockerfile / docker-compose.
- Pas de scripts de déploiement.
- Pas de gestion propre des variables d'environnement: credentials DB en dur.  
Réfs: [load.py](../load.py#L5), [requirements.txt](../requirements.txt).

## 7) Qualité et maintenabilité

### Points positifs

- Séparation par approche algorithmique.
- Fonctions utilitaires partagées pour similarité.
- CLI unique pour démontrer les variantes.

### Points fragiles importants

- `requirements.txt` contient des marqueurs de conflit Git non résolus (`<<<<<<<`, `>>>>>>>`).  
  Réf: [requirements.txt](../requirements.txt#L5)
- Erreur SQL probable: `user_parle langue` (table/alias invalide).  
  Réf: [reco_user_based_p2.py](../reco_user_based_p2.py#L38)
- `test.py` utilise `reco_item_based_mathieu.m` et `.indices` qui ne sont pas définis hors bloc commenté.  
  Réf: [test.py](../test.py#L278), [reco_item_based_mathieu.py](../reco_item_based_mathieu.py#L104)
- Effets de bord à l'import (exécution automatique de tests/requêtes) dans certains modules.
  Réf: [reco_steph_echonest.py](../reco_steph_echonest.py#L167), [hybride.py](../hybride.py#L93), [popu_ecoute.py](../popu_ecoute.py#L6)
- Credentials DB hardcodés et répétés.
- Fermeture de connexion incomplète dans certains chemins (ex: retour anticipé avec `get_title=True` dans p2).  
  Réf: [reco_user_based_p2.py](../reco_user_based_p2.py#L191)

### Tests

- Aucun test unitaire/intégration/e2e formel.
- `test.py` est une interface manuelle, pas une suite automatisée.

### Logging / erreurs

- Gestion majoritairement via `print` + `try/except` large.
- Peu de remontée structurée d'erreurs.

## 8) Documentation

- README présent mais très court, orienté contexte SAE, sans procédure d'installation/exécution complète.  
  Réf: [README.md](../README.md)
- Pas de documentation d'architecture, ni schéma DB, ni runbook.
- Commentaires présents dans le code, plutôt pédagogiques.
- Dossier `DEPRECATED` explicite une ancienne logique de peuplement: [DEPRECATED/peuplement_fav_user.py](../DEPRECATED/peuplement_fav_user.py).

## 9) Synthèse finale

### Ce que fait réellement le projet

Un banc d'essai local de systèmes de recommandation musicale multi-approches, branché sur une base PostgreSQL métier existante.

### Complexité globale

Complexité fonctionnelle moyenne (plusieurs algorithmes, flux DB variés), mais complexité d'infrastructure faible (tout en scripts locaux).

### Forces principales

- Diversité d'approches de recommandation.
- Découpage fonctionnel compréhensible par algorithme.
- Bonne base d'expérimentation académique.

### Faiblesses principales

- Fiabilité d'exécution limitée (bugs évidents, conflits non résolus).
- Absence d'automatisation qualité (tests/CI).
- Couplage fort à une DB locale non décrite.
- Sécurité/configuration non industrialisées (secrets en clair).

### Évaluation globale

Qualité globale: **prototype académique utile pour exploration**, mais **non prêt production** en l'état.  
Pour un nouvel ingénieur, le démarrage passe d'abord par: stabiliser l'exécution (bugs bloquants), formaliser la configuration DB, puis ajouter tests et documentation de schéma/flux.
