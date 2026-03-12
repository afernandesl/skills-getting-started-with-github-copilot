from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange – client already configured

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert "index.html" in response.url.path


def test_get_activities_returns_all():
    # Arrange
    expected = activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected


def test_successful_signup_adds_participant():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    activities[activity]["participants"] = [
        e for e in activities[activity]["participants"] if e != email
    ]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity}"


def test_signup_nonexistent_activity_returns_404():
    # Arrange
    activity = "Nonexistent"
    email = "foo@bar.com"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_student_returns_400():
    # Arrange
    activity = "Chess Club"
    email = activities[activity]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_successful_unregister_removes_participant():
    # Arrange
    activity = "Chess Club"
    email = "tobedeleted@mergington.edu"
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]
    assert response.json()["message"] == f"Unregistered {email} from {activity}"


def test_unregister_nonexistent_activity_returns_404():
    # Arrange
    activity = "Nonexistent"
    email = "foo@bar.com"

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_signed_up_returns_400():
    # Arrange
    activity = "Chess Club"
    email = "unknown@mergington.edu"
    activities[activity]["participants"] = [
        e for e in activities[activity]["participants"] if e != email
    ]

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"