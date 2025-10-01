from flask import Flask, request, jsonify, make_response
import time, json, requests
from werkzeug.exceptions import NotFound
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

PORT = 3200
HOST = '0.0.0.0'
USER_URL  = "http://localhost:3201" # microservice User

CACHE_TTL = 60 # secondes de validité du cache pour is_admin

# cache local pour stocker si un user est admin
# format : { "user_id": {"is_admin": True/False, "timestamp": 123456789} }
user_admin_cache = {}

# charge le fichier JSON contenant les films
with open('{}/databases/movies.json'.format("."), 'r') as jsf:
    movies = json.load(jsf)["movies"]
    print(movies)

# sauvegarde les films dans le fichier
def write(movies):
    with open('{}/databases/movies.json'.format("."), 'w') as f:
        full = {}
        full['movies']=movies
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
    Home endpoint for the Movie service.

    Returns:
        Response: HTML welcome message.
    """
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

# retourne tous les films en JSON brut
@app.route("/<user_id>/movies/json", methods=['GET'])
def get_json(user_id):
    """
    Get all movies in raw JSON format.

    Args:
        user_id (str): ID of the requesting user.

    Returns:
        Response: JSON response with the list of all movies,
                  or an error if user is not authorized.
    """
    _, error = verify_admin(user_id)
    if error:
        return error

    res = make_response(jsonify(movies), 200)
    return res

# retourne un film à partir de son ID
@app.route("/<user_id>/movies/<movie_id>", methods=['GET'])
def get_movie_by_id(user_id, movie_id):
    """
    Get a movie by its ID.

    Args:
        user_id (str): ID of the requesting user.
        movie_id (str): ID of the movie to retrieve.

    Returns:
        Response: JSON response with movie details if found,
                  or an error if movie ID is not found.
    """
    _, error = verify_admin(user_id)
    if error:
        return error

    for movie in movies:
        if str(movie["id"]) == str(movie_id):
            res = make_response(jsonify(movie),200)
            return res
    return make_response(jsonify({"error":"Movie ID not found"}),500)

# retourne un film à partir de son titre
@app.route("/<user_id>/movies/by_title", methods=['GET'])
def get_movie_by_title(user_id):
    """
    Get a movie by its title.

    Args:
        user_id (str): ID of the requesting user.

    Query Parameters:
        title (str): Title of the movie to search for.

    Returns:
        Response: JSON response with movie details if found,
                  or an error if title is not found.
    """
    _, error = verify_admin(user_id)
    if error:
        return error
    
    json = ""
    if request.args:
        req = request.args
        for movie in movies:
            if str(movie["title"]) == str(req["title"]):
                json = movie

    if not json:
        res = make_response(jsonify({"error":"movie title not found"}),500)
    else:
        res = make_response(jsonify(json),200)
    return res

# ajoute un nouveau film
@app.route("/<user_id>/movies/<movie_id>", methods=['POST'])
def add_movie(user_id, movie_id):
    """
    Add a new movie.

    Args:
        user_id (str): ID of the requesting user.
        movie_id (str): ID for the new movie.

    Request Body:
        JSON object with movie details (id, title, rating, etc.)

    Returns:
        Response: JSON message confirming addition,
                  or error if movie ID already exists or user is not admin.
    """
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    # si pas admin -> accès interdit
    if not is_admin:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    req = request.get_json()

    for movie in movies:
        if str(movie["id"]) == str(movie_id):
            print(movie["id"])
            print(movie_id)
            return make_response(jsonify({"error":"movie ID already exists"}),500)

    movies.append(req)
    write(movies)
    res = make_response(jsonify({"message":"movie added"}),200)
    return res

#modifie le score d'un film existant
@app.route("/<user_id>/movies/<movie_id>/<rate>", methods=['PUT'])
def update_movie_rating(user_id, movie_id, rate):
    """
    Update the rating of an existing movie.

    Args:
        user_id (str): ID of the requesting user.
        movie_id (str): ID of the movie to update.
        rate (str or float): New rating for the movie.

    Returns:
        Response: JSON response with updated movie data,
                  or error if movie ID is not found.
    """
    _, error = verify_admin(user_id)
    if error:
        return error

    for movie in movies:
        if str(movie["id"]) == str(movie_id):
            movie["rating"] = rate
            res = make_response(jsonify(movie),200)
            write(movies)
            return res

    res = make_response(jsonify({"error":"movie ID not found"}),500)
    return res

# supprime un film à partir de son ID
@app.route("/<user_id>/movies/<movie_id>", methods=['DELETE'])
def delete_movie(user_id, movie_id):
    """
    Delete a movie by its ID.

    Args:
        user_id (str): ID of the requesting user.
        movie_id (str): ID of the movie to delete.

    Returns:
        Response: JSON response confirming deletion,
                  or error if movie ID is not found or user is not admin.
    """
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    # si pas admin -> accès interdit
    if not is_admin:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    for movie in movies:
        if str(movie["id"]) == str(movie_id):
            movies.remove(movie)
            write(movies)
            return make_response(jsonify(movie),200)

    res = make_response(jsonify({"error":"movie ID not found"}),500)
    return res

if __name__ == "__main__":
    #p = sys.argv[1]
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)
