import grpc
from concurrent import futures
import schedule_pb2
import schedule_pb2_grpc
import requests
import time

# Import de la configuration
import config

# Affichage de la configuration au démarrage
config.print_config()

# Récupération du repository approprié (JSON ou MongoDB)
schedule_repository = config.get_schedule_repository()

# Cache pour les vérifications admin
user_admin_cache = {}

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def verify_admin(user_id):
    """Vérifie si un utilisateur est admin avec cache"""
    now = time.time()

    if user_id in user_admin_cache:
        cached = user_admin_cache[user_id]
        if now - cached["timestamp"] < config.CACHE_TTL:
            return cached["is_admin"], None

    try:
        response = requests.get(f"{config.USER_BASE_URL}/users/{user_id}/is_admin")
        response.raise_for_status()
        data = response.json()
        is_admin = data.get("is_admin", False)
        user_admin_cache[user_id] = {"is_admin": is_admin, "timestamp": now}
        return is_admin, None

    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Unable to verify user ({response.status_code}): {e}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"User service unreachable: {e}")


def fetch_movie_data(user_id, movie_id, context):
    """Récupère un film depuis le microservice Movie (GraphQL)"""
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
            json={"query": query, "variables": {"id": movie_id}}
        )
        response.raise_for_status()
        data = response.json()

        # Gestion des erreurs GraphQL
        if "errors" in data:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Movie not found for id {movie_id}")

        movie_details = data.get("data", {}).get("movie_by_id")

        if not movie_details:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Movie not found for id {movie_id}")

        return schedule_pb2.MovieData(
            id=movie_details["id"],
            title=movie_details["title"],
            director=movie_details["director"],
            rating=movie_details["rating"]
        )

    except requests.exceptions.RequestException as e:
        context.abort(grpc.StatusCode.UNAVAILABLE, f"Movie service unreachable: {e}")


# ============================================================================
# SERVICE gRPC
# ============================================================================

class ScheduleServicer(schedule_pb2_grpc.ScheduleServicer):

    def _check_admin(self, user_id, context, require_admin=False):
        """Vérifie les droits admin"""
        try:
            is_admin, _ = verify_admin(user_id)
        except Exception as e:
            context.abort(grpc.StatusCode.UNAVAILABLE, str(e))
        if require_admin and not is_admin:
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Admin access required")
        return is_admin

    def GetJson(self, request, context):
        """Récupère tous les horaires"""
        self._check_admin(request.userId, context)

        schedules = schedule_repository.get_all_schedules()

        for schedule in schedules:
            movies = [
                fetch_movie_data(request.userId, movie_id, context)
                for movie_id in schedule["movies"]
            ]
            yield schedule_pb2.ScheduleData(date=schedule["date"], movies=movies)

    def GetMoviesByDate(self, request, context):
        """Récupère les films pour une date donnée"""
        self._check_admin(request.userId, context)

        schedule = schedule_repository.get_schedule_by_date(request.date)

        if not schedule:
            context.abort(grpc.StatusCode.NOT_FOUND, "No movies found for this date")

        movies = [
            fetch_movie_data(request.userId, movie_id, context)
            for movie_id in schedule["movies"]
        ]
        return schedule_pb2.ScheduleData(date=schedule["date"], movies=movies)

    def GetScheduleByMovie(self, request, context):
        """Récupère les dates où un film est programmé"""
        self._check_admin(request.userId, context)

        movie_id = request.movieId
        if not movie_id:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "movieId not provided")

        dates = schedule_repository.get_dates_by_movie(movie_id)

        if not dates:
            context.abort(grpc.StatusCode.NOT_FOUND, "No dates found for this movie")

        return schedule_pb2.DateData(dates=dates)

    def AddSchedule(self, request, context):
        """Ajoute un nouvel horaire complet"""
        self._check_admin(request.userId, context, require_admin=True)

        try:
            # Vérifie que tous les films existent
            movies = [
                fetch_movie_data(request.userId, movie_id, context)
                for movie_id in request.moviesId
            ]

            # Ajoute l'horaire
            schedule_data = {
                "date": request.date,
                "movies": [movie.id for movie in movies]
            }
            schedule_repository.add_schedule(schedule_data)

            return schedule_pb2.ScheduleData(date=request.date, movies=movies)

        except ValueError as e:
            context.abort(grpc.StatusCode.ALREADY_EXISTS, str(e))

    def AddMovieToDate(self, request, context):
        """Ajoute des films à une date"""
        self._check_admin(request.userId, context, require_admin=True)

        if not request.moviesId:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "At least one movieId required")

        try:
            # Ajoute les films (ou crée la date si elle n'existe pas)
            schedule = schedule_repository.add_movies_to_date(
                request.date,
                list(request.moviesId)
            )

            # Récupère les détails de tous les films
            movies = [
                fetch_movie_data(request.userId, movie_id, context)
                for movie_id in schedule["movies"]
            ]

            return schedule_pb2.ScheduleData(date=request.date, movies=movies)

        except ValueError as e:
            context.abort(grpc.StatusCode.ALREADY_EXISTS, str(e))

    def DeleteDate(self, request, context):
        """Supprime un horaire complet"""
        self._check_admin(request.userId, context, require_admin=True)

        if not schedule_repository.delete_schedule(request.date):
            context.abort(grpc.StatusCode.NOT_FOUND, "Date not found")

        return schedule_pb2.Empty()

    def DeleteMovieFromDate(self, request, context):
        """Supprime des films d'une date"""
        self._check_admin(request.userId, context, require_admin=True)

        if not request.moviesId:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "moviesId list required")

        try:
            schedule_repository.delete_movies_from_date(
                request.date,
                list(request.moviesId)
            )
            return schedule_pb2.Empty()

        except ValueError as e:
            context.abort(grpc.StatusCode.NOT_FOUND, str(e))


# ============================================================================
# DÉMARRAGE DU SERVEUR gRPC
# ============================================================================

def serve():
    print(f"Schedule gRPC service started on port {config.SCHEDULE_PORT}")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    schedule_pb2_grpc.add_ScheduleServicer_to_server(ScheduleServicer(), server)
    server.add_insecure_port(f"[::]:{config.SCHEDULE_PORT}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    try:
        serve()
    finally:
        if config.USE_MONGODB:
            schedule_repository.close()