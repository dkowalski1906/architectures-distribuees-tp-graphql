import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# ============================================================================
# CONFIGURATION GLOBALE
# ============================================================================

USE_DOCKER = os.getenv('USE_DOCKER', 'false').lower() == 'true'
USE_MONGODB = os.getenv('USE_MONGODB', 'false').lower() == 'true'

# ============================================================================
# CONFIGURATION MONGODB
# ============================================================================

MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_USER = os.getenv('MONGO_USER', 'admin')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'password')

# Nom de la base de données spécifique au service User
MONGO_DB_NAME = 'users_db'

# URI de connexion MongoDB
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"

# ============================================================================
# CONFIGURATION DES SERVICES (pour appels inter-services)
# ============================================================================

# Service Booking (utilisé dans get_users_from_booking)
BOOKING_HOST = 'booking' if USE_DOCKER else 'localhost'
BOOKING_PORT = int(os.getenv('BOOKING_PORT', 3203))
BOOKING_BASE_URL = f"http://{BOOKING_HOST}:{BOOKING_PORT}"

# Service User (ce service)
USER_HOST = 'user' if USE_DOCKER else 'localhost'
USER_PORT = int(os.getenv('USER_PORT', 3201))
USER_BASE_URL = f"http://{USER_HOST}:{USER_PORT}"

# ============================================================================
# CONFIGURATION JSON (fallback)
# ============================================================================

JSON_DATA_PATH = os.path.join(os.path.dirname(__file__), 'databases', 'users.json')

# ============================================================================
# CONFIGURATION DU CACHE ADMIN
# ============================================================================

CACHE_TTL = int(os.getenv('CACHE_TTL', 60))  # Time-to-live en secondes

# ============================================================================
# FONCTION POUR RÉCUPÉRER LE REPOSITORY
# ============================================================================

def get_user_repository():
    """
    Factory function pour obtenir le repository approprié
    selon la configuration (MongoDB ou JSON)
    """
    if USE_MONGODB:
        from repositories.mongodb_repository import MongoUserRepository
        return MongoUserRepository(
            mongo_uri=MONGO_URI,
            db_name=MONGO_DB_NAME
        )
    else:
        from repositories.json_repository import JsonUserRepository
        return JsonUserRepository(json_file=JSON_DATA_PATH)

# ============================================================================
# LOGS DE DÉMARRAGE (pour debug)
# ============================================================================

def print_config():
    """Affiche la configuration au démarrage (utile pour debug)"""
    print("=" * 60)
    print("CONFIGURATION DU SERVICE USER")
    print("=" * 60)
    print(f"Mode Docker       : {USE_DOCKER}")
    print(f"Utilise MongoDB   : {USE_MONGODB}")
    if USE_MONGODB:
        print(f"MongoDB Host      : {MONGO_HOST}:{MONGO_PORT}")
        print(f"MongoDB Database  : {MONGO_DB_NAME}")
    else:
        print(f"JSON Data Path    : {JSON_DATA_PATH}")
    print(f"Booking Service   : {BOOKING_BASE_URL}")
    print(f"User Service      : {USER_BASE_URL}")
    print(f"Cache TTL         : {CACHE_TTL}s")
    print("=" * 60)