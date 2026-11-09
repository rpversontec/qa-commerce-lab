"""Ejemplo de prueba móvil: inicio de sesión y catálogo. Úsenla como modelo para las suyas."""
import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.mobile.conftest import por_descripcion, por_id

pytestmark = pytest.mark.mobile


def test_login_muestra_el_catalogo(driver, servidor_movil):
    espera = WebDriverWait(driver, 20)

    servidor = espera.until(EC.presence_of_element_located(por_descripcion("Servidor")))
    servidor.clear()
    servidor.send_keys(servidor_movil)
    driver.find_element(*por_descripcion("Correo electrónico")).send_keys("ana.garcia@example.com")
    driver.find_element(*por_descripcion("Contraseña")).send_keys("Password123")
    driver.find_element(*por_descripcion("Entrar")).click()

    # Espera explícita: la pantalla cambia cuando responde la API
    info = espera.until(EC.presence_of_element_located(por_id("catalog_info")))
    espera.until(lambda _: info.text == "38 productos")
    assert driver.find_element(*por_id("catalog_user")).text == "Ana García"
