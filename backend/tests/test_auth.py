def test_register_user(client):
    response = client.post("/api/auth/register", json={
        "username": "javier",
        "password": "testpass123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "javier"
    assert "id" in data
    assert "password" not in data


def test_register_duplicate_user(client):
    client.post("/api/auth/register", json={
        "username": "javier",
        "password": "testpass123",
    })
    response = client.post("/api/auth/register", json={
        "username": "javier",
        "password": "testpass123",
    })
    assert response.status_code == 400


def test_login(client):
    client.post("/api/auth/register", json={
        "username": "javier",
        "password": "testpass123",
    })
    response = client.post("/api/auth/login", data={
        "username": "javier",
        "password": "testpass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "username": "javier",
        "password": "testpass123",
    })
    response = client.post("/api/auth/login", data={
        "username": "javier",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_get_current_user(client):
    client.post("/api/auth/register", json={
        "username": "javier",
        "password": "testpass123",
    })
    login = client.post("/api/auth/login", data={
        "username": "javier",
        "password": "testpass123",
    })
    token = login.json()["access_token"]
    response = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}",
    })
    assert response.status_code == 200
    assert response.json()["username"] == "javier"
