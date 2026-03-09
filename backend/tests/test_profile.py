def _register_and_login(client):
    client.post("/api/auth/register", json={
        "username": "javier", "password": "testpass123",
    })
    resp = client.post("/api/auth/login", data={
        "username": "javier", "password": "testpass123",
    })
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_profile(client):
    token = _register_and_login(client)
    response = client.post("/api/profile", json={
        "skill_level": "intermediate",
        "health_conditions": ["lupus", "renal"],
        "health_goals": ["anti-inflammatory", "kidney-friendly"],
        "dietary_restrictions": ["low-sodium", "low-potassium"],
    }, headers=_auth(token))
    assert response.status_code == 201
    data = response.json()
    assert data["skill_level"] == "intermediate"
    assert "lupus" in data["health_conditions"]


def test_get_profile(client):
    token = _register_and_login(client)
    client.post("/api/profile", json={
        "skill_level": "intermediate",
        "health_conditions": ["lupus"],
        "health_goals": ["anti-inflammatory"],
        "dietary_restrictions": ["low-sodium"],
    }, headers=_auth(token))
    response = client.get("/api/profile", headers=_auth(token))
    assert response.status_code == 200
    assert response.json()["skill_level"] == "intermediate"


def test_update_profile(client):
    token = _register_and_login(client)
    client.post("/api/profile", json={
        "skill_level": "intermediate",
        "health_conditions": ["lupus"],
        "health_goals": ["anti-inflammatory"],
        "dietary_restrictions": ["low-sodium"],
    }, headers=_auth(token))
    response = client.put("/api/profile", json={
        "skill_level": "advanced",
        "health_conditions": ["lupus", "renal"],
        "health_goals": ["anti-inflammatory", "kidney-friendly"],
        "dietary_restrictions": ["low-sodium", "low-potassium"],
    }, headers=_auth(token))
    assert response.status_code == 200
    assert response.json()["skill_level"] == "advanced"


def test_get_profile_not_found(client):
    token = _register_and_login(client)
    response = client.get("/api/profile", headers=_auth(token))
    assert response.status_code == 404
