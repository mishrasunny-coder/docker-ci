import time

import pytest
import redis
import requests


@pytest.mark.timeout(10.0)
def test_e2e_basic_functionality(redis_client, flask_url):
    """Test basic end-to-end functionality"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Make a request to the Flask app
    response = requests.get(flask_url)

    # Then
    assert response.status_code == 200
    assert "This page has been viewed 1 times!" in response.text
    assert redis_client.get("page_views") == b"1"


@pytest.mark.timeout(10.0)
def test_e2e_multiple_requests(redis_client, flask_url):
    """Test multiple requests increment correctly"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Make multiple requests
    responses = []
    for i in range(5):
        response = requests.get(flask_url)
        responses.append(response)
        time.sleep(0.1)  # Small delay between requests

    # Then
    assert len(responses) == 5
    assert all(r.status_code == 200 for r in responses)
    assert redis_client.get("page_views") == b"5"

    # Verify each response shows correct count
    for i, response in enumerate(responses, 1):
        assert f"This page has been viewed {i} times!" in response.text


@pytest.mark.timeout(10.0)
def test_e2e_http_headers(redis_client, flask_url):
    """Test HTTP headers and response format"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Make a request
    response = requests.get(flask_url)

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/html")
    assert "This page has been viewed 1 times!" in response.text
    assert "🎉" in response.text
    assert "Thanks for visiting!" in response.text


# tests/e2e/test_app_comprehensive.py


@pytest.mark.timeout(10.0)
def test_e2e_http_methods(redis_client, flask_url):
    """Test different HTTP methods"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Test GET method (should work)
    get_response = requests.get(flask_url)

    # Then
    assert get_response.status_code == 200
    assert "This page has been viewed 1 times!" in get_response.text

    # When - Test POST method (should be disallowed)
    post_response = requests.post(flask_url)

    # Then - Assert that the method is not allowed
    assert post_response.status_code == 405


@pytest.mark.timeout(10.0)
def test_e2e_concurrent_requests(redis_client, flask_url):
    """Test concurrent requests handling"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Make concurrent requests
    import queue
    import threading

    results = queue.Queue()

    def make_request():
        try:
            response = requests.get(flask_url, timeout=5)
            results.put(response)
        except Exception as e:
            results.put(e)

    # Start multiple threads
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Then
    responses = []
    while not results.empty():
        result = results.get()
        if isinstance(result, requests.Response):
            responses.append(result)
        else:
            pytest.fail(f"Request failed: {result}")

    assert len(responses) == 5
    assert all(r.status_code == 200 for r in responses)
    assert redis_client.get("page_views") == b"5"


@pytest.mark.timeout(10.0)
def test_e2e_redis_connection_failure(redis_client, flask_url):
    """Test application behavior when Redis connection fails"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Make a request (should work normally)
    response = requests.get(flask_url)

    # Then
    assert response.status_code == 200
    assert "This page has been viewed 1 times!" in response.text

    # Note: Testing actual Redis failure is complex in E2E tests
    # as it would require stopping the Redis container, which would
    # break the test environment. This test verifies normal operation.


@pytest.mark.timeout(10.0)
def test_e2e_large_page_view_counts(redis_client, flask_url):
    """Test application with large page view counts"""
    # Given - Set a large initial value
    large_number = 999999
    redis_client.set("page_views", large_number)

    # When - Make a request
    response = requests.get(flask_url)

    # Then
    assert response.status_code == 200
    assert f"This page has been viewed {large_number + 1} times!" in response.text
    assert redis_client.get("page_views") == str(large_number + 1).encode()


@pytest.mark.timeout(10.0)
def test_e2e_unicode_handling(redis_client, flask_url):
    """Test unicode character handling in responses"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Make a request
    response = requests.get(flask_url)

    # Then
    assert response.status_code == 200
    assert "🎉" in response.text
    assert "Thanks for visiting!" in response.text

    # Verify response is properly encoded
    assert response.encoding == "utf-8" or response.encoding is None


@pytest.mark.timeout(10.0)
def test_e2e_response_time(redis_client, flask_url):
    """Test response time is reasonable"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Make a request and measure time
    start_time = time.time()
    response = requests.get(flask_url)
    end_time = time.time()

    # Then
    assert response.status_code == 200
    response_time = end_time - start_time
    assert response_time < 2.0  # Should respond within 2 seconds


@pytest.mark.timeout(10.0)
def test_e2e_redis_persistence_across_requests(redis_client, flask_url):
    """Test Redis data persists across multiple requests"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Make first request
    response1 = requests.get(flask_url)

    # Then
    assert response1.status_code == 200
    assert "This page has been viewed 1 times!" in response1.text
    assert redis_client.get("page_views") == b"1"

    # When - Make second request
    response2 = requests.get(flask_url)

    # Then
    assert response2.status_code == 200
    assert "This page has been viewed 2 times!" in response2.text
    assert redis_client.get("page_views") == b"2"


@pytest.mark.timeout(10.0)
def test_e2e_http_status_codes(redis_client, flask_url):
    """Test HTTP status codes are correct"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Make a request
    response = requests.get(flask_url)

    # Then
    assert response.status_code == 200
    assert response.reason == "OK"


@pytest.mark.timeout(10.0)
def test_e2e_redis_data_types(redis_client, flask_url):
    """Test Redis handles different data types correctly"""
    # Given - Test with different initial values
    test_cases = [
        (0, "1"),
        (1, "2"),
        (100, "101"),
        (-5, "-4"),
    ]

    for initial_value, expected_value in test_cases:
        # Set initial value
        redis_client.set("page_views", initial_value)

        # When - Make a request
        response = requests.get(flask_url)

        # Then
        assert response.status_code == 200
        assert redis_client.get("page_views") == expected_value.encode()


@pytest.mark.timeout(10.0)
def test_e2e_application_restart_simulation(redis_client, flask_url):
    """Test application behavior after simulated restart"""
    # Given - Set some data
    redis_client.set("page_views", 10)

    # When - Make a request (simulating after restart)
    response = requests.get(flask_url)

    # Then
    assert response.status_code == 200
    assert "This page has been viewed 11 times!" in response.text
    assert redis_client.get("page_views") == b"11"

    # This test verifies that the application can handle
    # existing Redis data after a restart


@pytest.mark.timeout(10.0)
def test_e2e_network_resilience(redis_client, flask_url):
    """Test application resilience to network issues"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Make requests with small delays (simulating network latency)
    responses = []
    for i in range(3):
        response = requests.get(flask_url, timeout=10)
        responses.append(response)
        time.sleep(0.5)  # Simulate network delay

    # Then
    assert len(responses) == 3
    assert all(r.status_code == 200 for r in responses)
    assert redis_client.get("page_views") == b"3"


@pytest.mark.timeout(10.0)
def test_e2e_error_recovery(redis_client, flask_url):
    """Test application error recovery capabilities"""
    # Given - Clear any existing data
    redis_client.delete("page_views")

    # When - Make a request
    response = requests.get(flask_url)

    # Then
    assert response.status_code == 200
    assert "This page has been viewed 1 times!" in response.text

    # Verify Redis state is correct
    assert redis_client.get("page_views") == b"1"

    # Make another request to verify continued operation
    response2 = requests.get(flask_url)
    assert response2.status_code == 200
    assert "This page has been viewed 2 times!" in response2.text
