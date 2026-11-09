"""Page Objects de QA Commerce Lab.

Cada clase representa una página: expone lo que un usuario puede hacer y ver,
y esconde los localizadores. Si la interfaz cambia, se corrige aquí, no en cada prueba.
"""
from playwright.sync_api import Locator, Page, expect


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.correo = page.get_by_label("Correo electrónico")
        self.contrasena = page.get_by_label("Contraseña")
        self.entrar = page.get_by_role("button", name="Entrar")
        self.error = page.get_by_role("alert")

    def abrir(self) -> "LoginPage":
        self.page.goto("/login")
        return self

    def iniciar_sesion(self, email: str, password: str) -> None:
        self.correo.fill(email)
        self.contrasena.fill(password)
        self.entrar.click()


class ProductoPage:
    def __init__(self, page: Page):
        self.page = page
        self.cantidad = page.get_by_label("Cantidad")
        self.agregar_btn = page.get_by_role("button", name="Agregar al carrito")
        self.aviso = page.locator(".flash.ok")

    def abrir(self, product_id: int) -> "ProductoPage":
        self.page.goto(f"/productos/{product_id}")
        return self

    def agregar(self, cantidad: int) -> None:
        self.cantidad.fill(str(cantidad))
        self.agregar_btn.click()
        expect(self.aviso).to_have_text("Producto agregado al carrito")


class CarritoPage:
    def __init__(self, page: Page):
        self.page = page
        self.subtotal = page.locator("#sum-subtotal")
        self.descuento = page.locator("#sum-discount")
        self.envio = page.locator("#sum-shipping")
        self.total = page.locator("#sum-total")
        self.cupon = page.get_by_label("Cupón")
        self.aplicar = page.get_by_role("button", name="Aplicar")
        self.continuar = page.get_by_role("link", name="Continuar al checkout")

    def abrir(self) -> "CarritoPage":
        self.page.goto("/carrito")
        return self

    def aplicar_cupon(self, codigo: str) -> None:
        self.cupon.fill(codigo)
        self.aplicar.click()

    def ir_al_checkout(self) -> "CheckoutPage":
        self.continuar.click()
        return CheckoutPage(self.page)


class CheckoutPage:
    DIRECCION = {"Calle y número": "Calle 1", "Colonia": "Centro", "Ciudad": "Monterrey",
                 "Estado": "Nuevo León", "Código postal": "64000", "Teléfono de contacto": "8112345678"}

    def __init__(self, page: Page):
        self.page = page
        self.total = page.locator("#co-total")
        self.confirmar = page.get_by_role("button", name="Confirmar y pagar")

    def abrir(self) -> "CheckoutPage":
        self.page.goto("/checkout")
        return self

    def enviar_direccion(self, **cambios: str) -> "PagoPage":
        for campo, valor in {**self.DIRECCION, **cambios}.items():
            self.page.get_by_label(campo).fill(valor)
        self.confirmar.click()
        return PagoPage(self.page)


class PagoPage:
    def __init__(self, page: Page):
        self.page = page
        self.error: Locator = page.locator("#payment-error")
        self.confirmacion = page.locator("#confirmation")
        self.ultimos4 = page.locator("#confirm-last4")

    def pagar(self, numero: str, titular: str = "Ana García", vencimiento: str = "12/30", cvv: str = "123") -> None:
        self.page.get_by_label("Nombre del titular").fill(titular)
        self.page.get_by_label("Número de tarjeta").fill(numero)
        self.page.get_by_label("Vencimiento (MM/AA)").fill(vencimiento)
        self.page.get_by_label("CVV").fill(cvv)
        self.page.get_by_role("button", name="Pagar").click()
