"""Fixtures para las pruebas móviles con Appium (app Android de QA Commerce Lab).

Antes de ejecutar:
  1. Emulador encendido (adb devices debe mostrarlo).
  2. Servidor de Appium corriendo: appium
  3. pytest tests/mobile

Si Appium no está corriendo, las pruebas se omiten (skip) en lugar de fallar.
La app se conecta al servidor de pruebas por 10.0.2.2, que es el localhost del equipo
visto desde el emulador.
"""
import os
import urllib.request
from pathlib import Path

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

from tests.conftest import _post

ROOT = Path(__file__).resolve().parents[2]
APK = ROOT / "mobile" / "qa-commerce-lab.apk"
APPIUM_URL = os.environ.get("APPIUM_URL", "http://127.0.0.1:4723")


def _appium_disponible() -> bool:
    try:
        with urllib.request.urlopen(f"{APPIUM_URL}/status", timeout=3) as res:
            return b'"ready":true' in res.read().replace(b" ", b"")
    except OSError:
        return False


@pytest.fixture(scope="session")
def appium_listo():
    if not _appium_disponible():
        pytest.skip(f"Appium no está corriendo en {APPIUM_URL}. Arranca 'appium' y un emulador.")


@pytest.fixture
def servidor_movil(servidor) -> str:
    """URL del servidor de pruebas vista desde el emulador. Reinicia los datos antes de cada prueba."""
    _post(f"{servidor}/api/test/reset")
    return servidor.replace("127.0.0.1", "10.0.2.2")


@pytest.fixture
def driver(appium_listo):
    opts = UiAutomator2Options()
    opts.platform_name = "Android"
    opts.automation_name = "UiAutomator2"
    opts.app = str(APK)
    opts.app_package = "mx.tec.qacl"
    opts.app_activity = ".LoginActivity"
    opts.no_reset = False  # datos de la app limpios en cada prueba
    d = webdriver.Remote(APPIUM_URL, options=opts)
    d.implicitly_wait(0)
    cerrar_aviso_sistema(d)
    yield d
    d.quit()


def cerrar_aviso_sistema(d) -> None:
    """Cierra el aviso 'System UI isn't responding' que a veces muestra el emulador."""
    for boton in d.find_elements(AppiumBy.XPATH, '//*[@text="Wait" or @text="Esperar"]'):
        boton.click()


def por_descripcion(texto: str):
    return (AppiumBy.ACCESSIBILITY_ID, texto)


def por_id(nombre: str):
    return (AppiumBy.ID, f"mx.tec.qacl:id/{nombre}")
