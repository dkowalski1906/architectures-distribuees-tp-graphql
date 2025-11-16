from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class BaseScheduleRepository(ABC):
    """
    Interface abstraite pour le repository des horaires.
    Toutes les implémentations (JSON, MongoDB) doivent respecter ce contrat.
    """

    @abstractmethod
    def get_all_schedules(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les horaires.

        Returns:
            List[Dict]: Liste de tous les horaires
        """
        pass

    @abstractmethod
    def get_schedule_by_date(self, date: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un horaire par sa date.

        Args:
            date: La date au format YYYYMMDD

        Returns:
            Dict ou None: L'horaire si trouvé, None sinon
        """
        pass

    @abstractmethod
    def get_dates_by_movie(self, movie_id: str) -> List[str]:
        """
        Récupère toutes les dates où un film est programmé.

        Args:
            movie_id: L'identifiant du film

        Returns:
            List[str]: Liste des dates
        """
        pass

    @abstractmethod
    def add_schedule(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ajoute un nouvel horaire.

        Args:
            schedule_data: Les données de l'horaire à ajouter (date, movies)

        Returns:
            Dict: L'horaire ajouté
        """
        pass

    @abstractmethod
    def add_movies_to_date(self, date: str, movie_ids: List[str]) -> Dict[str, Any]:
        """
        Ajoute des films à une date existante ou crée la date.

        Args:
            date: La date au format YYYYMMDD
            movie_ids: Liste des IDs de films à ajouter

        Returns:
            Dict: L'horaire mis à jour
        """
        pass

    @abstractmethod
    def delete_schedule(self, date: str) -> bool:
        """
        Supprime un horaire complet.

        Args:
            date: La date à supprimer

        Returns:
            bool: True si l'horaire a été supprimé, False sinon
        """
        pass

    @abstractmethod
    def delete_movies_from_date(self, date: str, movie_ids: List[str]) -> bool:
        """
        Supprime des films d'une date.

        Args:
            date: La date
            movie_ids: Liste des IDs de films à supprimer

        Returns:
            bool: True si au moins un film a été supprimé, False sinon
        """
        pass