"""Lab 5.2 · Autenticación (HU-01, HU-02)."""
from tests.api.contrato import validar


def test_login_valido(api, contrato):
    res = api.post("/api/auth/login", json={"email": "ana.garcia@example.com", "password": "Password123"})
    assert res.status_code == 200
    validar(contrato, "AuthOut", res.json())


def test_login_contrasena_incorrecta(api):  # CA-02.2
    res = api.post("/api/auth/login", json={"email": "ana.garcia@example.com", "password": "mala1234"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Correo o contraseña incorrectos"


def test_perfil_sin_token(api):
    assert api.get("/api/me").status_code == 401


def test_registro_con_correo_existente(api):  # RN-01
    res = api.post("/api/auth/register", json={
        "name": "Ana", "email": "ana.garcia@example.com", "password": "Password123",
        "password_confirm": "Password123", "birth_date": "1990-01-01"})
    assert res.status_code == 409
    assert "email" in res.json()["errors"]
