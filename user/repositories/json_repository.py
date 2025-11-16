import json
from typing import List, Optional, Dict, Any
from .base_repository import BaseUserRepository

class JsonUserRepository(BaseUserRepository):
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
                self.users = data.get('users', [])
        except FileNotFoundError:
            print(f"Fichier {self.json_file} non trouvé. Initialisation avec données vides.")
            self.users = []

    def _save_data(self):
        """Sauvegarde les données dans le fichier JSON"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump({'users': self.users}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Récupère tous les utilisateurs"""
        return self.users

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par son ID"""
        for user in self.users:
            if str(user.get('id')) == str(user_id):
                return user
        return None

    def get_user_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par son nom"""
        for user in self.users:
            if str(user.get('name')) == str(name):
                return user
        return None

    def is_admin(self, user_id: str) -> bool:
        """Vérifie si un utilisateur est admin"""
        user = self.get_user_by_id(user_id)
        if user:
            return user.get('is_admin', False)
        return False

    def add_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ajoute un nouvel utilisateur"""
        # Vérifie si l'utilisateur existe déjà
        if self.get_user_by_id(user_data.get('id')):
            raise ValueError(f"Un utilisateur avec l'ID {user_data.get('id')} existe déjà")

        self.users.append(user_data)
        self._save_data()
        return user_data

    def update_user_name(self, user_id: str, name: str) -> Optional[Dict[str, Any]]:
        """Met à jour le nom d'un utilisateur"""
        for user in self.users:
            if str(user.get('id')) == str(user_id):
                user['name'] = name
                self._save_data()
                return user
        return None

    def delete_user(self, user_id: str) -> bool:
        """Supprime un utilisateur"""
        for i, user in enumerate(self.users):
            if str(user.get('id')) == str(user_id):
                self.users.pop(i)
                self._save_data()
                return True
        return False