"""Lab 6.2 · Dobles de prueba en la red: simular respuestas de la API desde Playwright.

page.route() intercepta las peticiones del navegador y route.fulfill() responde
con datos inventados, sin llegar al servidor. Sirve para probar cómo reacciona
la interfaz ante situaciones difíciles de provocar: errores, listas vacías, datos extremos.
"""
import re

import requests
from playwright.sync_api import Page, expect

from tests.api.contrato import validar
from tests.web.conftest import iniciar_sesion

AGOTADO = {"id": 1, "name": "Producto de prueba", "description": "Simulado", "price": 10.0,
           "category": "Computación", "category_id": 1, "stock": 0, "available": False,
           "low_stock": False, "image": "/static/img/placeholder.svg"}
PAGINA_AGOTADO = {"items": [AGOTADO], "total": 1, "page": 1, "page_size": 12}


def test_catalogo_con_error_del_servidor(page: Page):  # ejemplo
    page.route("**/api/products*", lambda route: route.fulfill(
        status=503, json={"detail": "Servicio no disponible"}))

    page.goto("/")

    expect(page.locator("#flash")).to_have_text("Servicio no disponible")


def test_catalogo_vacio(page: Page):
    page.route("**/api/products*", lambda route: route.fulfill(
        json={"items": [], "total": 0, "page": 1, "page_size": 12}))

    page.goto("/")

    expect(page.locator("#results-info")).to_have_text("No encontramos productos para tu búsqueda")
    expect(page.get_by_test_id("product-card")).to_have_count(0)
    expect(page.locator("#page-info")).to_have_text("Página 1 de 1")


def test_producto_agotado_deshabilita_el_boton(page: Page):
    page.route("**/api/products*", lambda route: route.fulfill(json=PAGINA_AGOTADO))

    page.goto("/")

    tarjeta = page.get_by_test_id("product-card")
    expect(tarjeta.get_by_text("Agotado")).to_be_visible()
    expect(tarjeta.get_by_role("button")).to_be_disabled()


def test_agregar_con_sesion_vencida(page: Page):
    iniciar_sesion(page, "ana.garcia@example.com", "Password123")
    page.route("**/api/cart/items", lambda route: route.fulfill(
        status=401, json={"detail": "Tu sesión expiró"}))

    page.get_by_role("button", name="Agregar Teclado Mecánico Kappa al carrito").click()

    expect(page).to_have_url(re.compile(r"/login\?next=%2F$"))
    expect(page.locator("#flash")).to_have_text("Tu sesión expiró")


def test_el_mock_cumple_el_contrato(servidor):  # desafío: el doble no debe divergir del servicio real
    contrato = requests.get(f"{servidor}/openapi.json", timeout=10).json()
    validar(contrato, "ProductPage", PAGINA_AGOTADO)
