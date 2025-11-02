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
- Le fichier `requirements.txt` à jour

---

## Utilisation avec Docker

### Gestion du microservice Movie

Commencez par construire l'image :
```bash
docker build -t movie-app -f movie/Dockerfile .
```

Ensuite, vous pouvez lancer le microservice avec le fichier JSON local :
```bash
docker run --rm -it -p 3200:3200 movie-app
```

Désormais, le contenur pour le microservice Movie est prêt à être utilisé. Vous pouvez tester l'url de base avec :
```code
http://localhost:3200
```


### Gestion du microservice Booking

Commencez par construire l'image :
```bash
docker build -t booking-app -f booking/Dockerfile .
```

Ensuite, vous pouvez lancer le microservice avec le fichier JSON local :
```bash
docker run --rm -it -p 3203:3203 booking-app
```

Désormais, le contenur pour le microservice Booking est prêt à être utilisé. Vous pouvez tester l'url de base avec :
```code
http://localhost:3203
```


### Gestion du microservice User

Commencez par construire l'image :
```bash
docker build -t user-app -f user/Dockerfile .
```

Ensuite, vous pouvez lancer le microservice avec le fichier JSON local :
```bash
docker run --rm -it -p 3201:3201 user-app
```

Désormais, le contenur pour le microservice User est prêt à être utilisé. Vous pouvez tester l'url de base avec :
```code
http://localhost:3201
```

Si vous voulez tester une url non-autorisé en tant que non-admin, vous pouvez utiliser l'url suivante :
```code
http://localhost:3201/peter_curley/users/json
```

ou une en tant qu'admin :
```code
http://localhost:3201/chris_rivers/users/json
```

---



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