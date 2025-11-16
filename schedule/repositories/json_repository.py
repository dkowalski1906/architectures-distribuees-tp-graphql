import json
from typing import List, Optional, Dict, Any
from .base_repository import BaseScheduleRepository

class JsonScheduleRepository(BaseScheduleRepository):
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
                self.schedules = data.get('schedule', [])
        except FileNotFoundError:
            print(f"Fichier {self.json_file} non trouvé. Initialisation avec données vides.")
            self.schedules = []

    def _save_data(self):
        """Sauvegarde les données dans le fichier JSON"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump({'schedule': self.schedules}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def get_all_schedules(self) -> List[Dict[str, Any]]:
        """Récupère tous les horaires"""
        return self.schedules

    def get_schedule_by_date(self, date: str) -> Optional[Dict[str, Any]]:
        """Récupère un horaire par sa date"""
        for schedule in self.schedules:
            if str(schedule.get('date')) == str(date):
                return schedule
        return None

    def get_dates_by_movie(self, movie_id: str) -> List[str]:
        """Récupère toutes les dates où un film est programmé"""
        dates = []
        for schedule in self.schedules:
            if movie_id in schedule.get('movies', []):
                dates.append(schedule['date'])
        return dates

    def add_schedule(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ajoute un nouvel horaire"""
        date = schedule_data.get('date')

        # Vérifie si la date existe déjà
        if self.get_schedule_by_date(date):
            raise ValueError(f"Un horaire pour la date {date} existe déjà")

        self.schedules.append(schedule_data)
        self._save_data()
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

            # Ajoute les nouveaux films
            schedule['movies'].extend(movie_ids)
        else:
            # Crée une nouvelle entrée
            schedule = {
                'date': date,
                'movies': list(movie_ids)
            }
            self.schedules.append(schedule)

        self._save_data()
        return schedule

    def delete_schedule(self, date: str) -> bool:
        """Supprime un horaire complet"""
        for i, schedule in enumerate(self.schedules):
            if str(schedule.get('date')) == str(date):
                self.schedules.pop(i)
                self._save_data()
                return True
        return False

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

        # Supprime les films
        schedule['movies'] = list(existing_movies - found_movies)
        self._save_data()
        return True