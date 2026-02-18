"""
Entities related to user
"""

from hashlib import sha256

from dataclasses import dataclass

from .blob import BlobEntity


@dataclass
class UserEntity:
    """
    Entity for user
    """

    nome: str
    email: str
    telefone: str
    ativo: bool
    excluido: bool
    uuid: str
    avatar_blob_id: int | None = None
    avatar: BlobEntity | None = None
    _senha_hash: str | None = None


    def authenticated(self, password: str) -> bool:
        """
        Method for authenticated user

        Args:
            password: str

        Returns:
            bool
        """
        return self._senha_hash == sha256(password.encode()).hexdigest()

    def set_password(self, password: str):
        """
        Method for set password

        Notes:
            This method hash the password for sha256
        """
        self._senha_hash = sha256(password.encode()).hexdigest()

    def get_password_hash(self) -> str:
        """
        Getter for password
        """
        return self._senha_hash
