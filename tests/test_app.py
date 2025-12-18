from fastapi.testclient import TestClient
import copy

from src.app import app, activities

client = TestClient(app)
_original_activities = copy.deepcopy(activities)


def setup_function():
    # reset the in-memory activities before each test
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))


def test_root_redirects_to_static_index():
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers["location"] == "/static/index.html"


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "test_user@example.com"

    # Ensure clean start
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in activities[activity]["participants"]

    # Signing up again should fail
    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400

    # Unregister
    r3 = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert r3.status_code == 200
    assert email not in activities[activity]["participants"]

    # Unregister again should fail
    r4 = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert r4.status_code == 400


def test_activity_not_found_errors():
    r = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert r.status_code == 404

    r2 = client.delete("/activities/NoSuchActivity/unregister", params={"email": "a@b.com"})
    assert r2.status_code == 404
