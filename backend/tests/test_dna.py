def test_upload_dna_record(client):
    b1 = client.post("/api/birds/", json={"ring_id": "DNA-1", "sex": "unknown", "status": "in_stock"}).json()["id"]
    
    resp = client.post(
        "/api/dna/",
        data={"bird_id": str(b1), "file_type": "image"},
        files={"file": ("cert.jpg", b"fake file", "image/jpeg")}
    )
    assert resp.status_code == 200, f"Upload failed: {resp.json()}"
    # Verify record was created by fetching it back
    records = client.get(f"/api/dna/bird/{b1}").json()
    assert len(records) >= 1

def test_get_dna_for_bird(client):
    b1 = client.post("/api/birds/", json={"ring_id": "DNA-2", "sex": "unknown", "status": "in_stock"}).json()["id"]
    client.post(
        "/api/dna/",
        data={"bird_id": str(b1), "file_type": "image"},
        files={"file": ("cert2.jpg", b"fake file", "image/jpeg")}
    )

    resp = client.get(f"/api/dna/bird/{b1}")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1

def test_delete_dna_record(client):
    b1 = client.post("/api/birds/", json={"ring_id": "DNA-3", "sex": "unknown", "status": "in_stock"}).json()["id"]
    client.post(
        "/api/dna/",
        data={"bird_id": str(b1), "file_type": "image"},
        files={"file": ("cert3.jpg", b"fake file", "image/jpeg")}
    )
    # Get the DNA record ID from the list endpoint
    records = client.get(f"/api/dna/bird/{b1}").json()
    assert len(records) >= 1
    dna_id = records[0]["id"]

    del_resp = client.delete(f"/api/dna/{dna_id}")
    assert del_resp.status_code == 200

    # Verify it's gone
    records_after = client.get(f"/api/dna/bird/{b1}").json()
    assert len(records_after) == 0
