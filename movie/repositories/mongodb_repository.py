import uuid
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from .base_repository import BaseMovieRepository

class MongoMovieRepository(BaseMovieRepository):
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
            self.collection = self.db['movies']

            # Création d'index pour optimiser les requêtes
            self.collection.create_index('id', unique=True)
            self.collection.create_index('title')
            self.collection.create_index('director')
            self.collection.create_index('rating')

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

    def get_all_movies(self) -> List[Dict[str, Any]]:
        """Récupère tous les films"""
        movies = list(self.collection.find())
        return [self._document_to_dict(movie) for movie in movies]

    def get_movie_by_id(self, movie_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un film par son ID"""
        movie = self.collection.find_one({'id': movie_id})
        return self._document_to_dict(movie)

    def get_movie_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Récupère un film par son titre (insensible à la casse)"""
        movie = self.collection.find_one(
            {'title': {'$regex': f'^{title}$', '$options': 'i'}}
        )
        return self._document_to_dict(movie)

    def add_movie(self, movie_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ajoute un nouveau film"""
        # Génère un ID si pas fourni
        if 'id' not in movie_data:
            movie_data['id'] = str(uuid.uuid4())

        # Vérifie si le film existe déjà
        if self.get_movie_by_id(movie_data['id']):
            raise ValueError(f"Un film avec l'ID {movie_data['id']} existe déjà")

        # Insertion dans MongoDB
        self.collection.insert_one(movie_data.copy())
        return movie_data

    def update_movie(self, movie_id: str, movie_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un film existant"""
        # Préserve l'ID
        movie_data['id'] = movie_id

        result = self.collection.update_one(
            {'id': movie_id},
            {'$set': movie_data}
        )

        if result.matched_count > 0:
            return movie_data
        return None

    def delete_movie(self, movie_id: str) -> bool:
        """Supprime un film"""
        result = self.collection.delete_one({'id': movie_id})
        return result.deleted_count > 0

    def get_movies_by_director(self, director: str) -> List[Dict[str, Any]]:
        """Récupère tous les films d'un réalisateur (insensible à la casse)"""
        movies = list(self.collection.find(
            {'director': {'$regex': f'^{director}$', '$options': 'i'}}
        ))
        return [self._document_to_dict(movie) for movie in movies]

    def get_movies_by_rating(self, min_rating: float) -> List[Dict[str, Any]]:
        """Récupère tous les films avec un rating minimum"""
        movies = list(self.collection.find({'rating': {'$gte': min_rating}}))
        return [self._document_to_dict(movie) for movie in movies]

    def close(self):
        """Ferme la connexion MongoDB"""
        if self.client:
            self.client.close()
            print("✓ Connexion MongoDB fermée")