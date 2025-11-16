from flask import Flask, request, jsonify
from datetime import datetime
import requests

from ariadne import QueryType, MutationType, make_executable_schema, graphql_sync, ObjectType
from ariadne.explorer import ExplorerGraphiQL

explorer = ExplorerGraphiQL().html(None)

import config

# Initialisation Flask
app = Flask(__name__)
config.print_config()
movie_repository = config.get_movie_repository()
user_admin_cache = {}

# ============================================================================
# UTILITAIRES
# ============================================================================

def is_user_admin(user_id: str) -> bool:
    current_time = datetime.now()

    if user_id in user_admin_cache:
        cached = user_admin_cache[user_id]
        if (current_time - cached['timestamp']).total_seconds() < config.CACHE_TTL:
            return cached['is_admin']

    try:
        url = f"{config.USER_BASE_URL}/users/{user_id}/is_admin"
        resp = requests.get(url, timeout=5)

        if resp.status_code == 200:
            is_admin = resp.json().get("is_admin", False)
            user_admin_cache[user_id] = {
                "is_admin": is_admin,
                "timestamp": current_time
            }
            return is_admin
    except:
        pass
    return False

# ============================================================================
# SCHEMA ARIADNE
# ============================================================================

type_defs = """
    type Movie {
        id: String
        title: String
        director: String
        rating: Float
    }

    type Query {
        all_movies: [Movie!]
        movie_by_id(id: String!): Movie
        movie_by_title(title: String!): Movie
        movies_by_director(director: String!): [Movie!]
        movies_by_rating(min_rating: Float!): [Movie!]
    }

    type Mutation {
        add_movie(title: String!, director: String!, rating: Float!): Movie
    }
"""

query = QueryType()
mutation = MutationType()
movie_obj = ObjectType("Movie")

# ============================================================================
# RESOLVERS QUERY
# ============================================================================

@query.field("all_movies")
def resolve_all_movies(_, info):
    return movie_repository.get_all_movies()

@query.field("movie_by_id")
def resolve_movie_by_id(_, info, id):
    return movie_repository.get_movie_by_id(id)

@query.field("movie_by_title")
def resolve_movie_by_title(_, info, title):
    return movie_repository.get_movie_by_title(title)

@query.field("movies_by_director")
def resolve_movies_by_director(_, info, director):
    return movie_repository.get_movies_by_director(director)

@query.field("movies_by_rating")
def resolve_movies_by_rating(_, info, min_rating):
    return movie_repository.get_movies_by_rating(min_rating)

# ============================================================================
# RESOLVER MUTATION
# ============================================================================

@mutation.field("add_movie")
def resolve_add_movie(_, info, title, director, rating):
    user_id = info.context.get("user_id")

    if not is_user_admin(user_id):
        raise Exception("Accès refusé : droits administrateur requis")

    new_movie = movie_repository.add_movie({
        "title": title,
        "director": director,
        "rating": rating
    })
    return new_movie

# ============================================================================
# SCHEMA FINAL
# ============================================================================

schema = make_executable_schema(type_defs, query, mutation, movie_obj)

# ============================================================================
# ROUTES
# ============================================================================

@app.route("/<user_id>/graphql", methods=["GET"])
def graphql_playground(user_id):
    return explorer, 200

@app.route("/<user_id>/graphql", methods=["POST"])
def graphql_server(user_id):
    data = request.get_json()
    context = {"user_id": user_id}
    success, result = graphql_sync(schema, data, context_value=context)
    return jsonify(result), 200

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "movie",
        "using_mongodb": config.USE_MONGODB,
        "using_docker": config.USE_DOCKER
    }), 200

# ============================================================================
# DÉMARRAGE
# ============================================================================

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=config.MOVIE_PORT, debug=True)
    finally:
        if config.USE_MONGODB:
            movie_repository.close()
