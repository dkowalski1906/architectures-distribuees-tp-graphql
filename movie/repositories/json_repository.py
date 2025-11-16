import json
import uuid
from typing import List, Optional, Dict, Any
from .base_repository import BaseMovieRepository

class JsonMovieRepository(BaseMovieRepository):
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
                self.movies = data.get('movies', [])
        except FileNotFoundError:
            print(f"Fichier {self.json_file} non trouvé. Initialisation avec données vides.")
            self.movies = []

    def _save_data(self):
        """Sauvegarde les données dans le fichier JSON"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump({'movies': self.movies}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def get_all_movies(self) -> List[Dict[str, Any]]:
        """Récupère tous les films"""
        return self.movies

    def get_movie_by_id(self, movie_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un film par son ID"""
        for movie in self.movies:
            if movie.get('id') == movie_id:
                return movie
        return None

    def get_movie_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Récupère un film par son titre"""
        for movie in self.movies:
            if movie.get('title', '').lower() == title.lower():
                return movie
        return None

    def add_movie(self, movie_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ajoute un nouveau film"""
        # Génère un ID si pas fourni
        if 'id' not in movie_data:
            movie_data['id'] = str(uuid.uuid4())

        # Vérifie si le film existe déjà
        if self.get_movie_by_id(movie_data['id']):
            raise ValueError(f"Un film avec l'ID {movie_data['id']} existe déjà")

        self.movies.append(movie_data)
        self._save_data()
        return movie_data

    def update_movie(self, movie_id: str, movie_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un film existant"""
        for i, movie in enumerate(self.movies):
            if movie.get('id') == movie_id:
                # Préserve l'ID
                movie_data['id'] = movie_id
                self.movies[i] = movie_data
                self._save_data()
                return movie_data
        return None

    def delete_movie(self, movie_id: str) -> bool:
        """Supprime un film"""
        for i, movie in enumerate(self.movies):
            if movie.get('id') == movie_id:
                self.movies.pop(i)
                self._save_data()
                return True
        return False

    def get_movies_by_director(self, director: str) -> List[Dict[str, Any]]:
        """Récupère tous les films d'un réalisateur"""
        return [
            movie for movie in self.movies
            if movie.get('director', '').lower() == director.lower()
        ]

    def get_movies_by_rating(self, min_rating: float) -> List[Dict[str, Any]]:
        """Récupère tous les films avec un rating minimum"""
        return [
            movie for movie in self.movies
            if movie.get('rating', 0) >= min_rating
        ]