import pytest


@pytest.mark.timeout(1.5)
def test_app_redis(redis_client, http_client):
    # Given
    redis_client.set("page_views", 4)

    # When
    response = http_client.get("/")

    # Then
    assert response.status_code == 200
    assert response.text == "🎉 This page has been viewed 5 times! Thanks for visiting!"
    assert redis_client.get("page_views") == b"5"
