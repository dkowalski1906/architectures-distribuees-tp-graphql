import time
from flask import Flask, render_template, request, jsonify, make_response
import json, requests
from werkzeug.exceptions import NotFound
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

PORT = 3202
HOST = '0.0.0.0'
MOVIE_URL   = "http://localhost:3200" # microservice Movie
USER_URL  = "http://localhost:3201" # microservice User

CACHE_TTL = 60 # secondes de validité du cache pour is_admin

# cache local pour stocker si un user est admin
# format : { "user_id": {"is_admin": True/False, "timestamp": 123456789} }
user_admin_cache = {}

# charge le fichier JSON contenant le planning
with open('{}/databases/times.json'.format("."), "r") as jsf:
    schedule = json.load(jsf)["schedule"]

# sauvegarde le planning dans le fichier
def write(times):
    with open('{}/databases/times.json'.format("."), 'w') as f:
        full = {}
        full['schedule']=times
        json.dump(full, f)

# fonction utilitaire pour vérifier admin
def verify_admin(user_id):
    """
    Check if a user is an admin, with caching.

    Args:
        user_id (str): ID of the user to check.

    Returns:
        tuple: (is_admin (bool), error_response (Response or None))
               is_admin indicates if the user has admin privileges.
               error_response is a Flask response object if verification fails.
    """
    now = time.time()

    # vérifie si on a une valeur en cache et qu'elle est encore valide
    if user_id in user_admin_cache:
        cached = user_admin_cache[user_id]
        if now - cached["timestamp"] < CACHE_TTL:
            return cached["is_admin"], None

    # sinon appelle le microservice User
    try:
        r = requests.get(f"{USER_URL}/users/{user_id}/is_admin")
        if r.status_code == 200:
            data = r.json()
            is_admin = data.get("is_admin", False)
            user_admin_cache[user_id] = {"is_admin": is_admin, "timestamp": now}
            return is_admin, None
        else:
            return False, make_response(jsonify({"error": "Unable to verify user"}), 401)
    except requests.exceptions.RequestException:
        return False, make_response(jsonify({"error": "User service unreachable"}), 503)


# page d’accueil du service
@app.route("/", methods=['GET'])
def home():
   """
    Home endpoint
    ---
    responses:
      200:
        description: Welcome message
    """
   return "<h1 style='color:blue'>Welcome to the Schedule service!</h1>"

# retourne tout le planning en JSON brut
@app.route("/<user_id>/schedule/json", methods=['GET'])
def get_json(user_id):
    """
    Get the full schedule in raw JSON format.

    Args:
        user_id (str): ID of the requesting user.

    Returns:
        Response: JSON response with the full schedule if the user is an admin,
                  otherwise an error response.
    """
    _, error = verify_admin(user_id)
    if error:
        return error

    res = make_response(jsonify(schedule), 200)
    return res

# récupère les films programmés pour une date précise
@app.route("/<user_id>/schedule/<date>", methods=['GET'])
def get_movies_by_date(user_id, date):
    """
    Get scheduled movies for a specific date.

    Args:
        user_id (str): ID of the requesting user.
        date (str): Date to retrieve movies for.

    Returns:
        Response: JSON response with the list of movie IDs for the given date,
                  or an error if no movies are found.
    """
    _, error = verify_admin(user_id)
    if error:
        return error

    for movies_date in schedule:
        if str(movies_date["date"]) == str(date):
            res = make_response(jsonify(movies_date["movies"]),200) # renvoi tous les movies direct suivant la date
            return res
    return make_response(jsonify({"error":"No movies found with this date"}),500)

# récupère les films programmés pour une date avec leurs détails
@app.route("/<user_id>/schedule/<date>/details", methods=['GET'])
def get_movies_by_date_details(user_id, date):
    """
    Get scheduled movies with details for a specific date.

    Args:
        user_id (str): ID of the requesting user.
        date (str): Date to retrieve movie details for.

    Returns:
        Response: JSON response with movie details (from the Movie microservice),
                  or an error if the date is not found.
    """
    _, error = verify_admin(user_id)
    if error:
        return error

    for movies_date in schedule:
        if str(movies_date["date"]) == str(date):
            movies_detail = []
            for movie_id in movies_date["movies"]:
                try:
                    r = requests.get(f"{MOVIE_URL}/{user_id}/movies/{movie_id}")
                    if r.status_code == 200:
                        movies_detail.append(r.json())
                    else:
                        movies_detail.append({"id": movie_id, "error": "movie not found"})
                except requests.exceptions.RequestException:
                    movies_detail.append({"id": movie_id, "error": "movie service unreachable"})

            return make_response(jsonify({
                "date": date,
                "movies": movies_detail
            }), 200)

    return make_response(jsonify({"error": "date not found"}), 404)

# récupère toutes les dates où un film est projeté (via son ID en query param)
@app.route("/<user_id>/schedule/by_movie", methods=['GET'])
def get_schedule_by_movie_id(user_id):
    """
    Get all dates when a specific movie is scheduled.

    Args:
        user_id (str): ID of the requesting user.

    Query Parameters:
        id (str): The movie ID to search for.

    Returns:
        Response: JSON response with all dates the movie is scheduled,
                  or an error if not found.
    """
    _, error = verify_admin(user_id)
    if error:
        return error

    movie_id = request.args.get("id") # récupère ?id=xxxx
    
    if not movie_id:
        return make_response(jsonify({"error": "missing 'id' parameter"}), 400)

    # récupère toutes les dates où ce film apparaît
    dates = [movies_date["date"] for movies_date in schedule if movie_id in movies_date["movies"]]

    if not dates:
        return make_response(jsonify({"error": "no schedule found for this movie id"}), 404)

    return make_response(jsonify({
        "movie_id": movie_id,
        "dates": dates
    }), 200)

