def test_create_sale_marks_bird_sold(client):
    b1 = client.post("/api/birds/", json={"ring_id": "Sale-1", "sex": "male", "status": "in_stock"}).json()["id"]
    
    sale_resp = client.post("/api/sales/", json={
        "bird_id": b1,
        "buyer_name": "John Doe",
        "date_sold": "2024-05-01",
        "sale_price": 100.0
    })
    assert sale_resp.status_code == 200
    
    # check bird status
    bird_resp = client.get(f"/api/birds/{b1}")
    assert bird_resp.json()["status"] == "sold"

def test_cannot_sell_already_sold_bird(client):
    b1 = client.post("/api/birds/", json={"ring_id": "Sale-2", "sex": "male", "status": "in_stock"}).json()["id"]
    client.post("/api/sales/", json={"bird_id": b1, "buyer_name": "A", "date_sold": "2024-05-01", "sale_price": 100.0})
    
    sale_resp2 = client.post("/api/sales/", json={"bird_id": b1, "buyer_name": "B", "date_sold": "2024-05-02", "sale_price": 100.0})
    assert sale_resp2.status_code == 400

def test_delete_sale_reverts_bird(client):
    b1 = client.post("/api/birds/", json={"ring_id": "Sale-3", "sex": "male", "status": "in_stock"}).json()["id"]
    sale = client.post("/api/sales/", json={"bird_id": b1, "buyer_name": "A", "date_sold": "2024-05-01", "sale_price": 100.0}).json()["id"]
    
    client.delete(f"/api/sales/{sale}")
    
    bird_resp = client.get(f"/api/birds/{b1}")
    assert bird_resp.json()["status"] == "in_stock"

def test_sales_analytics(client):
    resp = client.get("/api/sales/analytics")
    # Might require year query param, etc
    assert resp.status_code == 200

def test_search_sales(client):
    b1 = client.post("/api/birds/", json={"ring_id": "Sale-4", "sex": "male", "status": "in_stock"}).json()["id"]
    client.post("/api/sales/", json={"bird_id": b1, "buyer_name": "Smith", "date_sold": "2024-05-01", "sale_price": 100.0})

    resp = client.get("/api/sales/search?q=Smith")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["buyer_name"] == "Smith"
