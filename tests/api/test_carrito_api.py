"""Lab 5.2 · Carrito (HU-06 a HU-09): estado, contrato, reglas y negativos."""
import pytest

from tests.api.contrato import validar


def test_agregar_requiere_sesion(api):  # CA-06.1
    res = api.post("/api/cart/items", json={"product_id": 4, "quantity": 1})
    assert res.status_code == 401


def test_agregar_producto(api_ana):
    res = api_ana.post("/api/cart/items", json={"product_id": 4, "quantity": 2})
    assert res.status_code == 200
    cart = res.json()
    assert cart["item_count"] == 2
    assert cart["subtotal"] == 2598.00          # oráculo: 2 × $1,299.00
    assert cart["shipping"] == 0                # RN-08: subtotal > $999


@pytest.mark.xfail(strict=True, reason="BUG-03: 'discount' llega como string; el contrato dice number")
def test_carrito_cumple_el_contrato(api_ana, contrato):
    res = api_ana.post("/api/cart/items", json={"product_id": 4, "quantity": 1})
    validar(contrato, "CartOut", res.json())


def test_sumar_cantidad_existente(api_ana):  # CA-06.3
    api_ana.post("/api/cart/items", json={"product_id": 4, "quantity": 3})
    cart = api_ana.post("/api/cart/items", json={"product_id": 4, "quantity": 4}).json()
    assert cart["items"][0]["quantity"] == 7


def test_producto_agotado(api_ana):  # CA-03.3
    res = api_ana.post("/api/cart/items", json={"product_id": 6, "quantity": 1})
    assert res.status_code == 409
    assert res.json()["detail"] == "Producto agotado"


def test_mas_unidades_que_el_stock(api_ana):  # RN-05
    res = api_ana.post("/api/cart/items", json={"product_id": 8, "quantity": 5})  # stock 3
    assert res.status_code == 409


def test_cantidad_cero_elimina_el_producto(api_ana):  # CA-07.3
    api_ana.post("/api/cart/items", json={"product_id": 4, "quantity": 2})
    cart = api_ana.patch("/api/cart/items/4", json={"quantity": 0}).json()
    assert cart["items"] == [] and cart["item_count"] == 0


def test_cupon_vencido(api_ana):
    api_ana.post("/api/cart/items", json={"product_id": 4, "quantity": 1})
    res = api_ana.post("/api/cart/coupon", json={"code": "NAVIDAD25"})
    assert res.status_code == 400
    assert res.json()["detail"] == "Cupón no válido"


def test_payload_sin_campos_obligatorios(api_ana):
    assert api_ana.post("/api/cart/items", json={"quantity": 1}).status_code == 422
