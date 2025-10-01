from flask import Flask, render_template, request, jsonify, make_response
import requests
import json, time
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

PORT = 3203
HOST = '0.0.0.0'
SCHEDULE_URL = "http://localhost:3202" # service Schedule
MOVIE_URL   = "http://localhost:3200" # service Movie
USER_URL  = "http://localhost:3201" # microservice User

CACHE_TTL = 60 # secondes de validité du cache pour is_admin

# cache local pour stocker si un user est admin
# format : { "user_id": {"is_admin": True/False, "timestamp": 123456789} }
user_admin_cache = {}

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
    bookings = json.load(jsf)["bookings"]

def write(bookings_data):
    with open('{}/databases/bookings.json'.format("."), 'w') as f:
        full = {}
        full['bookings'] = bookings_data
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
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

# récupère toutes les réservations
@app.route("/<user_id>/bookings", methods=['GET'])
def get_all_bookings(user_id):
    """
    Retrieve all bookings in the system.

    Args:
        user_id (str): ID of the requesting user.

    Returns:
        Response: JSON response containing all bookings if the user is admin,
                  or error if unauthorized.
    """
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    # si pas admin -> accès interdit
    if not is_admin:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    return make_response(jsonify(bookings), 200)

# récupère les réservations d’un utilisateur
@app.route("/<user_id>/bookings/<user_id_wanted>", methods=['GET'])
def get_user_bookings(user_id, user_id_wanted):
    """
    Retrieve all bookings for a specific user.

    Args:
        user_id (str): ID of the requesting user.
        user_id_wanted (str): ID of the user whose bookings are requested.

    Returns:
        Response: JSON response with user's bookings if found,
                  or error if user not found or unauthorized.
    """
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    # si pas admin OU que c'est pas l'utilisateur connecté -> accès interdit
    if not is_admin and user_id_wanted != user_id:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    for b in bookings:
        if b["userid"] == user_id_wanted:
            return make_response(jsonify(b), 200)
    return make_response(jsonify({"error": "user not found"}), 404)

# ajoute une réservation pour un utilisateur
@app.route("/<user_id>/bookings/<user_id_wanted>", methods=['POST'])
def add_booking(user_id, user_id_wanted):
    """
    Add a booking for a user.

    Args:
        user_id (str): ID of the requesting user.
        user_id_wanted (str): ID of the user for whom the booking is added.

    Request Body:
        {
            "date": "YYYY-MM-DD",
            "movie_id": "string"
        }

    Returns:
        Response: JSON message confirming booking addition,
                  or error if booking already exists, date/movie invalid, or unauthorized.
    """
    req = request.get_json()
    date = req.get("date")
    movie_id = req.get("movie_id")

    if not date or not movie_id:
        return make_response(jsonify({"error": "missing 'date' or 'movie_id'"}), 400)

    is_admin, error = verify_admin(user_id)
    if error:
        return error

    # si pas admin OU que c'est pas l'utilisateur connecté -> accès interdit
    if not is_admin and user_id_wanted != user_id:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    # vérifie auprès de Schedule que le film est dispo à cette date
    r = requests.get(f"{SCHEDULE_URL}/{user_id}/schedule/{date}") # appele microservice de Schedule
    if r.status_code != 200:
        return make_response(jsonify({"error": "date not found in schedule"}), 404)

    movies_for_date = r.json()
    if movie_id not in movies_for_date:
        return make_response(jsonify({"error": "movie not available at this date"}), 400)

    # si l’utilisateur existe déjà
    for b in bookings:
        if b["userid"] == user_id_wanted:
            for d in b["dates"]:
                if d["date"] == date:
                    if movie_id in d["movies"]:
                        return make_response(jsonify({"error": "booking already exists"}), 400)
                    d["movies"].append(movie_id)
                    write(bookings)
                    return make_response(jsonify({"message": "movie booked"}), 200)
            # sinon nouvelle date pour l’utilisateur
            b["dates"].append({"date": date, "movies": [movie_id]})
            write(bookings)
            return make_response(jsonify({"message": "movie booked with new date"}), 200)

    # si l’utilisateur n’existe pas encore -> on le crée
    new_booking = {
        "userid": user_id_wanted,
        "dates": [
            {"date": date, "movies": [movie_id]}
        ]
    }
    bookings.append(new_booking)
    write(bookings)
    return make_response(jsonify({"message": "new user created and booking added"}), 200)

