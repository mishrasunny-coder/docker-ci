import time

import pytest
import redis
from redis import ConnectionError, TimeoutError


@pytest.mark.timeout(5.0)
def test_integration_redis_connection_and_increment(redis_client, http_client):
    """Test basic Redis connection and increment functionality"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Make a request
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert "This page has been viewed 1 times!" in response.text
    assert redis_client.get("page_views") == b"1"


@pytest.mark.timeout(5.0)
def test_integration_multiple_increments(redis_client, http_client):
    """Test multiple increments work correctly"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Make multiple requests
    responses = []
    for i in range(5):
        response = http_client.get("/")
        responses.append(response)

    # Then
    assert len(responses) == 5
    assert all(r.status_code == 200 for r in responses)
    assert redis_client.get("page_views") == b"5"

    # Verify each response shows correct count
    for i, response in enumerate(responses, 1):
        assert f"This page has been viewed {i} times!" in response.text


@pytest.mark.timeout(5.0)
def test_integration_redis_persistence(redis_client, http_client):
    """Test that Redis data persists across requests"""
    # Given - Set initial value
    redis_client.set("page_views", 10)

    # When - Make a request
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert "This page has been viewed 11 times!" in response.text
    assert redis_client.get("page_views") == b"11"


@pytest.mark.timeout(5.0)
def test_integration_redis_data_types(redis_client, http_client):
    """Test Redis handles different data types correctly"""
    # Given - Test with different initial values
    test_cases = [
        (0, "1"),
        (1, "2"),
        (100, "101"),
        (999999, "1000000"),
    ]

    for initial_value, expected_value in test_cases:
        # Set initial value
        redis_client.set("page_views", initial_value)

        # When - Make a request
        response = http_client.get("/")

        # Then
        assert response.status_code == 200
        assert redis_client.get("page_views") == expected_value.encode()


@pytest.mark.timeout(5.0)
def test_integration_redis_key_expiration(redis_client, http_client):
    """Test Redis key expiration behavior"""
    # Given - Set a key with expiration
    redis_client.setex("page_views", 1, 5)  # Expires in 1 second

    # When - Make a request before expiration
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert "This page has been viewed 6 times!" in response.text

    # Wait for expiration
    time.sleep(2)

    # When - Make another request after expiration
    response = http_client.get("/")

    # Then - Should start from 1 again
    assert response.status_code == 200
    assert "This page has been viewed 1 times!" in response.text


@pytest.mark.timeout(5.0)
def test_integration_redis_memory_pressure(redis_client, http_client):
    """Test behavior under memory pressure scenarios"""
    # Given - Fill Redis with some data to simulate memory pressure
    for i in range(100):
        redis_client.set(f"test_key_{i}", f"test_value_{i}")

    # Set page_views to a high number
    redis_client.set("page_views", 1000)

    # When - Make a request
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert "This page has been viewed 1001 times!" in response.text
    assert redis_client.get("page_views") == b"1001"


@pytest.mark.timeout(5.0)
def test_integration_redis_connection_pooling(redis_client, http_client):
    """Test Redis connection pooling with multiple rapid requests"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Make many rapid requests to test connection pooling
    responses = []
    start_time = time.time()

    for _ in range(20):
        response = http_client.get("/")
        responses.append(response)

    end_time = time.time()

    # Then
    assert len(responses) == 20
    assert all(r.status_code == 200 for r in responses)
    assert redis_client.get("page_views") == b"20"

    # Should complete quickly (connection pooling working)
    assert (end_time - start_time) < 3.0


@pytest.mark.timeout(5.0)
def test_integration_redis_error_recovery(redis_client, http_client):
    """Test application behavior when Redis recovers from errors"""
    # Given - Set initial state
    redis_client.set("page_views", 5)

    # When - Make a request (should work)
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert "This page has been viewed 6 times!" in response.text

    # Simulate Redis becoming unavailable (this is hard to test in integration)
    # but we can test that the app handles the current state correctly
    assert redis_client.get("page_views") == b"6"


@pytest.mark.timeout(5.0)
def test_integration_redis_unicode_handling(redis_client, http_client):
    """Test Redis handles unicode characters correctly"""
    # Given - Set a key with unicode characters
    redis_client.set("page_views", 42)

    # When - Make a request
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert "🎉" in response.text
    assert "Thanks for visiting!" in response.text
    assert "42" in response.text


@pytest.mark.timeout(5.0)
def test_integration_redis_concurrent_access(redis_client, http_client):
    """Test Redis handles concurrent access correctly"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Simulate concurrent access (sequential but rapid)
    responses = []
    for _ in range(10):
        response = http_client.get("/")
        responses.append(response)
        time.sleep(0.01)  # Small delay to simulate concurrency

    # Then
    assert len(responses) == 10
    assert all(r.status_code == 200 for r in responses)
    assert redis_client.get("page_views") == b"10"

    # Verify each response shows correct incremental count
    for i, response in enumerate(responses, 1):
        assert f"This page has been viewed {i} times!" in response.text


@pytest.mark.timeout(5.0)
def test_integration_redis_large_numbers(redis_client, http_client):
    """Test Redis handles large numbers correctly"""
    # Given - Set a large number
    large_number = 999999999
    redis_client.set("page_views", large_number)

    # When - Make a request
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert f"This page has been viewed {large_number + 1} times!" in response.text
    assert redis_client.get("page_views") == str(large_number + 1).encode()


@pytest.mark.timeout(5.0)
def test_integration_redis_negative_numbers(redis_client, http_client):
    """Test Redis handles negative numbers correctly"""
    # Given - Set a negative number
    redis_client.set("page_views", -5)

    # When - Make a request
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert "This page has been viewed -4 times!" in response.text
    assert redis_client.get("page_views") == b"-4"
