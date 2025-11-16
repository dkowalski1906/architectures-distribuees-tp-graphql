from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from .base_repository import BaseBookingRepository

class MongoBookingRepository(BaseBookingRepository):
    """
    Implémentation du repository utilisant MongoDB.
    """

    def __init__(self, mongo_uri: str, db_name: str):
        """
        Initialise le repository MongoDB.

        Args:
            mongo_uri: URI de connexion MongoDB
            db_name: Nom de la base de données
        """
        try:
            self.client = MongoClient(mongo_uri)
            self.db = self.client[db_name]
            self.collection = self.db['bookings']

            # Création d'index pour optimiser les requêtes
            self.collection.create_index('userid', unique=True)

            print(f"✓ Connecté à MongoDB: {db_name}")
        except Exception as e:
            print(f"✗ Erreur de connexion à MongoDB: {e}")
            raise

    def _document_to_dict(self, doc: Optional[Dict]) -> Optional[Dict[str, Any]]:
        """
        Convertit un document MongoDB en dictionnaire Python.
        Supprime le champ _id de MongoDB.
        """
        if doc is None:
            return None
        doc.pop('_id', None)
        return doc

    def get_all_bookings(self) -> List[Dict[str, Any]]:
        """Récupère toutes les réservations"""
        bookings = list(self.collection.find())
        return [self._document_to_dict(booking) for booking in bookings]

    def get_booking_by_userid(self, userid: str) -> Optional[Dict[str, Any]]:
        """Récupère une réservation par l'ID utilisateur"""
        booking = self.collection.find_one({'userid': userid})
        return self._document_to_dict(booking)

    def booking_exists(self, userid: str, date: str, movieid: str) -> bool:
        """Vérifie si une réservation existe"""
        result = self.collection.find_one({
            'userid': userid,
            'dates': {
                '$elemMatch': {
                    'date': date,
                    'movies': movieid
                }
            }
        })
        return result is not None

    def add_booking(self, userid: str, date: str, movieid: str) -> Dict[str, Any]:
        """Ajoute une réservation"""
        # Vérifie si la réservation existe déjà
        if self.booking_exists(userid, date, movieid):
            raise ValueError("Booking already exists")

        # Cherche si l'utilisateur existe déjà
        booking = self.get_booking_by_userid(userid)

        if booking:
            # Vérifie si la date existe déjà
            date_exists = False
            for d in booking['dates']:
                if d['date'] == date:
                    date_exists = True
                    break

            if date_exists:
                # Ajoute le film à la date existante
                self.collection.update_one(
                    {'userid': userid, 'dates.date': date},
                    {'$push': {'dates.$.movies': movieid}}
                )
            else:
                # Ajoute une nouvelle date
                self.collection.update_one(
                    {'userid': userid},
                    {'$push': {'dates': {'date': date, 'movies': [movieid]}}}
                )
        else:
            # Crée une nouvelle réservation
            booking = {
                'userid': userid,
                'dates': [{
                    'date': date,
                    'movies': [movieid]
                }]
            }
            self.collection.insert_one(booking.copy())

        return self.get_booking_by_userid(userid)

    def remove_booking(self, userid: str, date: str, movieid: str) -> Dict[str, Any]:
        """Supprime une réservation spécifique"""
        if not self.booking_exists(userid, date, movieid):
            raise ValueError("Booking not found")

        # Supprime le film de la date
        self.collection.update_one(
            {'userid': userid, 'dates.date': date},
            {'$pull': {'dates.$.movies': movieid}}
        )

        return self.get_booking_by_userid(userid)

    def remove_all_bookings_for_user(self, userid: str) -> bool:
        """Supprime toutes les réservations d'un utilisateur"""
        result = self.collection.delete_one({'userid': userid})
        return result.deleted_count > 0

    def close(self):
        """Ferme la connexion MongoDB"""
        if self.client:
            self.client.close()
            print("✓ Connexion MongoDB fermée")