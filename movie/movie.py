from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
from flask import Flask, request, jsonify, make_response
import time, json, requests
from werkzeug.exceptions import NotFound
from flask_cors import CORS
import resolvers as r

app = Flask(__name__)

CORS(app)

PORT = 3200
HOST = '0.0.0.0'
USER_URL  = "http://localhost:3201" # microservice User

CACHE_TTL = 60 # secondes de validité du cache pour is_admin

# cache local pour stocker si un user est admin
# format : { "user_id": {"is_admin": True/False, "timestamp": 123456789} }
user_admin_cache = {}

# Création du schéma GraphQL
type_defs = load_schema_from_path('movie.graphql')

query = QueryType()
mutation = MutationType()

movie = ObjectType('Movie')

query.set_field('movie_with_id', r.movie_with_id)
query.set_field('movie_with_title', r.movie_with_title)
query.set_field('movies_json', r.movies_json)

mutation.set_field('add_movie', r.add_movie)
mutation.set_field('update_movie_rate', r.update_movie_rate)
mutation.set_field('remove_movie_with_id', r.remove_movie_with_id)

schema = make_executable_schema(type_defs, movie, query, mutation)

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

# route GraphQL
@app.route('/graphql', methods=['POST'])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
                        schema,
                        data,
                        context_value=None,
                        debug=app.debug
                    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    #p = sys.argv[1]
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)
