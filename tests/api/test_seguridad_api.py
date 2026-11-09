"""Lab 6.1 · Pruebas negativas y de seguridad de la API.

Fixtures: api (sin sesión), api_ana (Ana García), api_luis (Luis Pérez).
Recuerden: la orden 1 pertenece a Luis Pérez (datos base).

Ideas (OWASP API Top 10 2023):
  - API1 BOLA: ¿Ana puede ver, pagar o cancelar una orden de Luis cambiando el ID?
  - API2 Autenticación: token inválido, sin token, mensajes de error del login
  - Mensajes de error: ¿revelan datos personales? (RNF-04, CWE-209)
  - Entradas inválidas: tipos incorrectos, campos faltantes, valores fuera de rango
"""


def test_token_invalido(api):  # ejemplo
    api.session.headers["Authorization"] = "Bearer token-inventado"
    res = api.get("/api/cart")
    assert res.status_code == 401


# TODO: agreguen aquí sus pruebas negativas y de seguridad.
