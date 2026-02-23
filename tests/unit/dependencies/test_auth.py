"""
Tests for auth dependency
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from src.api.dependencies.auth import get_current_user_uuid


class TestGetCurrentUserUuid:
    """
    Tests for get_current_user_uuid dependency
    """

    @pytest.mark.asyncio
    async def test_get_current_user_uuid_success(self):
        """Test getting user UUID from valid token successfully"""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid_token"

        with patch('src.api.dependencies.auth.jwt_handler') as mock_jwt_handler:
            mock_jwt_handler.decode_payload.return_value = {"sub": "user-uuid-123"}

            result = await get_current_user_uuid(mock_credentials)

            assert result == "user-uuid-123"
            mock_jwt_handler.decode_payload.assert_called_once_with("valid_token")

    @pytest.mark.asyncio
    async def test_get_current_user_uuid_no_sub_claim(self):
        """Test getting user UUID when token has no sub claim"""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "token_without_sub"

        with patch('src.api.dependencies.auth.jwt_handler') as mock_jwt_handler:
            mock_jwt_handler.decode_payload.return_value = {"other": "data"}

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_uuid(mock_credentials)

            assert exc_info.value.status_code == 401
            assert "Invalid token payload" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_uuid_sub_none(self):
        """Test getting user UUID when sub claim is None"""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "token_with_none_sub"

        with patch('src.api.dependencies.auth.jwt_handler') as mock_jwt_handler:
            mock_jwt_handler.decode_payload.return_value = {"sub": None}

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_uuid(mock_credentials)

            assert exc_info.value.status_code == 401
            assert "Invalid token payload" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_uuid_invalid_token(self):
        """Test getting user UUID when token is invalid"""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid_token"

        with patch('src.api.dependencies.auth.jwt_handler') as mock_jwt_handler:
            mock_jwt_handler.decode_payload.side_effect = Exception("Invalid token")

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_uuid(mock_credentials)

            assert exc_info.value.status_code == 401
            assert "Invalid or expired token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_uuid_expired_token(self):
        """Test getting user UUID when token is expired"""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "expired_token"

        with patch('src.api.dependencies.auth.jwt_handler') as mock_jwt_handler:
            mock_jwt_handler.decode_payload.side_effect = Exception("Token expired")

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_uuid(mock_credentials)

            assert exc_info.value.status_code == 401
            assert "Invalid or expired token" in exc_info.value.detail
            assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
