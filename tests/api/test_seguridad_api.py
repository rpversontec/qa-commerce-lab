"""Lab 6.1 · Pruebas negativas y de seguridad de la API.

Fixtures: api (sin sesión), api_ana (Ana García), api_luis (Luis Pérez).
Recuerden: la orden 1 pertenece a Luis Pérez (datos base).

Ideas (OWASP API Top 10 2023):
  - API1 BOLA: ¿Ana puede ver, pagar o cancelar una orden de Luis cambiando el ID?
  - API2 Autenticación: token inválido, sin token, mensajes de error del login
  - Mensajes de error: ¿revelan datos personales? (RNF-04, CWE-209)
  - Entradas inválidas: tipos incorrectos, campos faltantes, valores fuera de rango
"""
import pytest

DIRECCION_ANA = {
    "street": "Calle Roble 15", "neighborhood": "Del Valle", "city": "Monterrey",
    "state": "Nuevo León", "postal_code": "64000", "phone": "8187654321",
}


def test_token_invalido(api):  # ejemplo
    api.session.headers["Authorization"] = "Bearer token-inventado"
    res = api.get("/api/cart")
    assert res.status_code == 401


def test_sin_token(api):  # API2
    assert api.get("/api/orders").status_code == 401


def test_token_de_sesion_cerrada(api_ana):  # API2: el token se invalida al salir
    assert api_ana.post("/api/auth/logout").status_code == 204
    assert api_ana.get("/api/cart").status_code == 401


# ---------- API1 BOLA: acceso a recursos de otro usuario ----------

def test_luis_ve_su_orden(api_luis):  # control: el recurso existe y es de Luis
    res = api_luis.get("/api/orders/1")
    assert res.status_code == 200
    assert res.json()["address"]["phone"] == "8112345678"


@pytest.mark.xfail(strict=True, reason="BUG: Ana ve la orden 1 de Luis, con su dirección y teléfono (BOLA)")
def test_no_puede_ver_orden_ajena(api_ana):  # CA-12.5
    assert api_ana.get("/api/orders/1").status_code == 404


def test_orden_ajena_no_aparece_en_el_historial(api_ana):
    assert all(o["id"] != 1 for o in api_ana.get("/api/orders").json())


def test_no_puede_cancelar_orden_ajena(api_ana):
    assert api_ana.post("/api/orders/1/cancel").status_code == 404


def test_no_puede_pagar_orden_ajena(api_ana):
    res = api_ana.post("/api/orders/1/pay", json={
        "card_holder": "Ana García", "card_number": "4111111111111111", "expiry": "12/30", "cvv": "123"})
    assert res.status_code == 404


# ---------- Mensajes de error ----------

@pytest.mark.xfail(strict=True, reason="BUG: el login responde 404 si el correo no existe y 401 si sí (enumeración)")
def test_login_no_revela_si_el_correo_existe(api):  # CA-02.2
    existe = api.post("/api/auth/login", json={"email": "luis.perez@example.com", "password": "mala1234"})
    no_existe = api.post("/api/auth/login", json={"email": "nadie@example.com", "password": "mala1234"})
    assert existe.status_code == no_existe.status_code == 401
    assert existe.json() == no_existe.json()


@pytest.mark.xfail(strict=True, reason="BUG: el error del C.P. incluye el nombre y el teléfono del cliente (RNF-04)")
def test_error_de_direccion_sin_datos_personales(api_ana):  # RNF-04, CWE-209
    api_ana.post("/api/cart/items", json={"product_id": 4, "quantity": 1})
    res = api_ana.post("/api/orders", json={"address": {**DIRECCION_ANA, "postal_code": "640"}})
    assert res.status_code == 400
    assert "postal_code" in res.json()["errors"]
    detalle = res.json()["detail"]
    assert "Ana" not in detalle and DIRECCION_ANA["phone"] not in detalle


# ---------- Entradas inválidas ----------

@pytest.mark.parametrize("payload", [
    {"product_id": "cuatro", "quantity": 1},
    {"product_id": 4, "quantity": "dos"},
    {"product_id": None, "quantity": 1},
])
def test_tipos_incorrectos(api_ana, payload):
    assert api_ana.post("/api/cart/items", json=payload).status_code == 422


@pytest.mark.parametrize("cantidad", [
    -1, 0,
    pytest.param(11, marks=pytest.mark.xfail(strict=True, reason="BUG: la API acepta 11 unidades (off-by-one)")),
])
def test_cantidad_fuera_de_rango(api_ana, cantidad):  # RN-05: entre 1 y 10
    res = api_ana.post("/api/cart/items", json={"product_id": 4, "quantity": cantidad})
    assert res.status_code == 400
    assert res.json()["detail"] == "La cantidad debe estar entre 1 y 10"


def test_producto_inexistente(api_ana):
    assert api_ana.post("/api/cart/items", json={"product_id": 9999, "quantity": 1}).status_code == 404


def test_cuerpo_que_no_es_json(api_ana):
    res = api_ana.post("/api/cart/items", data="no soy json", headers={"Content-Type": "application/json"})
    assert res.status_code == 422


# ---------- Desafío: un negativo no deja efectos ----------

def test_cancelar_orden_ajena_no_la_modifica(api_ana, api_luis):
    api_ana.post("/api/orders/1/cancel")
    assert api_luis.get("/api/orders/1").json()["status"] == "Pagada"


def test_cantidad_invalida_no_cambia_el_carrito(api_ana):
    api_ana.post("/api/cart/items", json={"product_id": 4, "quantity": 2})
    api_ana.post("/api/cart/items", json={"product_id": 4, "quantity": -1})
    cart = api_ana.get("/api/cart").json()
    assert cart["items"][0]["quantity"] == 2 and cart["item_count"] == 2
