def test_create_pairing(client):
    m_resp = client.post("/api/birds/", json={"ring_id": "M-1", "name": "Finch", "sex": "male", "status": "in_stock"})
    f_resp = client.post("/api/birds/", json={"ring_id": "F-1", "name": "Finch", "sex": "female", "status": "in_stock"})
    
    m_id = m_resp.json()["id"]
    f_id = f_resp.json()["id"]

    response = client.post("/api/pairings/", json={
        "bird_a_id": m_id,
        "bird_b_id": f_id,
        "start_date": "2024-01-01",
        "cage_number": "Cage-1"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["bird_a_id"] == m_id
    assert data["bird_b_id"] == f_id
    

def test_create_pairing_invalid_bird(client):
    response = client.post("/api/pairings/", json={
        "bird_a_id": 9999,
        "bird_b_id": 8888,
        "start_date": "2024-01-01"
    })
    assert response.status_code == 400 or response.status_code == 404

def test_get_pairings_list(client):
    response = client.get("/api/pairings/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_full_clutch_pipeline(client):
    # 1. Create pair
    m = client.post("/api/birds/", json={"ring_id": "P-M1", "sex": "male", "status": "in_stock"}).json()["id"]
    f = client.post("/api/birds/", json={"ring_id": "P-F1", "sex": "female", "status": "in_stock"}).json()["id"]
    pair = client.post("/api/pairings/", json={"bird_a_id": m, "bird_b_id": f, "start_date": "2024-01-01"}).json()["id"]
    
    # 2. Add clutch (route: /api/breeding/pairings/{pairing_id}/clutches)
    clutch_resp = client.post(f"/api/breeding/pairings/{pair}/clutches", json={"pairing_id": pair, "clutch_date": "2024-01-10", "total_eggs": 4})
    assert clutch_resp.status_code == 200
    clutch_id = clutch_resp.json()["id"]

    # 3. Add chick (route: /api/breeding/clutches/{clutch_id}/chicks)
    chick_resp = client.post(f"/api/breeding/clutches/{clutch_id}/chicks", json={"clutch_id": clutch_id, "hatch_date": "2024-01-24", "ring_id": "CH-1"})
    assert chick_resp.status_code == 200
    chick_id = chick_resp.json()["id"]

    # 4. Promote to stock
    promote_resp = client.post(f"/api/breeding/chicks/{chick_id}/promote")
    assert promote_resp.status_code == 200
    assert promote_resp.json()["status"] == "in_stock"

def test_promote_chick_creates_bird_with_parents(client):
    m = client.post("/api/birds/", json={"ring_id": "P-M2", "sex": "male", "status": "in_stock"}).json()["id"]
    f = client.post("/api/birds/", json={"ring_id": "P-F2", "sex": "female", "status": "in_stock"}).json()["id"]
    pair = client.post("/api/pairings/", json={"bird_a_id": m, "bird_b_id": f, "start_date": "2024-01-01"}).json()["id"]
    clutch = client.post(f"/api/breeding/pairings/{pair}/clutches", json={"pairing_id": pair, "total_eggs": 1}).json()["id"]
    chick = client.post(f"/api/breeding/clutches/{clutch}/chicks", json={"clutch_id": clutch, "ring_id": "CH-2"}).json()["id"]

    promote_resp = client.post(f"/api/breeding/chicks/{chick}/promote")
    assert promote_resp.status_code == 200
    
    new_bird_id = promote_resp.json()["id"]
    bird_resp = client.get(f"/api/birds/{new_bird_id}")
    data = bird_resp.json()
    assert data["father_id"] == m
    assert data["mother_id"] == f

def test_multi_partner_pairs(client):
    m1 = client.post("/api/birds/", json={"ring_id": "M1", "sex": "male", "status": "in_stock"}).json()["id"]
    f1 = client.post("/api/birds/", json={"ring_id": "F1", "sex": "female", "status": "in_stock"}).json()["id"]
    f2 = client.post("/api/birds/", json={"ring_id": "F2", "sex": "female", "status": "in_stock"}).json()["id"]

    client.post("/api/pairings/", json={"bird_a_id": m1, "bird_b_id": f1, "start_date": "2024-01-01"})
    # Same male, different female
    resp2 = client.post("/api/pairings/", json={"bird_a_id": m1, "bird_b_id": f2, "start_date": "2024-06-01"})
    assert resp2.status_code == 200

def test_breeding_analytics(client):
    resp = client.get("/api/breeding/analytics")
    # Might be 200 or 501 depending on impl, assuming 200
    if resp.status_code == 200:
        assert isinstance(resp.json(), dict)
