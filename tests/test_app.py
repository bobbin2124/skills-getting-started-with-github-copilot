import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture to provide a test client for the FastAPI app."""
    return TestClient(app)


def test_get_activities(client):
    """Test GET /activities endpoint."""
    # Arrange: No specific setup needed as data is in-memory

    # Act: Make the GET request
    response = client.get("/activities")

    # Assert: Check status and response structure
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0  # Should have activities
    # Check structure of one activity
    activity = next(iter(data.values()))
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_successful(client):
    """Test successful signup for an activity."""
    # Arrange: Choose an activity and email
    activity_name = "Chess Club"
    email = "test@example.com"

    # Act: Make the POST request
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check success
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]

    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_same_activity(client):
    """Test signing up the same email for the same activity twice (should fail)."""
    # Arrange: Sign up once first
    activity_name = "Programming Class"
    email = "duplicate@example.com"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Try to sign up again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should fail with 400
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up for this activity" in data["detail"]


def test_signup_multiple_activities(client):
    """Test signing up for multiple activities with same email (should fail)."""
    # Arrange: Sign up for first activity
    activity1 = "Gym Class"
    activity2 = "Basketball Team"
    email = "multi@example.com"
    client.post(f"/activities/{activity1}/signup?email={email}")

    # Act: Try to sign up for second activity
    response = client.post(f"/activities/{activity2}/signup?email={email}")

    # Assert: Should fail with 400
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Students can sign up for only one activity" in data["detail"]


def test_remove_participant_successful(client):
    """Test successful removal of a participant."""
    # Arrange: Add a participant first
    activity_name = "Art Club"
    email = "remove@example.com"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Remove the participant
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert: Check success
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]


def test_remove_nonexistent_participant(client):
    """Test removing a participant that doesn't exist."""
    # Arrange: Activity and email that isn't signed up
    activity_name = "Drama Club"
    email = "nonexistent@example.com"

    # Act: Try to remove
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert: Should return 404 or appropriate error
    assert response.status_code == 404  # Assuming backend returns 404


def test_invalid_activity_signup(client):
    """Test signing up for a non-existent activity."""
    # Arrange: Invalid activity name
    activity_name = "Invalid Activity"
    email = "test@example.com"

    # Act: Make the request
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 404
    assert response.status_code == 404


def test_invalid_activity_remove(client):
    """Test removing from a non-existent activity."""
    # Arrange: Invalid activity name
    activity_name = "Invalid Activity"
    email = "test@example.com"

    # Act: Make the request
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert: Should return 404
    assert response.status_code == 404