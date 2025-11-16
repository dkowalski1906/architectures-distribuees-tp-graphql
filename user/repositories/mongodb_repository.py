from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from .base_repository import BaseUserRepository

class MongoUserRepository(BaseUserRepository):
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
            self.collection = self.db['users']

            # Création d'index pour optimiser les requêtes
            self.collection.create_index('id', unique=True)
            self.collection.create_index('name')

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

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Récupère tous les utilisateurs"""
        users = list(self.collection.find())
        return [self._document_to_dict(user) for user in users]

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par son ID"""
        user = self.collection.find_one({'id': user_id})
        return self._document_to_dict(user)

    def get_user_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par son nom"""
        user = self.collection.find_one({'name': name})
        return self._document_to_dict(user)

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

        # Insertion dans MongoDB
        self.collection.insert_one(user_data.copy())
        return user_data

    def update_user_name(self, user_id: str, name: str) -> Optional[Dict[str, Any]]:
        """Met à jour le nom d'un utilisateur"""
        result = self.collection.update_one(
            {'id': user_id},
            {'$set': {'name': name}}
        )

        if result.matched_count > 0:
            return self.get_user_by_id(user_id)
        return None

    def delete_user(self, user_id: str) -> bool:
        """Supprime un utilisateur"""
        result = self.collection.delete_one({'id': user_id})
        return result.deleted_count > 0

    def close(self):
        """Ferme la connexion MongoDB"""
        if self.client:
            self.client.close()
            print("✓ Connexion MongoDB fermée")