from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class BaseMovieRepository(ABC):
    """
    Interface abstraite pour le repository des films.
    Toutes les implémentations (JSON, MongoDB) doivent respecter ce contrat.
    """

    @abstractmethod
    def get_all_movies(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les films.

        Returns:
            List[Dict]: Liste de tous les films
        """
        pass

    @abstractmethod
    def get_movie_by_id(self, movie_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un film par son ID.

        Args:
            movie_id: L'identifiant du film

        Returns:
            Dict ou None: Le film si trouvé, None sinon
        """
        pass

    @abstractmethod
    def get_movie_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un film par son titre.

        Args:
            title: Le titre du film

        Returns:
            Dict ou None: Le film si trouvé, None sinon
        """
        pass

    @abstractmethod
    def add_movie(self, movie_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ajoute un nouveau film.

        Args:
            movie_data: Les données du film à ajouter

        Returns:
            Dict: Le film ajouté avec son ID
        """
        pass

    @abstractmethod
    def update_movie(self, movie_id: str, movie_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Met à jour un film existant.

        Args:
            movie_id: L'identifiant du film
            movie_data: Les nouvelles données du film

        Returns:
            Dict ou None: Le film mis à jour si trouvé, None sinon
        """
        pass

    @abstractmethod
    def delete_movie(self, movie_id: str) -> bool:
        """
        Supprime un film.

        Args:
            movie_id: L'identifiant du film à supprimer

        Returns:
            bool: True si le film a été supprimé, False sinon
        """
        pass

    @abstractmethod
    def get_movies_by_director(self, director: str) -> List[Dict[str, Any]]:
        """
        Récupère tous les films d'un réalisateur.

        Args:
            director: Le nom du réalisateur

        Returns:
            List[Dict]: Liste des films du réalisateur
        """
        pass

    @abstractmethod
    def get_movies_by_rating(self, min_rating: float) -> List[Dict[str, Any]]:
        """
        Récupère tous les films avec un rating minimum.

        Args:
            min_rating: Le rating minimum

        Returns:
            List[Dict]: Liste des films correspondants
        """
        pass