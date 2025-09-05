import os
import unittest.mock

import pytest
from redis import ConnectionError, Redis, ResponseError, TimeoutError


def test_redis_connection_with_default_url():
    """Test Redis connection with default URL"""
    with unittest.mock.patch("redis.Redis.from_url") as mock_redis:
        # Given
        mock_redis.return_value = unittest.mock.MagicMock()

        # When
        from page_tracker.app import redis

        # Clear the cache to ensure fresh call
        redis.cache_clear()
        redis_client = redis()

        # Then
        mock_redis.assert_called_once_with("redis://localhost:6379")
        assert redis_client is not None


def test_redis_connection_with_custom_url():
    """Test Redis connection with custom URL from environment"""
    with unittest.mock.patch.dict(os.environ, {"REDIS_URL": "redis://custom:6379"}):
        with unittest.mock.patch("redis.Redis.from_url") as mock_redis:
            # Given
            mock_redis.return_value = unittest.mock.MagicMock()

            # When
            from page_tracker.app import redis

            # Clear the cache to ensure fresh call
            redis.cache_clear()
            redis_client = redis()

            # Then
            mock_redis.assert_called_once_with("redis://custom:6379")
            assert redis_client is not None


def test_redis_connection_caching():
    """Test that Redis connection is cached"""
    with unittest.mock.patch("redis.Redis.from_url") as mock_redis:
        # Given
        mock_redis.return_value = unittest.mock.MagicMock()

        # When - Call redis() multiple times
        from page_tracker.app import redis

        # Clear the cache to ensure fresh call
        redis.cache_clear()
        client1 = redis()
        client2 = redis()
        client3 = redis()

        # Then - Should only create one connection
        assert client1 is client2 is client3
        mock_redis.assert_called_once()


def test_redis_connection_with_invalid_url():
    """Test Redis connection with invalid URL"""
    with unittest.mock.patch.dict(os.environ, {"REDIS_URL": "invalid://url"}):
        with unittest.mock.patch("redis.Redis.from_url") as mock_redis:
            # Given
            mock_redis.side_effect = ValueError("Invalid URL")

            # When
            from page_tracker.app import redis

            # Clear the cache to ensure fresh call
            redis.cache_clear()

            # Then - Should raise the error
            with pytest.raises(ValueError):
                redis()


def test_redis_connection_with_empty_url():
    """Test Redis connection with empty URL"""
    with unittest.mock.patch.dict(os.environ, {"REDIS_URL": ""}):
        with unittest.mock.patch("redis.Redis.from_url") as mock_redis:
            # Given
            mock_redis.return_value = unittest.mock.MagicMock()

            # When
            from page_tracker.app import redis

            # Clear the cache to ensure fresh call
            redis.cache_clear()
            redis_client = redis()

            # Then
            mock_redis.assert_called_once_with("")
            assert redis_client is not None


def test_redis_connection_with_none_url():
    """Test Redis connection with None URL"""
    with unittest.mock.patch.dict(os.environ, {"REDIS_URL": "None"}):
        with unittest.mock.patch("redis.Redis.from_url") as mock_redis:
            # Given
            mock_redis.return_value = unittest.mock.MagicMock()

            # When
            from page_tracker.app import redis

            # Clear the cache to ensure fresh call
            redis.cache_clear()
            redis_client = redis()

            # Then
            mock_redis.assert_called_once_with("None")
            assert redis_client is not None


def test_redis_connection_with_special_characters():
    """Test Redis connection with special characters in URL"""
    special_url = "redis://user:pass@host:6379/0?ssl=true"
    with unittest.mock.patch.dict(os.environ, {"REDIS_URL": special_url}):
        with unittest.mock.patch("redis.Redis.from_url") as mock_redis:
            # Given
            mock_redis.return_value = unittest.mock.MagicMock()

            # When
            from page_tracker.app import redis

            # Clear the cache to ensure fresh call
            redis.cache_clear()
            redis_client = redis()

            # Then
            mock_redis.assert_called_once_with(special_url)
            assert redis_client is not None


