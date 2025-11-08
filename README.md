# UE-AD-A1-MIXTE

## Nos choix techniques

Nous avons mis en place un système **admin/user** dans notre architecture microservices de manière à la fois
**maintenable**, **performante** et **simple à étendre**.

### Architecture et gestion des accès

- Toutes les routes (endpoints) de chaque microservice commencent par `/<user_id>/...`
- Chaque route vérifie si l’utilisateur est admin en interrogeant le microservice **User** via : `/users/<user_id>/is_admin`
- Un **cache mémoire** (`user_admin_cache`) permet de limiter les appels au microservice User :
    - Le cache contient un booléen `is_admin` avec un timestamp.
    - Si la donnée est trop ancienne (selon la variable `CACHE_TTL`, fixée à 60 secondes), elle est rechargée depuis le microservice `User`.
- Certains endpoints nécessitent le statut **admin** (ajout, suppression, etc.) :  
  si l’utilisateur n’est pas admin, on retourne une réponse `403 Forbidden`.

---

## Rôles des microservices

| Microservice | Type | Rôle principal |
|-------------|------|----------------|
| **User** | REST | Gestion des utilisateurs, vérification des droits admin et gestion de l’authentification. |
| **Movie** | GraphQL | Gestion des films : création, lecture, mise à jour et suppression des informations de films. |
| **Booking** | GraphQL | Gestion des réservations : création, consultation et suppression de réservations. |
| **Schedule** | gRPC | Planification des séances : récupère les films et vérifie les droits admin via User, expose les horaires disponibles. |

---


## Lancement des microservices avec Docker

> **Important** : le microservice `User` doit toujours être lancé, car il est utilisé par tous les autres pour la gestion admin/user.


### Prérequis

Avant toute chose, assurez-vous d’avoir :
- **Docker** installé et en fonctionnement
- **Python 3.10+** installé (pour les exécutions locales)
- Le fichier `requirements.txt` à jour


### Création d’un réseau Docker commun

Pour que les microservices puissent communiquer entre eux via leurs noms de conteneur :
```bash
docker network create movie-net
```


### Lancement des conteneurs avec noms fixes

#### Microservice User

```bash
docker build -t user-app -f user/Dockerfile .
docker run --rm -it --name user --network movie-net -p 3201:3201 user-app
```

- URL de base : http://user:3201
- Exemples d’accès :
  - Non-admin : http://user:3201/peter_curley/users/json
  - Admin : http://user:3201/chris_rivers/users/json

#### Microservice Movie

```bash
docker build -t movie-app -f movie/Dockerfile .
docker run --rm -it --name movie --network movie-net -p 3200:3200 movie-app
```

- URL de base : http://booking:3203

#### Microservice Schedule (gRPC)

```bash
docker build -t schedule-app -f schedule/Dockerfile .
docker run --rm -it --name schedule --network movie-net -p 3202:3202 schedule-app
```

- Schedule communique avec :
  - User : http://user:3201
  - Movie : http://movie:3200
- Écoute sur le port 3202 en mode gRPC, ne renvoie rien tant qu’aucun client ne se connecte.


### Tests gRPC Schedule

Installer l’outil :
```bash
brew install grpcurl
```

Exemple de test sans films :
```bash
grpcurl -plaintext \
  -import-path schedule/protos \
  -proto schedule.proto \
  -d '{"userId":"chris_rivers","date":"20251001"}' \
  localhost:3202 Schedule/GetMoviesByDate
```

Exemple de test pour une date précise :
```bash
grpcurl -plaintext \
  -import-path schedule/protos \
  -proto schedule.proto \
  -d '{"userId":"chris_rivers","date":"20151201"}' \
  localhost:3202 Schedule/GetMoviesByDate
```


## Documentation OpenAPI

Les fichiers OpenAPI (format .yaml) se trouvent dans les dossiers des microservices correspondants.

Exemple : pour le microservice Booking :
- `booking/booking.yaml`


## Tests via Insomnia

Pour tester l’application, importez le fichier suivant dans Insomnia :
`Insomnia.yaml` (disponible à la racine du projet)

---

BOURREAU Quentin / KOWALSKI Damien - FIL A1