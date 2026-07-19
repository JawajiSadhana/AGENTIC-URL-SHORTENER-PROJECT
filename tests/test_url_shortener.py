from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_shorten_returns_url():
    """Test /shorten endpoint returns a short URL"""
    response = client.post("/shorten?url=https://google.com")
    assert response.status_code == 200
    data = response.json()
    assert "short_url" in data
    assert "code" in data
    assert data["short_url"].startswith("http://localhost:8000/")

def test_redirect_increments_clicks():
    """Test redirect works and analytics increments"""
    # 1. Pehle short URL banao
    response = client.post("/shorten?url=https://github.com")
    assert response.status_code == 200
    code = response.json()["code"]
    
    # 2. Redirect hit karo
    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 307  # Redirect status
    
    # 3. Analytics check karo - clicks = 1 hone chahiye
    response = client.get(f"/analytics/{code}")
    assert response.status_code == 200
    data = response.json()
    assert data["clicks"] == 1
    assert data["original"] == "https://github.com"

def test_404_for_invalid_code():
    """Test invalid short code gives 404"""
    response = client.get("/invalidcode123")
    assert response.status_code == 404