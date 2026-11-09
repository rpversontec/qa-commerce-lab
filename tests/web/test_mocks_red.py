"""Lab 6.2 · Dobles de prueba en la red: simular respuestas de la API desde Playwright.

page.route() intercepta las peticiones del navegador y route.fulfill() responde
con datos inventados, sin llegar al servidor. Sirve para probar cómo reacciona
la interfaz ante situaciones difíciles de provocar: errores, listas vacías, datos extremos.
"""
from playwright.sync_api import Page, expect


def test_catalogo_con_error_del_servidor(page: Page):  # ejemplo
    page.route("**/api/products*", lambda route: route.fulfill(
        status=503, json={"detail": "Servicio no disponible"}))

    page.goto("/")

    expect(page.locator("#flash")).to_have_text("Servicio no disponible")


# TODO: agreguen aquí sus pruebas con respuestas simuladas.