# supprime une réservation (film spécifique pour une date d’un user)
@app.route("/<user_id>/bookings/<user_id_wanted>/<date>/<movie_id>", methods=['DELETE'])
def delete_booking(user_id, user_id_wanted, date, movie_id):
    """
    Delete a specific booking for a user.

    Args:
        user_id (str): ID of the requesting user.
        user_id_wanted (str): ID of the user.
        date (str): Booking date.
        movie_id (str): ID of the movie to delete from booking.

    Returns:
        Response: JSON message confirming deletion,
                  or error if booking/movie not found or unauthorized.
    """
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    # si pas admin OU que c'est pas l'utilisateur connecté -> accès interdit
    if not is_admin and user_id_wanted != user_id:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    for b in bookings:
        if b["userid"] == user_id_wanted:
            for d in b["dates"]:
                if d["date"] == date:
                    if movie_id in d["movies"]:
                        d["movies"].remove(movie_id)
                        write(bookings)
                        return make_response(jsonify({"message": "booking deleted"}), 200)
                    return make_response(jsonify({"error": "movie not found in this booking"}), 404)
    return make_response(jsonify({"error": "booking not found"}), 404)

# supprime toutes les réservations d’un utilisateur
@app.route("/<user_id>/bookings/<user_id_wanted>", methods=['DELETE'])
def delete_user_bookings(user_id, user_id_wanted):
    """
    Delete all bookings of a specific user.

    Args:
        user_id (str): ID of the requesting user.
        user_id_wanted (str): ID of the user whose bookings will be deleted.

    Returns:
        Response: JSON message confirming deletion of all bookings,
                  or error if user not found or unauthorized.
    """
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    # si pas admin OU que c'est pas l'utilisateur connecté -> accès interdit
    if not is_admin and user_id_wanted != user_id:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    global bookings # variable en dehors de fonction
    new_bookings = [b for b in bookings if b["userid"] != user_id_wanted]
    if len(new_bookings) == len(bookings):
        return make_response(jsonify({"error": "user not found"}), 404)

    bookings = new_bookings
    write(bookings)
    return make_response(jsonify({"message": f"all bookings deleted for {user_id_wanted}"}), 200)

# récupère les réservations d’un utilisateur avec détail des films
@app.route("/<user_id>/bookings/<user_id_wanted>/details", methods=['GET'])
def get_user_booking_details(user_id, user_id_wanted):
    """
    Retrieve all bookings of a user with detailed movie information.

    Args:
        user_id (str): ID of the requesting user.
        user_id_wanted (str): ID of the user whose detailed bookings are requested.

    Returns:
        Response: JSON response containing user's bookings with movie details,
                  or error if user not found or unauthorized.
    """
    is_admin, error = verify_admin(user_id)
    if error:
        return error

    # si pas admin OU que c'est pas l'utilisateur connecté -> accès interdit
    if not is_admin and user_id_wanted != user_id:
        return make_response(jsonify({"error": "Unauthorized: admin access required"}), 403)

    for b in bookings:
        if b["userid"] == user_id_wanted:
            detailed = {"userid": user_id_wanted, "dates": []}
            for d in b["dates"]:
                movies_detail = []
                for m in d["movies"]:
                    r = requests.get(f"{MOVIE_URL}/{user_id}/movies/{m}") # appele microservice de Movie
                    if r.status_code == 200:
                        movies_detail.append(r.json())
                    else:
                        movies_detail.append({"id": m, "error": "movie not found"})
                detailed["dates"].append({
                    "date": d["date"],
                    "movies": movies_detail
                })
            return make_response(jsonify(detailed), 200)
    return make_response(jsonify({"error": "user not found"}), 404)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
