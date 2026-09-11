def test_create_category(client):
    response = client.post("/api/categories/", json={"name": "Finch", "description": "Finch category"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Finch"
    assert "id" in data

def test_create_bird(client):
    # First create a category
    cat_resp = client.post("/api/categories/", json={"name": "Canary"})
    cat_id = cat_resp.json()["id"]

    bird_data = {
        "ring_id": "C-101",
        "name": "Canary",
        "sex": "male",
        "status": "in_stock",
        "category_id": cat_id
    }
    response = client.post("/api/birds/", json=bird_data)
    assert response.status_code == 200
    data = response.json()
    assert data["ring_id"] == "C-101"
    assert data["status"] == "in_stock"
    assert data["category_id"] == cat_id

def test_create_bird_duplicate_ring_id(client):
    bird_data = {
        "ring_id": "C-102",
        "name": "Canary",
        "sex": "male",
        "status": "in_stock"
    }
    client.post("/api/birds/", json=bird_data)
    response = client.post("/api/birds/", json=bird_data)
    assert response.status_code == 400

def test_get_birds_list(client):
    client.post("/api/birds/", json={"ring_id": "L-1", "name": "Lovebird", "sex": "female", "status": "in_stock"})
    response = client.get("/api/birds/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_bird_by_id(client):
    resp = client.post("/api/birds/", json={"ring_id": "L-2", "name": "Lovebird", "sex": "male", "status": "in_stock"})
    bird_id = resp.json()["id"]

    response = client.get(f"/api/birds/{bird_id}")
    assert response.status_code == 200
    assert response.json()["id"] == bird_id

def test_update_bird(client):
    resp = client.post("/api/birds/", json={"ring_id": "L-3", "name": "Lovebird", "sex": "male", "status": "in_stock"})
    bird_id = resp.json()["id"]

    response = client.put(f"/api/birds/{bird_id}", json={"status": "Paired", "notes": "Updated"})
    assert response.status_code == 200
    assert response.json()["status"] == "Paired"
    assert response.json()["notes"] == "Updated"

def test_delete_bird(client):
    resp = client.post("/api/birds/", json={"ring_id": "L-4", "name": "Lovebird", "sex": "male", "status": "in_stock"})
    bird_id = resp.json()["id"]

    response = client.delete(f"/api/birds/{bird_id}")
    assert response.status_code == 200

    # verify soft delete
    get_resp = client.get(f"/api/birds/{bird_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "deceased"

def test_search_birds(client):
    client.post("/api/birds/", json={"ring_id": "Search-1", "name": "Parrot", "sex": "male", "status": "in_stock"})
    response = client.get("/api/birds/search/?q=Search-1")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["ring_id"] == "Search-1"

def test_filter_birds_by_category(client):
    cat_resp = client.post("/api/categories/", json={"name": "FilterCat"})
    cat_id = cat_resp.json()["id"]
    client.post("/api/birds/", json={"ring_id": "F-1", "name": "Finch", "sex": "male", "status": "in_stock", "category_id": cat_id})
    
    response = client.get(f"/api/birds/?category_id={cat_id}")
    assert response.status_code == 200
    for b in response.json():
        assert b["category_id"] == cat_id

def test_filter_birds_by_status(client):
    client.post("/api/birds/", json={"ring_id": "S-1", "name": "Finch", "sex": "male", "status": "in_stock"})
    
    response = client.get("/api/birds/?status=Available")
    assert response.status_code == 200
    assert all(b["status"] == "in_stock" for b in response.json())

def test_get_bird_siblings(client):
    resp = client.post("/api/birds/", json={"ring_id": "Sib-1", "name": "Finch", "sex": "male", "status": "in_stock"})
    bird_id = resp.json()["id"]
    
    response = client.get(f"/api/birds/{bird_id}/siblings")
    # Might just return [] if logic requires parent relationships
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_upload_bird_photo(client):
    resp = client.post("/api/birds/", json={"ring_id": "Photo-1", "name": "Finch", "sex": "male", "status": "in_stock"})
    bird_id = resp.json()["id"]

    # Mock file upload
    response = client.post(
        f"/api/birds/{bird_id}/photo",
        files={"file": ("photo.jpg", b"fake image bytes", "image/jpeg")}
    )
    assert response.status_code == 200
    assert "photo_url" in response.json()
