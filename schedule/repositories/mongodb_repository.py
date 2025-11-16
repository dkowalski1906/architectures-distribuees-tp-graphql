from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from .base_repository import BaseScheduleRepository

class MongoScheduleRepository(BaseScheduleRepository):
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
            self.collection = self.db['schedules']

            # Création d'index pour optimiser les requêtes
            self.collection.create_index('date', unique=True)

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

    def get_all_schedules(self) -> List[Dict[str, Any]]:
        """Récupère tous les horaires"""
        schedules = list(self.collection.find())
        return [self._document_to_dict(schedule) for schedule in schedules]

    def get_schedule_by_date(self, date: str) -> Optional[Dict[str, Any]]:
        """Récupère un horaire par sa date"""
        schedule = self.collection.find_one({'date': date})
        return self._document_to_dict(schedule)

    def get_dates_by_movie(self, movie_id: str) -> List[str]:
        """Récupère toutes les dates où un film est programmé"""
        schedules = list(self.collection.find({'movies': movie_id}))
        return [schedule['date'] for schedule in schedules]

    def add_schedule(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ajoute un nouvel horaire"""
        date = schedule_data.get('date')

        # Vérifie si la date existe déjà
        if self.get_schedule_by_date(date):
            raise ValueError(f"Un horaire pour la date {date} existe déjà")

        # Insertion dans MongoDB
        self.collection.insert_one(schedule_data.copy())
        return schedule_data

    def add_movies_to_date(self, date: str, movie_ids: List[str]) -> Dict[str, Any]:
        """Ajoute des films à une date existante ou crée la date"""
        schedule = self.get_schedule_by_date(date)

        if schedule:
            # Vérifie les doublons
            existing_movies = set(schedule['movies'])
            duplicates = [mid for mid in movie_ids if mid in existing_movies]

            if duplicates:
                raise ValueError(f"Films déjà programmés : {duplicates}")

            # Ajoute les nouveaux films avec $addToSet (évite les doublons)
            self.collection.update_one(
                {'date': date},
                {'$push': {'movies': {'$each': movie_ids}}}
            )

            return self.get_schedule_by_date(date)
        else:
            # Crée une nouvelle entrée
            schedule_data = {
                'date': date,
                'movies': list(movie_ids)
            }
            self.collection.insert_one(schedule_data.copy())
            return schedule_data

    def delete_schedule(self, date: str) -> bool:
        """Supprime un horaire complet"""
        result = self.collection.delete_one({'date': date})
        return result.deleted_count > 0

    def delete_movies_from_date(self, date: str, movie_ids: List[str]) -> bool:
        """Supprime des films d'une date"""
        schedule = self.get_schedule_by_date(date)

        if not schedule:
            return False

        existing_movies = set(schedule['movies'])
        movies_to_remove = set(movie_ids)
        found_movies = movies_to_remove & existing_movies

        if not found_movies:
            raise ValueError("Aucun des films spécifiés n'est trouvé à cette date")

        # Supprime les films avec $pull
        self.collection.update_one(
            {'date': date},
            {'$pull': {'movies': {'$in': movie_ids}}}
        )

        return True

    def close(self):
        """Ferme la connexion MongoDB"""
        if self.client:
            self.client.close()
            print("✓ Connexion MongoDB fermée")