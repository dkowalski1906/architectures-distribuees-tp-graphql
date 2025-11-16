from flask import Flask, request, jsonify, make_response
import time
import requests
from flask_cors import CORS

# Import de la configuration
import config

app = Flask(__name__)
CORS(app)

# Affichage de la configuration au démarrage
config.print_config()

# Récupération du repository approprié (JSON ou MongoDB)
user_repository = config.get_user_repository()

# Cache pour les vérifications admin
user_admin_cache = {}

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def verify_admin(user_id):
    """
    Vérifie si un utilisateur est admin, avec cache.

    Args:
        user_id (str): ID de l'utilisateur à vérifier.

    Returns:
        tuple: (is_admin (bool), error_response (Response ou None))
    """
    now = time.time()

    # Vérifie le cache
    if user_id in user_admin_cache:
        cached = user_admin_cache[user_id]
        if now - cached["timestamp"] < config.CACHE_TTL:
            return cached["is_admin"], None

    # Appel au repository
    try:
        is_admin = user_repository.is_admin(user_id)
        user_admin_cache[user_id] = {"is_admin": is_admin, "timestamp": now}
        return is_admin, None
    except Exception as e:
        print(f"Erreur lors de la vérification admin: {e}")
        return False, make_response(jsonify({"error": "Unable to verify user"}), 401)

# ============================================================================
# ROUTES
# ============================================================================

@app.route("/", methods=['GET'])
def home():
    """Page d'accueil du service"""
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/health", methods=['GET'])
def health_check():
    """Endpoint de santé"""
    return jsonify({
        "status": "healthy",
        "service": "user",
        "using_mongodb": config.USE_MONGODB,
        "using_docker": config.USE_DOCKER
    }), 200

@app.route("/users/<user_id>/is_admin", methods=['GET'])
def is_admin(user_id):
    """Vérifie si un utilisateur est admin"""
    try:
        is_admin_status = user_repository.is_admin(user_id)
        if is_admin_status is not None:
            return jsonify({
                "id": user_id,
                "is_admin": is_admin_status
            }), 200
        return jsonify({"error": "User ID not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/<user_id>/users/json", methods=['GET'])
def get_json(user_id):
    """Récupère tous les utilisateurs en JSON"""
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    if not is_admin:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    users = user_repository.get_all_users()
    return jsonify(users)

@app.route("/<user_id>/users/<user_id_wanted>", methods=['GET'])
def get_user_by_id(user_id, user_id_wanted):
    """Récupère un utilisateur par son ID"""
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    if not is_admin:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    user = user_repository.get_user_by_id(user_id_wanted)
    if user:
        return jsonify(user), 200
    return jsonify({"error": "User ID not found"}), 404

@app.route("/<user_id>/users/by_name", methods=['GET'])
def get_user_by_name(user_id):
    """Récupère un utilisateur par son nom"""
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    if not is_admin:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    name = request.args.get('name')
    if not name:
        return make_response(jsonify({"error": "Name parameter required"}), 400)

    user = user_repository.get_user_by_name(name)
    if user:
        return jsonify(user), 200
    return make_response(jsonify({"error": "User name not found"}), 404)

@app.route("/<user_id>/users/bookings", methods=["GET"])
def get_users_from_booking(user_id):
    """Récupère les utilisateurs ayant réservé un film à une date donnée"""
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    if not is_admin:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    req = request.get_json()
    date = req.get("date")
    movie_id = req.get("movie")
    user_list = []

    try:
        r = requests.get(f"{config.BOOKING_BASE_URL}/{user_id}/bookings")
        data = r.json()

        for b in data:
            for d in b["dates"]:
                if d["date"] == date:
                    for m in d["movies"]:
                        if m == movie_id:
                            user = user_repository.get_user_by_id(b["userid"])
                            if user is None:
                                return make_response(jsonify({"error": "The user does not exist"}), 404)
                            user_list.append(user["name"])

        return make_response(jsonify({"users": user_list}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

@app.route("/<user_id>/users/<user_id_wanted>", methods=['POST'])
def add_user(user_id, user_id_wanted):
    """Ajoute un nouvel utilisateur"""
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    if not is_admin:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    req = request.get_json()

    try:
        user_repository.add_user(req)
        return make_response(jsonify({"message": "User added"}), 200)
    except ValueError as e:
        return make_response(jsonify({"error": str(e)}), 500)

@app.route("/<user_id>/users/<user_id_wanted>/<name>", methods=['PUT'])
def update_user_name(user_id, user_id_wanted, name):
    """Met à jour le nom d'un utilisateur"""
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    if not is_admin:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    user = user_repository.update_user_name(user_id_wanted, name)
    if user:
        return make_response(jsonify(user), 200)
    return make_response(jsonify({"error": "user ID not found"}), 500)

@app.route("/<user_id>/users/<user_id_wanted>", methods=['DELETE'])
def delete_user(user_id, user_id_wanted):
    """Supprime un utilisateur"""
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    if not is_admin:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    if user_repository.delete_user(user_id_wanted):
        return make_response(jsonify({"message": "User deleted"}), 200)
    return make_response(jsonify({"error": "user ID not found"}), 500)

# ============================================================================
# DÉMARRAGE
# ============================================================================

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=config.USER_PORT, debug=True)
    finally:
        if config.USE_MONGODB:
            user_repository.close()