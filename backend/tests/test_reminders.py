def test_create_reminder(client):
    resp = client.post("/api/reminders/", json={
        "title": "Buy seed",
        "description": "Get more seeds",
        "due_date": "2030-01-01",
         
    })
    assert resp.status_code == 200
    assert resp.json()["title"] == "Buy seed"

def test_get_due_reminders(client):
    resp = client.get("/api/reminders/due")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_mark_reminder_sent(client):
    r_id = client.post("/api/reminders/", json={
        "title": "Medication",
        "due_date": "2030-01-01",
         
    }).json()["id"]

    resp = client.post(f"/api/reminders/{r_id}/mark-sent")
    assert resp.status_code == 200
    assert resp.json()["notification_sent"] == True

def test_update_reminder(client):
    r_id = client.post("/api/reminders/", json={
        "title": "Update me",
        "due_date": "2030-01-01",
         
    }).json()["id"]

    resp = client.put(f"/api/reminders/{r_id}", json={
        "title": "Updated"
    })
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"

def test_delete_reminder(client):
    r_id = client.post("/api/reminders/", json={
        "title": "Delete me",
        "due_date": "2030-01-01",
         
    }).json()["id"]

    resp = client.delete(f"/api/reminders/{r_id}")
    assert resp.status_code == 200
