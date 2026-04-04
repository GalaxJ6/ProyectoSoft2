import random
import string
from locust import HttpUser, task, between

class ProjectFullTest(HttpUser):
    wait_time = between(2, 4)
    token = ""

    def on_start(self):
        """ 
        Se ejecuta al iniciar cada usuario virtual. 
        Hace login para tener el token listo para las rutas protegidas.
        """
        login_data = {
            "email": "s.gomez@universidad.edu.co", # <--- Usuario base en la BD
            "password": "Password2026*"
        }
        with self.client.post("/api/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                self.token = response.json().get("access_token") or response.json().get("token")
            else:
                response.failure(f"Error Login inicial: {response.status_code}")

    # --- RUTAS PÚBLICAS ---

    @task(1)
    def register_new_user(self):
        """ Prueba de Registro (Crea usuarios aleatorios) """
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        payload = {
            "name": f"User_{random_suffix}",
            "email": f"test_{random_suffix}@example.com",
            "password": "Password123*",
            "password_confirmation": "Password123*",
            "security_question": "¿Mascota?",
            "security_answer": "Pelusa"
        }
        self.client.post("/api/register", json=payload)

    @task(1)
    def recovery_password(self):
        """ Prueba de Recuperación de Contraseña """
        payload = {
            "email": "s.gomez@universidad.edu.co",
            "security_answer": "Roco", # <--- Asegurarse que esta respuesta coincida con la que tiene en la BD
            "new_password": "NewPassword2026*"
        }
        self.client.post("/api/recovery", json=payload)

    # --- RUTAS PROTEGIDAS ---

    @task(4)
    def get_products(self):
        """ Consulta de Catálogo (Proxy a Express) """
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.get("/api/catalog/products", headers=headers)

    @task(2)
    def create_product_orchestrated(self):
        """ Creación Orquestada (Laravel -> FastAPI -> Express -> Flask) """
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {
                "name": f"Prod_{random.randint(100, 999)}",
                "price": 100,
                "description": "Carga vía Locust",
                "stock": 10,
                "category": "Test",
                "user_id": 2 # <--- ID que exista en la BD
            }
            self.client.post("/api/catalog/products", json=payload, headers=headers)

    @task(2)
    def get_django_profile(self):
        """ Info detallada del usuario (Proxy a Django) """
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            # Se prueba con el ID 2 que es el que está activo en mi BD
            self.client.get("/api/users/profile/2", headers=headers)

    @task(1)
    def logout_test(self):
        """ Prueba de Cierre de Sesión """
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            with self.client.post("/api/logout", headers=headers, catch_response=True) as response:
                if response.status_code == 200:
                    self.token = "" 
                    response.success()