# ajoute une nouvelle date (échoue si la date existe déjà)
@app.route("/<user_id>/schedule/<date_id>", methods=['POST'])
def add_date_schedule(user_id, date_id):
    """
    Add a new schedule entry for a given date.

    Args:
        user_id (str): ID of the requesting user.
        date_id (str): Date to create a schedule for.

    Request Body:
        {
            "movies": [list of movie IDs] (optional)
        }

    Returns:
        Response: JSON message indicating success or error if date already exists.
    """
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    # si pas admin -> accès interdit
    if not is_admin:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    req = request.get_json()

    # vérifie si la date existe déjà
    for movies_date in schedule:
        if str(movies_date["date"]) == str(date_id):
            return make_response(jsonify({"error": "schedule date already exists"}), 500)

    # ajoute la nouvelle entrée (soit avec données du body, soit vide avec seulement l'ID)
    new_entry = {
        "date": date_id,
        "movies": req.get("movies", []) # si pas fourni, on met []
    }
    schedule.append(new_entry)
    write(schedule)

    return make_response(jsonify({"message": "schedule date added"}), 200)

# ajoute un film à une date (crée la date si elle n’existe pas)
@app.route("/<user_id>/schedule/<date>/movies", methods=['POST'])
def add_movie_to_date(user_id, date):
    """
    Add a movie to an existing date or create a new date entry if it does not exist.

    Args:
        user_id (str): ID of the requesting user.
        date (str): Date to which the movie will be added.

    Request Body:
        {
            "movie_id": "string" (required)
        }

    Returns:
        Response: JSON message indicating success or error if the movie/date already exists.
    """
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    # si pas admin -> accès interdit
    if not is_admin:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    req = request.get_json()
    movie_id = req.get("movie_id")

    if not movie_id:
        return make_response(jsonify({"error": "missing 'movie_id' in body"}), 400)

    # cherche si la date existe déjà
    for movies_date in schedule:
        if str(movies_date["date"]) == str(date):
            # si le film existe déjà dans la liste
            if movie_id in movies_date["movies"]:
                return make_response(jsonify({"error": "movie already scheduled for this date"}), 500)
            
            # sinon on ajoute
            movies_date["movies"].append(movie_id)
            write(schedule)
            return make_response(jsonify({"message": "movie added to existing date"}), 200)

    # si la date n'existe pas : on la crée
    new_entry = {
        "date": date,
        "movies": [movie_id]
    }
    schedule.append(new_entry)
    write(schedule)

    return make_response(jsonify({"message": "new date created and movie added"}), 200)

# supprime une date complète (tous les films inclus)
@app.route("/<user_id>/schedule/<date_id>", methods=['DELETE'])
def delete_date(user_id, date_id):
    """
    Delete an entire schedule entry (all movies) for a given date.

    Args:
        user_id (str): ID of the requesting user.
        date_id (str): Date to delete.

    Returns:
        Response: JSON message confirming deletion or error if the date is not found.
    """
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    # si pas admin -> accès interdit
    if not is_admin:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    global schedule # variable faisant référence en dehors fonction
    new_schedule = [s for s in schedule if str(s["date"]) != str(date_id)]

    if len(new_schedule) == len(schedule):
        return make_response(jsonify({"error": "date not found"}), 404)

    schedule = new_schedule
    write(schedule)
    return make_response(jsonify({"message": f"date {date_id} deleted"}), 200)

# supprime un film d’une date précise
@app.route("/<user_id>/schedule/<date_id>/movies/<movie_id>", methods=['DELETE'])
def delete_movie_from_date(user_id, date_id, movie_id):
    """
    Delete a specific movie from a given date.

    Args:
        user_id (str): ID of the requesting user.
        date_id (str): Date of the schedule.
        movie_id (str): ID of the movie to remove.

    Returns:
        Response: JSON message confirming removal or error if not found.
    """
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    # si pas admin -> accès interdit
    if not is_admin:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    for s in schedule:
        if str(s["date"]) == str(date_id):
            if movie_id in s["movies"]:
                s["movies"].remove(movie_id)
                write(schedule)
                return make_response(jsonify({"message": f"movie {movie_id} removed from date {date_id}"}), 200)
            return make_response(jsonify({"error": "movie not found in this date"}), 404)
    
    return make_response(jsonify({"error": "date not found"}), 404)

# supprime un film de toutes les dates
@app.route("/<user_id>/schedule/movies/<movie_id>", methods=['DELETE'])
def delete_movie_from_all_dates(user_id, movie_id):
    """
    Delete a specific movie from all scheduled dates.

    Args:
        user_id (str): ID of the requesting user.
        movie_id (str): ID of the movie to remove.

    Returns:
        Response: JSON message confirming removal from all dates,
                  or error if the movie was not scheduled.
    """
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    # si pas admin -> accès interdit
    if not is_admin:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    found = False
    for s in schedule:
        if movie_id in s["movies"]:
            s["movies"].remove(movie_id)
            found = True

    if not found:
        return make_response(jsonify({"error": "movie not found in any date"}), 404)

    write(schedule)
    return make_response(jsonify({"message": f"movie {movie_id} removed from all dates"}), 200)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
