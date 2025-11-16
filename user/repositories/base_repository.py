from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class BaseUserRepository(ABC):
    """
    Interface abstraite pour le repository des utilisateurs.
    Toutes les implémentations (JSON, MongoDB) doivent respecter ce contrat.
    """

    @abstractmethod
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les utilisateurs.

        Returns:
            List[Dict]: Liste de tous les utilisateurs
        """
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un utilisateur par son ID.

        Args:
            user_id: L'identifiant de l'utilisateur

        Returns:
            Dict ou None: L'utilisateur si trouvé, None sinon
        """
        pass

    @abstractmethod
    def get_user_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un utilisateur par son nom.

        Args:
            name: Le nom de l'utilisateur

        Returns:
            Dict ou None: L'utilisateur si trouvé, None sinon
        """
        pass

    @abstractmethod
    def is_admin(self, user_id: str) -> bool:
        """
        Vérifie si un utilisateur est admin.

        Args:
            user_id: L'identifiant de l'utilisateur

        Returns:
            bool: True si admin, False sinon
        """
        pass

    @abstractmethod
    def add_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ajoute un nouvel utilisateur.

        Args:
            user_data: Les données de l'utilisateur à ajouter

        Returns:
            Dict: L'utilisateur ajouté
        """
        pass

    @abstractmethod
    def update_user_name(self, user_id: str, name: str) -> Optional[Dict[str, Any]]:
        """
        Met à jour le nom d'un utilisateur.

        Args:
            user_id: L'identifiant de l'utilisateur
            name: Le nouveau nom

        Returns:
            Dict ou None: L'utilisateur mis à jour si trouvé, None sinon
        """
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        """
        Supprime un utilisateur.

        Args:
            user_id: L'identifiant de l'utilisateur à supprimer

        Returns:
            bool: True si l'utilisateur a été supprimé, False sinon
        """
        pass