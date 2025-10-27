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

## Lancement des microservices

> **Important** : le microservice `User` doit toujours être lancé, car il est utilisé par tous les autres pour la gestion admin/user.

### Prérequis

Avant toute chose, assurez-vous d’avoir :
- **Docker** installé et en fonctionnement
- **Python 3.10+** installé (pour les exécutions locales)
- Le fichier `requirements.txt` à jour dans chaque microservice

---

## Utilisation avec Docker

### Construire les images

```bash
docker build -t user -f user/Dockerfile .
docker build -t schedule -f schedule/Dockerfile .
```

### Lancer les microservices avec les fichiers JSON locaux

Microservice `User`

```bash
docker run --rm -p 3201:3201 \
  -v "$(pwd)/user/databases:/app/databases" \
  -e USE_DOCKER=1 \
  user
```

Microservice `Schedule`

```bash
docker run --rm -p 3202:3202 \
  -v "$(pwd)/schedule/databases:/app/databases" \
  -e USE_DOCKER=1 \
  schedule
```

### Options utiles

Exécuter en arrière-plan :
Ajoutez `-d` après `docker run`

Monter un fichier particulier :

```bash
-v "$(pwd)/user/databases/users.json:/app/databases/users.json"
```

## Exécution locale (sans Docker)

Microservice `User`

```bash
cd user
pip install -r requirements.txt
USE_DOCKER=0 python user.py
```

Microservice `Schedule`

```bash
cd schedule
pip install -r requirements.txt
USE_DOCKER=0 python schedule.py
```

## Documentation OpenAPI

Les fichiers OpenAPI (format .yaml) se trouvent dans les dossiers des microservices correspondants.
Exemple : pour le microservice Booking, ouvrez :

```bash
booking/booking.yaml
```

## Tests via Insomnia

Pour tester l’application, importez le fichier suivant dans Insomnia :
`Insomnia.yaml`

(disponible à la racine du projet)

---

BOURREAU Quentin / KOWALSKI Damien - FIL A1






reste a faire : 
- tester schedule
- faire dockefile pour les 2 autre microservices
- faire readme a jour (+ voir pour partie utiles)
- compléter docker-compose pour simplifier le lancement des 4 microservices + expliquer dans le readme