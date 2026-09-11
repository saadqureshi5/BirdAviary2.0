def test_create_soft_food_log(client):
    resp = client.post("/api/soft-food/", json={
        "year": 2024,
        "season": "Spring",
        "recipe_name": "Mix 1",
        "ingredients": "Eggs, carrot"
    })
    assert resp.status_code == 200
    assert resp.json()["ingredients"] == "Eggs, carrot"

def test_filter_by_year_season(client):
    client.post("/api/soft-food/", json={"year": 2024, "season": "Spring", "recipe_name": "Mix 1", "ingredients": "Eggs"})
    client.post("/api/soft-food/", json={"year": 2024, "season": "Winter", "recipe_name": "Mix 2", "ingredients": "Carrots"})

    resp = client.get("/api/soft-food/?year=2024")
    assert resp.status_code == 200
    # Additional params like season might be supported

def test_update_soft_food_log(client):
    s_id = client.post("/api/soft-food/", json={"year": 2024, "season": "Spring", "recipe_name": "Mix", "ingredients": "Eggs"}).json()["id"]

    resp = client.put(f"/api/soft-food/{s_id}", json={"recipe_name": "Updated Test"})
    assert resp.status_code == 200
    assert resp.json()["recipe_name"] == "Updated Test"

def test_delete_soft_food_log(client):
    s_id = client.post("/api/soft-food/", json={"year": 2024, "season": "Spring", "recipe_name": "Mix", "ingredients": "Eggs"}).json()["id"]

    resp = client.delete(f"/api/soft-food/{s_id}")
    assert resp.status_code == 200
