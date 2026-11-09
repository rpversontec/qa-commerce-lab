"""Lab 5.2 · Catálogo (HU-03 a HU-05): estado, contrato y reglas de negocio."""
import pytest

from tests.api.contrato import validar


def test_listar_productos(api, contrato):
    res = api.get("/api/products")
    assert res.status_code == 200
    validar(contrato, "ProductPage", res.json())
    assert res.json()["page_size"] == 20
    assert len(res.json()["items"]) == 20


def test_no_lista_productos_inactivos(api):  # CA-03.4
    nombres = [p["name"] for p in api.get("/api/products", params={"page": 1}).json()["items"]]
    nombres += [p["name"] for p in api.get("/api/products", params={"page": 2}).json()["items"]]
    assert "Reproductor MP3 Clásico" not in nombres
    assert len(nombres) == 38


def test_filtrar_por_categoria(api):  # CA-04.2
    datos = api.get("/api/products", params={"category": 2}).json()
    assert datos["total"] > 0
    assert {p["category"] for p in datos["items"]} == {"Audio"}


@pytest.mark.parametrize("orden,inverso", [("price_asc", False), ("price_desc", True)])
def test_ordenar_por_precio(api, orden, inverso):  # CA-04.3
    precios = [p["price"] for p in api.get("/api/products", params={"sort": orden}).json()["items"]]
    assert precios == sorted(precios, reverse=inverso)


def test_detalle_de_producto(api, contrato):  # HU-05
    res = api.get("/api/products/2")
    assert res.status_code == 200
    validar(contrato, "ProductOut", res.json())
    assert res.json()["low_stock"] is True  # 4 unidades: "¡Últimas unidades!" (CA-05.2)


@pytest.mark.parametrize("product_id", [39, 9999])  # 39 es inactivo
def test_producto_inexistente_o_inactivo(api, product_id):
    res = api.get(f"/api/products/{product_id}")
    assert res.status_code == 404
    assert res.json()["detail"] == "Producto no encontrado"


def test_parametro_de_orden_invalido(api):
    assert api.get("/api/products", params={"sort": "nombre"}).status_code == 422
