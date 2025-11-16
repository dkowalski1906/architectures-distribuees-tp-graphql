from graphql import GraphQLError
import requests
import time
import grpc

import config
from schedule_client import get_schedule_client
import schedule_pb2

# Récupération du repository
booking_repository = config.get_booking_repository()

# Client gRPC Schedule
schedule = get_schedule_client()

# Cache admin
user_admin_cache = {}

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def verify_admin(user_id):
    """Vérifie si user_id est admin, avec cache"""
    now = time.time()
    if user_id in user_admin_cache:
        cached = user_admin_cache[user_id]
        if now - cached["timestamp"] < config.CACHE_TTL:
            return cached["is_admin"], None

    try:
        r = requests.get(f"{config.USER_BASE_URL}/users/{user_id}/is_admin")
        if r.status_code == 200:
            data = r.json()
            is_admin = data.get("is_admin", False)
            user_admin_cache[user_id] = {"is_admin": is_admin, "timestamp": now}
            return is_admin, None
        else:
            raise GraphQLError("Unable to verify user")
    except requests.exceptions.RequestException:
        raise GraphQLError("User service unreachable")

# ============================================================================
# RESOLVERS POUR LES TYPES
# ============================================================================

def resolve_booking_userid(booking, info):
    """Résout le champ userid (retourne l'objet User complet)"""
    user_id = booking["userid"]

    try:
        # Appel au service User pour récupérer les détails
        r = requests.get(f"{config.USER_BASE_URL}/chris_rivers/users/{user_id}")
        if r.status_code == 200:
            return r.json()
        raise GraphQLError(f"User not found: {user_id}")
    except requests.exceptions.RequestException:
        raise GraphQLError("User service unreachable")

def resolve_booking_dates(booking, info):
    """Résout le champ dates"""
    dates_to_return = []
    for date in booking["dates"]:
        date["user_id"] = booking["userid"]
        dates_to_return.append(date)
    return dates_to_return

def resolve_date_movies(date, info):
    """Résout le champ movies (appelle le service Movie en GraphQL)"""
    user_id = date["user_id"]
    movies_to_return = []

    for movieid in date["movies"]:
        query = """
        query GetMovie($id: String!) {
            movie_by_id(id: $id) {
                id
                title
                director
                rating
            }
        }
        """

        try:
            response = requests.post(
                f"{config.MOVIE_BASE_URL}/{user_id}/graphql",
                json={'query': query, 'variables': {'id': movieid}}
            )
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                raise GraphQLError(f"Movie service error for id {movieid}: {data['errors']}")

            if "data" in data and "movie_by_id" in data["data"]:
                movie_details = data["data"]["movie_by_id"]
                if movie_details:
                    movies_to_return.append(movie_details)
                else:
                    raise GraphQLError(f"Movie not found: {movieid}")
            else:
                raise GraphQLError(f"Invalid movie service response for id {movieid}")

        except requests.exceptions.RequestException as e:
            raise GraphQLError(f"Movie service unreachable: {e}")

    return movies_to_return

# ============================================================================
# QUERIES
# ============================================================================

def bookings_json(_, info, user_id):
    """Récupère toutes les réservations"""
    _, error = verify_admin(user_id)
    if error:
        return error
    return booking_repository.get_all_bookings()

def booking_with_id(_, info, user_id, id):
    """Récupère une réservation par ID utilisateur"""
    _, error = verify_admin(user_id)
    if error:
        return error

    booking = booking_repository.get_booking_by_userid(id)
    if not booking:
        raise GraphQLError("Booking not found with id: " + id)
    return booking

# ============================================================================
# MUTATIONS
# ============================================================================

def add_booking(_, info, user_id, userid, date, movieid):
    """Ajoute une réservation"""
    is_admin, error = verify_admin(user_id)
    if error:
        return error
    if not is_admin:
        raise GraphQLError("Unauthorized: admin access required")

    # Vérifie auprès de Schedule que le film est dispo à cette date
    try:
        response = schedule.GetMoviesByDate(
            schedule_pb2.GetMoviesByDateRequest(
                userId=user_id,
                date=str(date)
            )
        )
        movie_ids = [m.id for m in response.movies]
        if movieid not in movie_ids:
            raise GraphQLError("Movie not scheduled on this date")

    except grpc.RpcError as e:
        raise GraphQLError(f"Schedule service error: {e.details()}")

    # Ajoute la réservation via le repository
    try:
        booking = booking_repository.add_booking(userid, date, movieid)
        return booking
    except ValueError as e:
        raise GraphQLError(str(e))

def remove_booking_with_movie_date_user(_, info, user_id, userid, date, movieid):
    """Supprime une réservation spécifique"""
    is_admin, error = verify_admin(user_id)
    if error:
        return error
    if not is_admin:
        raise GraphQLError("Unauthorized: admin access required")

    try:
        booking = booking_repository.remove_booking(userid, date, movieid)
        return booking
    except ValueError as e:
        raise GraphQLError(str(e))

def remove_bookings_with_user_id(_, info, user_id, userid):
    """Supprime toutes les réservations d'un utilisateur"""
    is_admin, error = verify_admin(user_id)
    if error:
        return error
    if not is_admin:
        raise GraphQLError("Unauthorized: admin access required")

    if not booking_repository.remove_all_bookings_for_user(userid):
        raise GraphQLError("User not found")

    return f"All bookings removed for userid: {userid}"