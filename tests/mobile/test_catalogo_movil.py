"""Lab 6.3 · Solución: login inválido, búsqueda y producto agotado en la app Android."""
import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.mobile.conftest import por_descripcion, por_id

pytestmark = pytest.mark.mobile


def iniciar_sesion(driver, servidor: str, email: str, password: str) -> WebDriverWait:
    espera = WebDriverWait(driver, 20)
    campo = espera.until(EC.presence_of_element_located(por_descripcion("Servidor")))
    campo.clear()
    campo.send_keys(servidor)
    driver.find_element(*por_descripcion("Correo electrónico")).send_keys(email)
    driver.find_element(*por_descripcion("Contraseña")).send_keys(password)
    driver.find_element(*por_descripcion("Entrar")).click()
    return espera


def buscar(driver, espera: WebDriverWait, texto: str) -> list[str]:
    """Busca en el catálogo y devuelve los nombres de los productos que aparecen."""
    info = espera.until(EC.presence_of_element_located(por_id("catalog_info")))
    espera.until(lambda _: info.text.endswith("productos"))
    driver.find_element(*por_descripcion("Buscar producto")).send_keys(texto)
    driver.find_element(*por_descripcion("Buscar")).click()
    espera.until(lambda _: info.text != "38 productos")
    return [e.text for e in driver.find_elements(*por_id("item_name"))]


def test_login_con_contrasena_incorrecta(driver, servidor_movil):  # CA-02.2
    espera = iniciar_sesion(driver, servidor_movil, "ana.garcia@example.com", "mala1234")

    error = driver.find_element(*por_id("login_error"))
    espera.until(lambda _: error.text != "")
    assert error.text == "Correo o contraseña incorrectos"
    assert driver.find_elements(*por_id("catalog_info")) == []


def test_buscar_teclado(driver, servidor_movil):
    espera = iniciar_sesion(driver, servidor_movil, "ana.garcia@example.com", "Password123")

    nombres = buscar(driver, espera, "Teclado")

    assert nombres and all("Teclado" in n for n in nombres)
    assert driver.find_element(*por_id("catalog_info")).text == f"{len(nombres)} productos"


@pytest.mark.xfail(strict=True, reason="BUG: en la app, 'Agregar' sigue habilitado en un producto agotado (CA-03.3)")
def test_producto_agotado_no_se_puede_agregar(driver, servidor_movil):
    espera = iniciar_sesion(driver, servidor_movil, "ana.garcia@example.com", "Password123")

    nombres = buscar(driver, espera, "Disco SSD")

    assert nombres == ["Disco SSD Externo 1 TB"]
    assert driver.find_element(*por_id("item_status")).text == "Agotado"
    agregar = driver.find_element(*por_descripcion("Agregar Disco SSD Externo 1 TB al carrito"))
    assert not agregar.is_enabled()
