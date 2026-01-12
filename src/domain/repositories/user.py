"""
Repositories related to user
"""

from abc import ABC, abstractmethod

from domain.entities.user import UserEntity


class IUserRepository(ABC):
    """
    Repository for user
    """

    @abstractmethod
    async def get_by_uuid(self, uuid: str) -> UserEntity:
        """
        Method for get user by uuid

        Args:
            uuid: str

        Returns:
            UserEntity
        """

    @abstractmethod
    async def create(self, user: UserEntity) -> UserEntity:
        """
        Method for create user

        Args:
            user: UserEntity
    
        Returns:
            UserEntity
        """

    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity:
        """
        Method for get user by email

        Args:
            email: str

        Returns:
            UserEntity
        """

    @abstractmethod
    async def update_user(self, user: UserEntity) -> UserEntity:
        """
        Method for update user

        Args:
            user: UserEntity

        Returns:
            UserEntity
        """
