import unittest.mock

import pytest
from redis import (BusyLoadingError, ConnectionError, ResponseError,
                   TimeoutError)

from page_tracker.app import app


@unittest.mock.patch("page_tracker.app.redis")
def test_should_call_redis_incr(mock_redis, http_client):
    # Given
    mock_redis.return_value.incr.return_value = 5

    # When
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert response.text == "🎉 This page has been viewed 5 times! Thanks for visiting!"
    mock_redis.return_value.incr.assert_called_once_with("page_views")


@unittest.mock.patch("page_tracker.app.redis")
def test_should_handle_redis_connection_error(mock_redis, http_client):
    # Given
    mock_redis.return_value.incr.side_effect = ConnectionError

    # When
    response = http_client.get("/")

    # Then
    assert response.status_code == 500
    assert response.text == "Sorry, something went wrong \N{PENSIVE FACE}"


# Edge Case Tests for Redis Errors
@unittest.mock.patch("page_tracker.app.redis")
def test_should_handle_redis_timeout_error(mock_redis, http_client):
    # Given
    mock_redis.return_value.incr.side_effect = TimeoutError

    # When
    response = http_client.get("/")

    # Then
    assert response.status_code == 500
    assert response.text == "Sorry, something went wrong \N{PENSIVE FACE}"


@unittest.mock.patch("page_tracker.app.redis")
def test_should_handle_redis_response_error(mock_redis, http_client):
    # Given
    mock_redis.return_value.incr.side_effect = ResponseError("Invalid command")

    # When
    response = http_client.get("/")

    # Then
    assert response.status_code == 500
    assert response.text == "Sorry, something went wrong \N{PENSIVE FACE}"


@unittest.mock.patch("page_tracker.app.redis")
def test_should_handle_redis_busy_loading_error(mock_redis, http_client):
    # Given
    mock_redis.return_value.incr.side_effect = BusyLoadingError

    # When
    response = http_client.get("/")

    # Then
    assert response.status_code == 500
    assert response.text == "Sorry, something went wrong \N{PENSIVE FACE}"


@unittest.mock.patch("page_tracker.app.redis")
def test_should_handle_redis_generic_exception(mock_redis, http_client):
    # Given
    mock_redis.return_value.incr.side_effect = Exception("Unexpected error")

    # When
    response = http_client.get("/")

    # Then
    assert response.status_code == 500
    # Flask returns HTML error page for unhandled exceptions
    assert "Internal Server Error" in response.text


# Edge Case Tests for Page View Counts
@unittest.mock.patch("page_tracker.app.redis")
def test_should_handle_large_page_view_count(mock_redis, http_client):
    # Given - Test with a very large number
    mock_redis.return_value.incr.return_value = 999999999

    # When
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert (
        response.text
        == "🎉 This page has been viewed 999999999 times! Thanks for visiting!"
    )


@unittest.mock.patch("page_tracker.app.redis")
def test_should_handle_zero_page_view_count(mock_redis, http_client):
    # Given - Test with zero (edge case)
    mock_redis.return_value.incr.return_value = 0

    # When
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert response.text == "🎉 This page has been viewed 0 times! Thanks for visiting!"


@unittest.mock.patch("page_tracker.app.redis")
def test_should_handle_negative_page_view_count(mock_redis, http_client):
    # Given - Test with negative number (edge case)
    mock_redis.return_value.incr.return_value = -1

    # When
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert (
        response.text == "🎉 This page has been viewed -1 times! Thanks for visiting!"
    )


@unittest.mock.patch("page_tracker.app.redis")
def test_should_handle_unicode_in_page_views(mock_redis, http_client):
    # Given - Test with unicode characters in response
    mock_redis.return_value.incr.return_value = 42

    # When
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert "🎉" in response.text
    assert "Thanks for visiting!" in response.text
    assert "42" in response.text


# Edge Case Tests for Redis Operations
@unittest.mock.patch("page_tracker.app.redis")
def test_should_call_redis_with_correct_key(mock_redis, http_client):
    # Given
    mock_redis.return_value.incr.return_value = 1

    # When
    response = http_client.get("/")

    # Then
    mock_redis.return_value.incr.assert_called_once_with("page_views")
    assert response.status_code == 200


@unittest.mock.patch("page_tracker.app.redis")
def test_should_handle_multiple_rapid_requests(mock_redis, http_client):
    # Given - Simulate rapid requests
    mock_redis.return_value.incr.side_effect = [1, 2, 3, 4, 5]

    # When - Make multiple requests
    responses = []
    for _ in range(5):
        response = http_client.get("/")
        responses.append(response)

    # Then
    assert len(responses) == 5
    assert all(r.status_code == 200 for r in responses)
    assert mock_redis.return_value.incr.call_count == 5


@unittest.mock.patch("page_tracker.app.redis")
def test_should_handle_redis_incr_returning_none(mock_redis, http_client):
    # Given - Redis incr returns None (edge case)
    mock_redis.return_value.incr.return_value = None

    # When
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert (
        response.text == "🎉 This page has been viewed None times! Thanks for visiting!"
    )


@unittest.mock.patch("page_tracker.app.redis")
def test_should_handle_redis_incr_returning_string(mock_redis, http_client):
    # Given - Redis incr returns string (edge case)
    mock_redis.return_value.incr.return_value = "123"

    # When
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert (
        response.text == "🎉 This page has been viewed 123 times! Thanks for visiting!"
    )
