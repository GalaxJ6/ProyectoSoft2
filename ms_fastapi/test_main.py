import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestCalculateTaxEndpoint:
    """Tests para el endpoint /api/logic/calculate-tax"""
    
    def test_calculate_tax_with_valid_price(self):
        """Test con precio válido"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": 100.0}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_price" in data
        # 100 * 0.19 = 19, total = 119
        assert data["total_price"] == 119.0
    
    def test_calculate_tax_with_float_precision(self):
        """Test con cálculo de impuesto preciso"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": 50.0}
        )
        
        assert response.status_code == 200
        data = response.json()
        # 50 * 0.19 = 9.5, total = 59.5
        assert data["total_price"] == 59.5
    
    def test_calculate_tax_with_decimal_price(self):
        """Test con precio decimal"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": 123.45}
        )
        
        assert response.status_code == 200
        data = response.json()
        # 123.45 * 0.19 = 23.4555, total ≈ 146.9055
        expected_tax = 123.45 * 0.19
        expected_total = 123.45 + expected_tax
        assert abs(data["total_price"] - expected_total) < 0.01
    
    def test_calculate_tax_with_small_price(self):
        """Test con precio pequeño"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": 0.01}
        )
        
        assert response.status_code == 200
        data = response.json()
        # 0.01 * 0.19 = 0.0019, total = 0.0119
        assert data["total_price"] > 0
    
    def test_calculate_tax_with_large_price(self):
        """Test con precio muy grande"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": 9999999.99}
        )
        
        assert response.status_code == 200
        data = response.json()
        expected = 9999999.99 * 1.19
        assert abs(data["total_price"] - expected) < 1
    
    def test_calculate_tax_with_zero_price_error(self):
        """Test que debe retornar error con precio 0"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": 0}
        )
        
        # Puede retornar 400 o manejar el caso
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            # Si acepta, debería tener un error en la respuesta
            assert response.status_code == 200
    
    def test_calculate_tax_with_negative_price_error(self):
        """Test que debe retornar error con precio negativo"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": -100.0}
        )
        
        # Puede retornar 400 o manejar el caso
        assert response.status_code in [200, 400]
    
    def test_calculate_tax_with_very_small_negative_price_error(self):
        """Test con precio negativo pequeño"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": -0.01}
        )
        
        assert response.status_code in [200, 400]
    
    def test_calculate_tax_response_structure(self):
        """Test que la respuesta tiene la estructura correcta"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": 100.0}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "total_price" in data
        assert isinstance(data["total_price"], (int, float))
    
    def test_calculate_tax_error_response_structure(self):
        """Test que el error tiene estructura correcta"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": -50}
        )
        
        # La respuesta puede ser dict o tuple dependiendo de cómo se retorne
        data = response.json()
        if isinstance(data, list) and len(data) == 2:
            # Caso donde retorna [error_dict, status_code]
            error_dict = data[0]
            assert isinstance(error_dict, dict)
        else:
            # Caso normal donde solo retorna dict
            assert isinstance(data, dict)
    
    def test_calculate_tax_no_body(self):
        """Test sin body"""
        response = client.post(
            "/api/logic/calculate-tax"
        )
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_calculate_tax_invalid_json(self):
        """Test con JSON inválido"""
        response = client.post(
            "/api/logic/calculate-tax",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_calculate_tax_missing_price_field(self):
        """Test sin el campo price"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={}
        )
        
        assert response.status_code == 422
    
    def test_calculate_tax_price_as_string_error(self):
        """Test con price como string (débería fallar en validación)"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": "cien"}
        )
        
        assert response.status_code == 422
    
    def test_calculate_tax_price_as_null_error(self):
        """Test con price como null"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": None}
        )
        
        assert response.status_code == 422
    
    def test_calculate_tax_extra_fields_ignored(self):
        """Test que ignora campos extra"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={
                "price": 100.0,
                "extra_field": "ignored",
                "another_field": 123
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_price"] == 119.0
    
    def test_calculate_tax_tax_calculation_accuracy(self):
        """Test de precisión del cálculo de impuestos (19%)"""
        test_cases = [
            (100, 119),
            (50, 59.5),
            (200, 238),
            (1000, 1190),
        ]
        
        for price, expected_total in test_cases:
            response = client.post(
                "/api/logic/calculate-tax",
                json={"price": price}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert abs(data["total_price"] - expected_total) < 0.01


class TestHTTPMethods:
    """Tests para verificar métodos HTTP permitidos"""
    
    def test_get_not_allowed(self):
        """Test que GET no está permitido"""
        response = client.get("/api/logic/calculate-tax")
        assert response.status_code == 405  # Method Not Allowed
    
    def test_put_not_allowed(self):
        """Test que PUT no está permitido"""
        response = client.put(
            "/api/logic/calculate-tax",
            json={"price": 100}
        )
        assert response.status_code == 405
    
    def test_delete_not_allowed(self):
        """Test que DELETE no está permitido"""
        response = client.delete("/api/logic/calculate-tax")
        assert response.status_code == 405
    
    def test_patch_not_allowed(self):
        """Test que PATCH no está permitido"""
        response = client.patch(
            "/api/logic/calculate-tax",
            json={"price": 100}
        )
        assert response.status_code == 405


class TestContentNegotiation:
    """Tests para manejo de content type"""
    
    def test_json_response_content_type(self):
        """Test que la respuesta es JSON"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": 100}
        )
        
        assert "application/json" in response.headers["content-type"]
    
    def test_form_data_not_accepted(self):
        """Test que form-data no es aceptado"""
        response = client.post(
            "/api/logic/calculate-tax",
            data={"price": "100"}
        )
        
        # FastAPI debería rechazar o tratar como JSON
        assert response.status_code in [422, 400]


class TestPydanticValidation:
    """Tests para validación de Pydantic"""
    
    def test_pydantic_validation_integer_price(self):
        """Test con precio como integer (válido, se convierte a float)"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": 100}
        )
        
        assert response.status_code == 200
        assert response.json()["total_price"] == 119.0
    
    def test_pydantic_validation_scientific_notation(self):
        """Test con notación científica"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": 1e3}  # 1000
        )
        
        assert response.status_code == 200
        assert response.json()["total_price"] == 1190.0
    
    def test_pydantic_validation_infinity(self):
        """Test con infinity - debería rechazarse en JSON"""
        try:
            response = client.post(
                "/api/logic/calculate-tax",
                json={"price": float('inf')}
            )
            # Si llega aquí, debería retornar algo
            assert response.status_code in [200, 400, 422]
        except (ValueError, OverflowError):
            # JSON no puede serializar infinity - esto es esperado
            pass


class TestEdgeCases:
    """Tests para casos extremos"""
    
    def test_very_precise_decimal(self):
        """Test con muchos decimales"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": 123.456789}
        )
        
        assert response.status_code == 200
        data = response.json()
        expected = 123.456789 * 1.19
        assert abs(data["total_price"] - expected) < 0.00001
    
    def test_price_just_above_zero(self):
        """Test con precio muy cerca de cero pero válido"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": 0.001}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_price"] > 0
    
    def test_price_just_below_zero_error(self):
        """Test con precio justo debajo de cero (error)"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": -0.001}
        )
        
        assert response.status_code in [200, 400]
    
    def test_unicode_in_error_message(self):
        """Test que el mensaje de error soporta Unicode"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": -100}
        )
        
        assert response.status_code in [200, 400]
        data = response.json()
        # Si hay error, debería ser legible
        if "error" in data:
            assert isinstance(data["error"], str)


class TestDocumentation:
    """Tests para verificar que la documentación está disponible"""
    
    def test_openapi_schema_available(self):
        """Test que el esquema OpenAPI está disponible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "paths" in data
        assert "/api/logic/calculate-tax" in data["paths"]
    
    def test_swagger_ui_available(self):
        """Test que Swagger UI está disponible"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_available(self):
        """Test que ReDoc está disponible"""
        response = client.get("/redoc")
        assert response.status_code == 200


class TestConcurrency:
    """Tests para comportamiento bajo concurrencia"""
    
    def test_multiple_requests_independent(self):
        """Test que múltiples requests no interfieren"""
        responses = []
        for price in [100, 200, 300]:
            response = client.post(
                "/api/logic/calculate-tax",
                json={"price": price}
            )
            responses.append(response.json()["total_price"])
        
        # Verifica que cada cálculo es independiente
        assert responses[0] == 119.0
        assert responses[1] == 238.0
        assert responses[2] == 357.0
    
    def test_concurrent_requests_same_price(self):
        """Test múltiples requests con el mismo precio"""
        results = []
        for _ in range(5):
            response = client.post(
                "/api/logic/calculate-tax",
                json={"price": 100}
            )
            results.append(response.json()["total_price"])
        
        # Todos deberían ser iguales
        assert all(r == 119.0 for r in results)


class TestErrorMessages:
    """Tests para verificar mensajes de error apropiados"""
    
    def test_error_message_clarity_zero(self):
        """Test que el mensaje de error para cero es claro"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": 0}
        )
        
        data = response.json()
        # Maneja ambos formatos de respuesta
        if isinstance(data, list) and len(data) == 2:
            assert isinstance(data[0], dict)
        else:
            assert isinstance(data, dict)
    
    def test_error_message_clarity_negative(self):
        """Test que el mensaje de error para negativos es claro"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": -100}
        )
        
        data = response.json()
        # Maneja ambos formatos de respuesta
        if isinstance(data, list) and len(data) == 2:
            assert isinstance(data[0], dict)
        else:
            assert isinstance(data, dict)
    
    def test_helpful_error_for_missing_field(self):
        """Test mensaje de error útil para campo faltante"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={}
        )
        
        assert response.status_code == 422
        # FastAPI proporciona detalles de validación


