# UE-AD-A1-MIXTE - Système de Microservices

## Vue d'ensemble

Architecture microservices pour la gestion d'un système de réservation de films, composée de 4 services communicants :

| Service | Type | Port | Rôle |
|---------|------|------|------|
| **User** | REST | 3201 | Gestion des utilisateurs et vérification des droits admin |
| **Movie** | GraphQL | 3200 | Gestion du catalogue de films |
| **Booking** | GraphQL | 3203 | Gestion des réservations |
| **Schedule** | gRPC | 3202 | Planification des séances |

## Architecture et sécurité

### Système Admin/User

- Toutes les routes commencent par `/<user_id>/...`
- Vérification automatique des droits admin via le service User : `/users/<user_id>/is_admin`
- **Cache mémoire** avec TTL de 60 secondes pour optimiser les performances
- Certaines opérations (ajout, suppression) nécessitent les droits admin → réponse `403 Forbidden` si non autorisé

### Stockage des données

Le système supporte deux modes de stockage :
- **MongoDB** (recommandé) : Stockage persistant dans des bases séparées
- **JSON** : Fichiers locaux pour le développement

## Démarrage rapide

### Prérequis

- Docker et Docker Compose
- Python 3.10+ (pour exécution locale)
- grpcurl (pour tester le service Schedule)

### Lancement avec Docker + MongoDB (Recommandé)

```bash
make docker-mongo
```

Cette commande :
- Configure automatiquement l'environnement
- Lance tous les services avec Docker Compose
- Initialise MongoDB avec les données de base
- Attend que tous les services soient prêts

**URLs d'accès :**
- User : http://localhost:3201
- Movie : http://localhost:3200 (interface GraphiQL disponible)
- Booking : http://localhost:3203 (interface GraphiQL disponible)
- Schedule : localhost:3202 (serveur gRPC)

### Autres options de lancement

```bash
# Docker + JSON
make docker-json

# Local + MongoDB
make local-mongo

# Local + JSON
make local-json
```

## Tests

### Tests rapides

```bash
# Tester chaque service individuellement
make test-user
make test-movie
make test-booking
make test-schedule

# Tester tous les services
make test-all
```

### Exemples de requêtes

#### User (REST)

```bash
# Health check
curl http://localhost:3201/health

# Vérifier si un utilisateur est admin
curl http://localhost:3201/users/chris_rivers/is_admin

# Récupérer tous les utilisateurs (admin uniquement)
curl http://localhost:3201/chris_rivers/users/json
```

#### Movie (GraphQL)

**Interface interactive :** http://localhost:3200/chris_rivers/graphql

```bash
# Récupérer tous les films
curl -X POST http://localhost:3200/chris_rivers/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ all_movies { id title director rating } }"}'

# Récupérer un film par titre
curl -X POST http://localhost:3200/chris_rivers/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ movie_by_title(title: \"The Martian\") { id title director rating } }"}'

# Ajouter un film (admin uniquement)
curl -X POST http://localhost:3200/chris_rivers/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { add_movie(title: \"Inception\", director: \"Christopher Nolan\", rating: 8.8) { id title director rating } }"}'
```

**Exemples GraphiQL :**

```graphql
# Query simple
{
  all_movies {
    id
    title
    director
    rating
  }
}

# Mutation
mutation {
  add_movie(
    title: "Dune"
    director: "Denis Villeneuve"
    rating: 8.0
  ) {
    id
    title
    director
    rating
  }
}
```

#### Booking (GraphQL)

**Interface interactive :** http://localhost:3203/chris_rivers/graphql

```bash
# Récupérer les réservations d'un utilisateur
curl -X POST http://localhost:3203/chris_rivers/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ booking_with_id(user_id: \"chris_rivers\", id: \"chris_rivers\") { userid { id name } dates { date movies { title } } } }"}'
```

#### Schedule (gRPC)

```bash
# Installation de grpcurl (macOS)
brew install grpcurl

# Récupérer toutes les séances
grpcurl -plaintext \
  -import-path schedule/protos \
  -proto schedule.proto \
  -d '{"userId":"chris_rivers"}' \
  localhost:3202 Schedule/GetJson

# Récupérer les films pour une date
grpcurl -plaintext \
  -import-path schedule/protos \
  -proto schedule.proto \
  -d '{"userId":"chris_rivers","date":"20151201"}' \
  localhost:3202 Schedule/GetMoviesByDate

# Ajouter une séance (admin uniquement)
grpcurl -plaintext \
  -import-path schedule/protos \
  -proto schedule.proto \
  -d '{"userId":"chris_rivers","date":"20251215","moviesId":["a8034f44-aee4-44cf-b32c-74cf452aaaae"]}' \
  localhost:3202 Schedule/AddSchedule
```

## Gestion des services

### Logs

```bash
# Tous les services
make logs

# Service spécifique
make logs-movie
make logs-user
make logs-booking
make logs-schedule
make logs-mongodb
```

### Arrêt et nettoyage

```bash
# Arrêter les services
make stop

# Nettoyage complet (conteneurs, volumes, cache)
make clean
```

## MongoDB

### Vérification des données

```bash
# Vérifier rapidement toutes les bases
make mongo-check

# Ouvrir le shell MongoDB
make mongo-shell
```

**Commandes utiles dans le shell :**
```javascript
show dbs                    // Liste les bases
use movies_db               // Sélectionne une base
show collections            // Liste les collections
db.movies.find().pretty()   // Affiche les films
exit                        // Quitter
```

## Documentation

### Fichiers OpenAPI

Les spécifications API se trouvent dans les dossiers respectifs :
- `user/user.yaml`
- `movie/movie.yaml`
- `booking/booking.yaml`
- `schedule/protos/schedule.proto` (gRPC)

### Tests avec Insomnia

Un fichier de configuration Insomnia est disponible à la racine : `Insomnia.yaml`

**Import :**
1. Ouvrir Insomnia
2. Menu **Import/Export** → **Import Data**
3. Sélectionner `Insomnia.yaml`
4. Tous les endpoints sont automatiquement configurés

## Commandes Makefile

```bash
make help              # Affiche toutes les commandes disponibles

# Lancement
make docker-mongo      # Docker + MongoDB (recommandé)
make docker-json       # Docker + JSON
make local-mongo       # Local + MongoDB
make local-json        # Local + JSON

# Tests
make test-user         # Teste User (REST)
make test-movie        # Teste Movie (GraphQL)
make test-booking      # Teste Booking (GraphQL)
make test-schedule     # Teste Schedule (gRPC)
make test-all          # Teste tous les services

# Gestion
make stop              # Arrête les conteneurs
make clean             # Nettoyage complet
make logs              # Logs en temps réel

# MongoDB
make mongo-shell       # Ouvre le shell MongoDB
make mongo-check       # Vérifie les données
```

## Dépannage

### Les conteneurs ne démarrent pas

Vérifier que les ports ne sont pas déjà utilisés :
```bash
lsof -i :3200
lsof -i :3201
lsof -i :3202
lsof -i :3203
```

### MongoDB ne démarre pas

Vérifier les logs :
```bash
make logs-mongodb
```

Nettoyage complet et redémarrage :
```bash
make clean
make docker-mongo
```

## Utilisateurs de test

| Utilisateur | ID | Admin |
|-------------|-------|-------|
| Chris Rivers | chris_rivers | ✅ Oui |
| Peter Curley | peter_curley | ❌ Non |

## Auteurs

**BOURREAU Quentin / KOWALSKI Damien** - FIL A1