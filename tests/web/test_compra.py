"""Lab 5.1 · Las pruebas heredadas, refactorizadas con Page Objects.

Verifican lo mismo que tests/web/legacy/test_compra_legacy.py, pero:
sin esperas fijas, con localizadores accesibles, sin código duplicado y con aserciones web-first.
"""
import pytest
from playwright.sync_api import Page, expect

from tests.web.pages.paginas import CarritoPage, CheckoutPage, LoginPage, ProductoPage


@pytest.fixture
def ana(page: Page) -> Page:
    LoginPage(page).abrir().iniciar_sesion("ana.garcia@example.com", "Password123")
    expect(page.locator("#user-name")).to_have_text("Ana García")
    return page


def test_compra_completa(ana: Page):
    ProductoPage(ana).abrir(4).agregar(2)
    carrito = CarritoPage(ana).abrir()
    expect(carrito.total).to_have_text("$2,598.00")

    pago = carrito.ir_al_checkout().enviar_direccion()
    pago.pagar("4111 1111 1111 1111")

    expect(pago.confirmacion).to_contain_text("Gracias")
    expect(pago.ultimos4).to_have_text("1111")


def test_compra_con_tarjeta_rechazada(ana: Page):
    ProductoPage(ana).abrir(4).agregar(1)
    pago = CheckoutPage(ana).abrir().enviar_direccion()
    pago.pagar("4000 0000 0000 0002")

    expect(pago.error).to_have_text("Pago rechazado. Verifica tus datos o usa otra tarjeta.")


def test_cupon_bienvenida_en_carrito(ana: Page):
    ProductoPage(ana).abrir(4).agregar(2)
    carrito = CarritoPage(ana).abrir()
    carrito.aplicar_cupon("BIENVENIDA10")

    expect(carrito.descuento).to_have_text("-$259.80")
    expect(carrito.total).to_have_text("$2,338.20")