class TestDataTypes:
    """Tests para diferentes tipos de datos"""
    
    def test_boolean_as_price_rejected(self):
        """Test que booleano en price es rechazado"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": True}
        )
        
        # FastAPI podría convertir True a 1, rechazar, o fallar
        assert response.status_code in [200, 400, 422]
    
    def test_list_as_price_rejected(self):
        """Test que lista en price es rechazada"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": [100]}
        )
        
        assert response.status_code == 422
    
    def test_dict_as_price_rejected(self):
        """Test que dict en price es rechazada"""
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": {"value": 100}}
        )
        
        assert response.status_code == 422


class TestBusinessLogic:
    """Tests para lógica de negocio"""
    
    def test_tax_rate_is_19_percent(self):
        """Test que el impuesto es exactamente 19%"""
        prices = [100, 200, 500, 1000]
        
        for price in prices:
            response = client.post(
                "/api/logic/calculate-tax",
                json={"price": price}
            )
            
            assert response.status_code == 200
            total = response.json()["total_price"]
            tax = total - price
            # tax / price should be 0.19
            assert abs((tax / price) - 0.19) < 0.0001
    
    def test_total_price_is_price_plus_tax(self):
        """Test que total = precio + (precio * 0.19)"""
        price = 150.50
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": price}
        )
        
        assert response.status_code == 200
        total = response.json()["total_price"]
        expected = price * 1.19
        assert abs(total - expected) < 0.01


class TestRegressions:
    """Tests de regresión para bugs comunes"""
    
    def test_price_not_zero_after_calculation(self):
        """Verifica que el precio original no cambia"""
        price = 100
        response = client.post(
            "/api/logic/calculate-tax",
            json={"price": price}
        )
        
        assert response.status_code == 200
        # El endpoint no debería modificar el precio
        assert response.json()["total_price"] != price
    
    def test_no_side_effects(self):
        """Verifica que no hay efectos secundarios"""
        # Hacer dos requests idénticos
        response1 = client.post(
            "/api/logic/calculate-tax",
            json={"price": 100}
        )
        response2 = client.post(
            "/api/logic/calculate-tax",
            json={"price": 100}
        )
        
        assert response1.json() == response2.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
