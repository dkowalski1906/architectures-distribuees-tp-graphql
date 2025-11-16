import json
from typing import List, Optional, Dict, Any
from .base_repository import BaseBookingRepository

class JsonBookingRepository(BaseBookingRepository):
    """
    Implémentation du repository utilisant un fichier JSON.
    Compatible avec l'ancienne architecture.
    """

    def __init__(self, json_file: str):
        """
        Initialise le repository JSON.

        Args:
            json_file: Chemin vers le fichier JSON
        """
        self.json_file = json_file
        self._load_data()

    def _load_data(self):
        """Charge les données depuis le fichier JSON"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.bookings = data.get('bookings', [])
        except FileNotFoundError:
            print(f"Fichier {self.json_file} non trouvé. Initialisation avec données vides.")
            self.bookings = []

    def _save_data(self):
        """Sauvegarde les données dans le fichier JSON"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump({'bookings': self.bookings}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def get_all_bookings(self) -> List[Dict[str, Any]]:
        """Récupère toutes les réservations"""
        return self.bookings

    def get_booking_by_userid(self, userid: str) -> Optional[Dict[str, Any]]:
        """Récupère une réservation par l'ID utilisateur"""
        for booking in self.bookings:
            if booking.get('userid') == userid:
                return booking
        return None

    def booking_exists(self, userid: str, date: str, movieid: str) -> bool:
        """Vérifie si une réservation existe"""
        booking = self.get_booking_by_userid(userid)
        if not booking:
            return False

        for d in booking.get('dates', []):
            if d.get('date') == date:
                if movieid in d.get('movies', []):
                    return True
        return False

    def add_booking(self, userid: str, date: str, movieid: str) -> Dict[str, Any]:
        """Ajoute une réservation"""
        # Vérifie si la réservation existe déjà
        if self.booking_exists(userid, date, movieid):
            raise ValueError("Booking already exists")

        # Cherche si l'utilisateur existe déjà
        booking = self.get_booking_by_userid(userid)

        if booking:
            # Utilisateur existe, cherche la date
            date_found = False
            for d in booking['dates']:
                if d['date'] == date:
                    # Date existe, ajoute le film
                    d['movies'].append(movieid)
                    date_found = True
                    break

            if not date_found:
                # Date n'existe pas, crée-la
                booking['dates'].append({
                    'date': date,
                    'movies': [movieid]
                })
        else:
            # Utilisateur n'existe pas, crée-le
            booking = {
                'userid': userid,
                'dates': [{
                    'date': date,
                    'movies': [movieid]
                }]
            }
            self.bookings.append(booking)

        self._save_data()
        return booking

    def remove_booking(self, userid: str, date: str, movieid: str) -> Dict[str, Any]:
        """Supprime une réservation spécifique"""
        booking = self.get_booking_by_userid(userid)

        if not booking:
            raise ValueError("Booking not found")

        for d in booking['dates']:
            if d['date'] == date:
                if movieid in d['movies']:
                    d['movies'].remove(movieid)
                    self._save_data()
                    return booking
                raise ValueError("Movie not found in this booking")

        raise ValueError("Date not found in this booking")

    def remove_all_bookings_for_user(self, userid: str) -> bool:
        """Supprime toutes les réservations d'un utilisateur"""
        initial_count = len(self.bookings)
        self.bookings = [b for b in self.bookings if b['userid'] != userid]

        if len(self.bookings) < initial_count:
            self._save_data()
            return True
        return False