def test_redis_connection_with_unicode_url():
    """Test Redis connection with unicode characters in URL"""
    unicode_url = "redis://host:6379/数据库"
    with unittest.mock.patch.dict(os.environ, {"REDIS_URL": unicode_url}):
        with unittest.mock.patch("redis.Redis.from_url") as mock_redis:
            # Given
            mock_redis.return_value = unittest.mock.MagicMock()

            # When
            from page_tracker.app import redis

            # Clear the cache to ensure fresh call
            redis.cache_clear()
            redis_client = redis()

            # Then
            mock_redis.assert_called_once_with(unicode_url)
            assert redis_client is not None


def test_redis_connection_with_very_long_url():
    """Test Redis connection with very long URL"""
    long_url = "redis://" + "a" * 1000 + ":6379"
    with unittest.mock.patch.dict(os.environ, {"REDIS_URL": long_url}):
        with unittest.mock.patch("redis.Redis.from_url") as mock_redis:
            # Given
            mock_redis.return_value = unittest.mock.MagicMock()

            # When
            from page_tracker.app import redis

            # Clear the cache to ensure fresh call
            redis.cache_clear()
            redis_client = redis()

            # Then
            mock_redis.assert_called_once_with(long_url)
            assert redis_client is not None


def test_redis_connection_with_connection_error():
    """Test Redis connection when connection fails"""
    with unittest.mock.patch("redis.Redis.from_url") as mock_redis:
        # Given
        mock_redis.side_effect = ConnectionError("Connection failed")

        # When
        from page_tracker.app import redis

        # Clear the cache to ensure fresh call
        redis.cache_clear()

        # Then - Should raise the error
        with pytest.raises(ConnectionError):
            redis()


def test_redis_connection_with_timeout_error():
    """Test Redis connection when timeout occurs"""
    with unittest.mock.patch("redis.Redis.from_url") as mock_redis:
        # Given
        mock_redis.side_effect = TimeoutError("Connection timeout")

        # When
        from page_tracker.app import redis

        # Clear the cache to ensure fresh call
        redis.cache_clear()

        # Then - Should raise the error
        with pytest.raises(TimeoutError):
            redis()


def test_redis_connection_with_response_error():
    """Test Redis connection when response error occurs"""
    with unittest.mock.patch("redis.Redis.from_url") as mock_redis:
        # Given
        mock_redis.side_effect = ResponseError("Invalid response")

        # When
        from page_tracker.app import redis

        # Clear the cache to ensure fresh call
        redis.cache_clear()

        # Then - Should raise the error
        with pytest.raises(ResponseError):
            redis()


def test_redis_connection_with_generic_exception():
    """Test Redis connection when generic exception occurs"""
    with unittest.mock.patch("redis.Redis.from_url") as mock_redis:
        # Given
        mock_redis.side_effect = Exception("Unexpected error")

        # When
        from page_tracker.app import redis

        # Clear the cache to ensure fresh call
        redis.cache_clear()

        # Then - Should raise the error
        with pytest.raises(Exception):
            redis()


def test_redis_connection_with_none_environment():
    """Test Redis connection when environment variable is None"""
    with unittest.mock.patch.dict(os.environ, {}, clear=True):
        with unittest.mock.patch("redis.Redis.from_url") as mock_redis:
            # Given
            mock_redis.return_value = unittest.mock.MagicMock()

            # When
            from page_tracker.app import redis

            # Clear the cache to ensure fresh call
            redis.cache_clear()
            redis_client = redis()

            # Then - Should use default URL
            mock_redis.assert_called_once_with("redis://localhost:6379")
            assert redis_client is not None


def test_redis_connection_with_multiple_environment_variables():
    """Test Redis connection with multiple environment variables"""
    with unittest.mock.patch.dict(
        os.environ,
        {
            "REDIS_URL": "redis://primary:6379",
            "REDIS_URL_BACKUP": "redis://backup:6379",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
        },
    ):
        with unittest.mock.patch("redis.Redis.from_url") as mock_redis:
            # Given
            mock_redis.return_value = unittest.mock.MagicMock()

            # When
            from page_tracker.app import redis

            # Clear the cache to ensure fresh call
            redis.cache_clear()
            redis_client = redis()

            # Then - Should use REDIS_URL
            mock_redis.assert_called_once_with("redis://primary:6379")
            assert redis_client is not None
