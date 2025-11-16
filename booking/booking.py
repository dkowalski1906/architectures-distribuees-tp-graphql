from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
from ariadne.explorer import ExplorerGraphiQL
from flask import Flask, request, jsonify
from flask_cors import CORS

import config
import resolvers as r

app = Flask(__name__)
CORS(app)

# Affichage de la configuration au démarrage
config.print_config()

# Interface GraphiQL
explorer = ExplorerGraphiQL()

# Création du schéma GraphQL
type_defs = load_schema_from_path('booking.graphql')

query = QueryType()
mutation = MutationType()

booking = ObjectType('Booking')
user = ObjectType('User')
date = ObjectType('Date')
movie = ObjectType('Movie')

# Association des resolvers
query.set_field('bookings_json', r.bookings_json)
query.set_field('booking_with_id', r.booking_with_id)
mutation.set_field('add_booking', r.add_booking)
mutation.set_field('remove_booking_with_movie_date_user', r.remove_booking_with_movie_date_user)
mutation.set_field('remove_bookings_with_user_id', r.remove_bookings_with_user_id)
booking.set_field("userid", r.resolve_booking_userid)
booking.set_field("dates", r.resolve_booking_dates)
date.set_field("movies", r.resolve_date_movies)

schema = make_executable_schema(type_defs, query, mutation, booking, user, date, movie)

# ============================================================================
# ROUTES
# ============================================================================

@app.route("/", methods=['GET'])
def home():
    """Page d'accueil du service"""
    return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/health", methods=['GET'])
def health_check():
    """Endpoint de santé"""
    return jsonify({
        "status": "healthy",
        "service": "booking",
        "using_mongodb": config.USE_MONGODB,
        "using_docker": config.USE_DOCKER
    }), 200

@app.route("/<user_id>/graphql", methods=['GET'])
def graphql_playground(user_id):
    """Interface GraphiQL"""
    return explorer.html(None), 200

@app.route("/<user_id>/graphql", methods=['POST'])
def graphql_server(user_id):
    """Endpoint GraphQL"""
    data = request.get_json()
    context = {"user_id": user_id}
    success, result = graphql_sync(
        schema,
        data,
        context_value=context,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

# ============================================================================
# DÉMARRAGE
# ============================================================================

if __name__ == "__main__":
    try:
        print(f"Server running on port {config.BOOKING_PORT}")
        app.run(host='0.0.0.0', port=config.BOOKING_PORT, debug=True)
    finally:
        if config.USE_MONGODB:
            r.booking_repository.close()