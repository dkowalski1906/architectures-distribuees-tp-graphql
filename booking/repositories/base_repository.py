from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class BaseBookingRepository(ABC):
    """
    Interface abstraite pour le repository des réservations.
    Toutes les implémentations (JSON, MongoDB) doivent respecter ce contrat.
    """

    @abstractmethod
    def get_all_bookings(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les réservations.

        Returns:
            List[Dict]: Liste de toutes les réservations
        """
        pass

    @abstractmethod
    def get_booking_by_userid(self, userid: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une réservation par l'ID utilisateur.

        Args:
            userid: L'identifiant de l'utilisateur

        Returns:
            Dict ou None: La réservation si trouvée, None sinon
        """
        pass

    @abstractmethod
    def add_booking(self, userid: str, date: str, movieid: str) -> Dict[str, Any]:
        """
        Ajoute une réservation (ou l'ajoute à une réservation existante).

        Args:
            userid: L'identifiant de l'utilisateur
            date: La date de la réservation
            movieid: L'identifiant du film

        Returns:
            Dict: La réservation mise à jour ou créée
        """
        pass

    @abstractmethod
    def remove_booking(self, userid: str, date: str, movieid: str) -> Dict[str, Any]:
        """
        Supprime une réservation spécifique.

        Args:
            userid: L'identifiant de l'utilisateur
            date: La date de la réservation
            movieid: L'identifiant du film

        Returns:
            Dict: La réservation mise à jour
        """
        pass

    @abstractmethod
    def remove_all_bookings_for_user(self, userid: str) -> bool:
        """
        Supprime toutes les réservations d'un utilisateur.

        Args:
            userid: L'identifiant de l'utilisateur

        Returns:
            bool: True si des réservations ont été supprimées, False sinon
        """
        pass

    @abstractmethod
    def booking_exists(self, userid: str, date: str, movieid: str) -> bool:
        """
        Vérifie si une réservation existe.

        Args:
            userid: L'identifiant de l'utilisateur
            date: La date de la réservation
            movieid: L'identifiant du film

        Returns:
            bool: True si la réservation existe, False sinon
        """
        pass