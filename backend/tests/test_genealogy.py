def test_ancestry_flat(client):
    gm1 = client.post("/api/birds/", json={"ring_id": "GM1", "sex": "female", "status": "in_stock"}).json()["id"]
    gf1 = client.post("/api/birds/", json={"ring_id": "GF1", "sex": "male", "status": "in_stock"}).json()["id"]
    
    m1 = client.post("/api/birds/", json={"ring_id": "M1", "sex": "female", "status": "in_stock", "father_id": gf1, "mother_id": gm1}).json()["id"]
    f1 = client.post("/api/birds/", json={"ring_id": "F1", "sex": "male", "status": "in_stock"}).json()["id"]

    c1 = client.post("/api/birds/", json={"ring_id": "C1", "sex": "unknown", "status": "in_stock", "father_id": f1, "mother_id": m1}).json()["id"]

    resp = client.get(f"/api/birds/{c1}/ancestry")
    assert resp.status_code == 200
    # verify format

def test_ancestry_tree(client):
    gm1 = client.post("/api/birds/", json={"ring_id": "GM2", "sex": "female", "status": "in_stock"}).json()["id"]
    gf1 = client.post("/api/birds/", json={"ring_id": "GF2", "sex": "male", "status": "in_stock"}).json()["id"]
    m1 = client.post("/api/birds/", json={"ring_id": "M2", "sex": "female", "status": "in_stock", "father_id": gf1, "mother_id": gm1}).json()["id"]
    c1 = client.post("/api/birds/", json={"ring_id": "C2", "sex": "unknown", "status": "in_stock", "mother_id": m1}).json()["id"]

    resp = client.get(f"/api/birds/{c1}/ancestry/tree")
    assert resp.status_code == 200

def test_descendants_flat(client):
    gm1 = client.post("/api/birds/", json={"ring_id": "GM3", "sex": "female", "status": "in_stock"}).json()["id"]
    m1 = client.post("/api/birds/", json={"ring_id": "M3", "sex": "female", "status": "in_stock", "mother_id": gm1}).json()["id"]
    c1 = client.post("/api/birds/", json={"ring_id": "C3", "sex": "unknown", "status": "in_stock", "mother_id": m1}).json()["id"]

    resp = client.get(f"/api/birds/{gm1}/descendants")
    assert resp.status_code == 200
    
def test_deep_generational_lookup(client):
    # 5 generations
    b1 = client.post("/api/birds/", json={"ring_id": "Gen1", "sex": "female", "status": "in_stock"}).json()["id"]
    b2 = client.post("/api/birds/", json={"ring_id": "Gen2", "sex": "female", "status": "in_stock", "mother_id": b1}).json()["id"]
    b3 = client.post("/api/birds/", json={"ring_id": "Gen3", "sex": "female", "status": "in_stock", "mother_id": b2}).json()["id"]
    b4 = client.post("/api/birds/", json={"ring_id": "Gen4", "sex": "female", "status": "in_stock", "mother_id": b3}).json()["id"]
    b5 = client.post("/api/birds/", json={"ring_id": "Gen5", "sex": "female", "status": "in_stock", "mother_id": b4}).json()["id"]

    resp = client.get(f"/api/birds/{b5}/ancestry")
    assert resp.status_code == 200
