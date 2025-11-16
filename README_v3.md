

#####################
###################



# Arreter les services
make stop

# Test rapide (5 tests essentiels)
make test-movie

make test-user
OU
curl http://localhost:3201/health
curl http://localhost:3201/users/chris_rivers/is_admin
curl http://localhost:3201/chris_rivers/users/json

---------------

test schedule

Requête GraphQL pour récupérer tous les films :

```bash
curl -X POST http://localhost:3200/chris_rivers/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ all_movies { id title director rating } }"}'
```

Requête pour récupérer un film spécifique :

```bash
curl -X POST http://localhost:3200/chris_rivers/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ movie_by_id(id: \"a8034f44-aee4-44cf-b32c-74cf452aaaae\") { id title director rating } }"}'
```

----------------

# Test complet (toutes les fonctionnalités)
make test-movie-full

# Ouvrir l'interface graphique dans le navigateur
# Allez sur : http://localhost:3200/chris_rivers/graphql

Ici, vous pouvez interagir avec l'API GraphQL de manière visuelle.
Vous pouvez écrire des requêtes, explorer le schéma et voir les résultats en temps réel.

Vous verrez une interface interactive où vous pouvez taper vos requêtes GraphQL !
Tests avec curl (ligne de commande)
Récupérer tous les films :

```bash
curl -X POST http://localhost:3200/chris_rivers/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ all_movies { id title director rating } }"}'
```

Récupérer un film par ID :
```bash
curl -X POST http://localhost:3200/chris_rivers/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ movie_by_id(id: \"a8034f44-aee4-44cf-b32c-74cf452aaaae\") { id title director rating } }"}'
```

Récupérer un film par titre :
```bash
curl -X POST http://localhost:3200/chris_rivers/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ movie_by_title(title: \"The Martian\") { id title director rating } }"}'
```

Récupérer les films d'un réalisateur :
```bash
curl -X POST http://localhost:3200/chris_rivers/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ movies_by_director(director: \"Ridley Scott\") { id title director rating } }"}'
```

Ajouter un film (nécessite admin = chris_rivers) :
```bash
curl -X POST http://localhost:3200/chris_rivers/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { add_movie(title: \"Inception\", director: \"Christopher Nolan\", rating: 8.8) { id title director rating } }"
  }'
```

Essayer d'ajouter un film en tant que non-admin (doit échouer) :
```bash
curl -X POST http://localhost:3200/peter_curley/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { add_movie(title: \"Test Movie\", director: \"Test Director\", rating: 5.0) { id title director rating } }"
  }'
```

-------------

```bash
docker logs movie
```

Tout fonctionne correctement ! Les logs montrent que :

✅ MongoDB est connecté (✓ Connecté à MongoDB: movies_db)
✅ Les requêtes fonctionnent (codes 200)
✅ La sécurité admin fonctionne (peter_curley est bien bloqué pour add_movie)
✅ L'interface GraphiQL fonctionne

L'erreur "Accès refusé" pour peter_curley est normale et attendue ! C'est exactement ce qu'on veut : seuls les admins peuvent ajouter des films.


----------

# Afficher l'aide
make help

# Lancer avec Docker + MongoDB (la config que vous voulez)
make docker-mongo

Pour chaque service :

User (user/config.py) :

MONGO_DB_NAME = 'users_db'
Pas besoin de USER_BASE_URL (c'est lui le service User)


Movie (movie/config.py) :

MONGO_DB_NAME = 'movies_db'
Besoin de USER_BASE_URL pour vérifier les admins


Booking (booking/config.py) :

MONGO_DB_NAME = 'bookings_db'
Besoin de USER_BASE_URL et MOVIE_BASE_URL


Schedule (schedule/config.py) :

MONGO_DB_NAME = 'schedules_db'
Besoin de USER_BASE_URL et MOVIE_BASE_URL



Avantages de cette structure :

✅ Séparation claire des responsabilités
✅ Facile de switcher entre JSON et MongoDB
✅ Code testable (on peut mocker les repositories)
✅ Respect du principe SOLID (Open/Closed)
✅ Pas de duplication de code entre les implémentations

-----------

Exemple de requêtes dans GraphiQL
Une fois sur http://localhost:3200/chris_rivers/graphql, essayez ces requêtes :
Query simple pour récupérer tous les films :
```graphql
{
    all_movies {
        id
        title
        director
        rating
    }
}
```

Mutation : 
```graphql
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

Désormais, vous refaites la query simple pour voir le nouveau film ajouté !
