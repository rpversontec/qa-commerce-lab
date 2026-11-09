"""Fixtures para las pruebas de API con requests contra el servidor real.

- api: cliente HTTP con la base de datos reiniciada antes de cada prueba.
- api_ana: lo mismo, con sesión iniciada como Ana García.
- api_luis: un segundo cliente, con sesión de Luis Pérez (para probar accesos entre usuarios).
- contrato: el documento OpenAPI publicado por la app (/openapi.json).

Ejecutar:  pytest tests/api
"""
import pytest
import requests

from tests.conftest import _post


class Api:
    """Cliente mínimo: requests con la URL base del servidor de pruebas."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        return self.session.request(method, self.base_url + path, timeout=10, **kwargs)

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, **kw):
        return self.request("POST", path, **kw)

    def patch(self, path, **kw):
        return self.request("PATCH", path, **kw)

    def delete(self, path, **kw):
        return self.request("DELETE", path, **kw)

    def login(self, email: str, password: str) -> dict:
        res = self.post("/api/auth/login", json={"email": email, "password": password})
        res.raise_for_status()
        self.session.headers["Authorization"] = f"Bearer {res.json()['token']}"
        return res.json()


@pytest.fixture
def api(servidor) -> Api:
    _post(f"{servidor}/api/test/reset")
    return Api(servidor)


@pytest.fixture
def api_ana(api) -> Api:
    api.login("ana.garcia@example.com", "Password123")
    return api


@pytest.fixture
def api_luis(servidor, api) -> Api:
    otro = Api(servidor)
    otro.login("luis.perez@example.com", "Password123")
    return otro


@pytest.fixture(scope="session")
def contrato(servidor) -> dict:
    return requests.get(f"{servidor}/openapi.json", timeout=10).json()
