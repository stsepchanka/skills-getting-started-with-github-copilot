import urllib.parse

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure activity exists
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    assert activity in activities

    # Ensure email not already present
    participants = activities[activity]["participants"]
    if email in participants:
        # If test rerun without restarting process, remove first to ensure clean start
        encoded_activity = urllib.parse.quote(activity, safe="")
        client.delete(f"/activities/{encoded_activity}/participants?email={urllib.parse.quote(email, safe='')}")

    # Sign up
    encoded_activity = urllib.parse.quote(activity, safe="")
    resp = client.post(f"/activities/{encoded_activity}/signup?email={urllib.parse.quote(email, safe='')}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant present
    resp = client.get("/activities")
    activities = resp.json()
    assert email in activities[activity]["participants"]

    # Signing up again should fail with 400
    resp = client.post(f"/activities/{encoded_activity}/signup?email={urllib.parse.quote(email, safe='')}")
    assert resp.status_code == 400

    # Unregister
    resp = client.delete(f"/activities/{encoded_activity}/participants?email={urllib.parse.quote(email, safe='')}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Verify removed
    resp = client.get("/activities")
    activities = resp.json()
    assert email not in activities[activity]["participants"]
