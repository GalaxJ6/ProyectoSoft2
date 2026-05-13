import unittest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
from app import app, make_log


class FlaskLoggingTestCase(unittest.TestCase):
    """Tests para el servicio de logging en Flask"""
    
    def setUp(self):
        """Configura el cliente de prueba"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Limpia después de cada test"""
        pass


class MakeLogFunctionTest(FlaskLoggingTestCase):
    """Tests para la función make_log"""
    
    def test_make_log_creates_entry_with_all_fields(self):
        """Verifica que make_log crea una entrada con todos los campos"""
        log_entry = make_log('test_event', 1, 'test details', 'SUCCESS')
        
        self.assertIn('timestamp', log_entry)
        self.assertEqual(log_entry['event'], 'test_event')
        self.assertEqual(log_entry['user_id'], 1)
        self.assertEqual(log_entry['details'], 'test details')
        self.assertEqual(log_entry['status'], 'SUCCESS')
    
    def test_make_log_default_status(self):
        """Verifica el estado por defecto de make_log"""
        log_entry = make_log('event', 1)
        self.assertEqual(log_entry['status'], 'SUCCESS')
    
    def test_make_log_timestamp_format(self):
        """Verifica que el timestamp está en formato correcto"""
        log_entry = make_log('event', 1)
        timestamp = log_entry['timestamp']
        
        # Verifica que tenga el formato YYYY-MM-DD HH:MM:SS
        try:
            datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            valid_format = True
        except ValueError:
            valid_format = False
        
        self.assertTrue(valid_format)
    
    def test_make_log_with_none_details(self):
        """Verifica que make_log maneja details=None"""
        log_entry = make_log('event', 1, None)
        self.assertIsNone(log_entry['details'])
    
    def test_make_log_with_complex_details(self):
        """Verifica que make_log maneja detalles complejos"""
        details = {'product': 'laptop', 'quantity': 3}
        log_entry = make_log('event', 1, details)
        self.assertEqual(log_entry['details'], details)
    
    def test_make_log_with_string_user_id(self):
        """Test make_log con user_id como string"""
        log_entry = make_log('event', 'user123')
        self.assertEqual(log_entry['user_id'], 'user123')
    
    def test_make_log_with_zero_user_id(self):
        """Test make_log con user_id = 0"""
        log_entry = make_log('event', 0)
        self.assertEqual(log_entry['user_id'], 0)


class LogEventEndpointTest(FlaskLoggingTestCase):
    """Tests para el endpoint /api/notify/log"""
    
    def test_log_event_success(self):
        """Test POST exitoso al endpoint log"""
        payload = {
            'event': 'product_viewed',
            'user_id': 1,
            'details': 'laptop'
        }
        
        response = self.client.post(
            '/api/notify/log',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('log', data)
        self.assertEqual(data['log']['event'], 'product_viewed')
    
    def test_log_event_missing_event_field(self):
        """Test POST sin campo 'event'"""
        payload = {
            'user_id': 1,
            'details': 'test'
        }
        
        response = self.client.post(
            '/api/notify/log',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_log_event_missing_user_id_field(self):
        """Test POST sin campo 'user_id'"""
        payload = {
            'event': 'test_event',
            'details': 'test'
        }
        
        response = self.client.post(
            '/api/notify/log',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_log_event_empty_payload(self):
        """Test POST con payload vacío"""
        response = self.client.post(
            '/api/notify/log',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_log_event_none_payload(self):
        """Test POST con None como payload"""
        response = self.client.post(
            '/api/notify/log',
            data=None,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_log_event_with_product_fallback(self):
        """Test que usa 'product' cuando 'details' no está presente"""
        payload = {
            'event': 'product_action',
            'user_id': 1,
            'product': 'monitor'
        }
        
        response = self.client.post(
            '/api/notify/log',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['log']['details'], 'monitor')
    
    def test_log_event_details_priority_over_product(self):
        """Test que 'details' tiene prioridad sobre 'product'"""
        payload = {
            'event': 'action',
            'user_id': 1,
            'details': 'details_value',
            'product': 'product_value'
        }
        
        response = self.client.post(
            '/api/notify/log',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['log']['details'], 'details_value')
    
    def test_log_event_with_special_characters(self):
        """Test con caracteres especiales"""
        payload = {
            'event': 'test_event<>&"',
            'user_id': 1,
            'details': 'details with <html> & special'
        }
        
        response = self.client.post(
            '/api/notify/log',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)


class LoginLogEndpointTest(FlaskLoggingTestCase):
    """Tests para el endpoint /api/notify/login"""
    
    def test_login_event_success(self):
        """Test POST exitoso para login"""
        payload = {
            'user_id': 123,
            'username': 'john_doe'
        }
        
        response = self.client.post(
            '/api/notify/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['log']['event'], 'login')
        self.assertIn('john_doe', data['log']['details'])
    
    def test_login_event_missing_user_id(self):
        """Test login sin user_id"""
        payload = {
            'username': 'john_doe'
        }
        
        response = self.client.post(
            '/api/notify/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_login_event_missing_username(self):
        """Test login sin username"""
        payload = {
            'user_id': 123
        }
        
        response = self.client.post(
            '/api/notify/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_login_event_empty_payload(self):
        """Test login con payload vacío"""
        response = self.client.post(
            '/api/notify/login',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_login_event_with_special_username(self):
        """Test login con username especial"""
        payload = {
            'user_id': 1,
            'username': 'user@example.com'
        }
        
        response = self.client.post(
            '/api/notify/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)


class LogoutLogEndpointTest(FlaskLoggingTestCase):
    """Tests para el endpoint /api/notify/logout"""
    
    def test_logout_event_success(self):
        """Test POST exitoso para logout"""
        payload = {
            'user_id': 123
        }
        
        response = self.client.post(
            '/api/notify/logout',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['log']['event'], 'logout')
        self.assertEqual(data['log']['user_id'], 123)
    
    def test_logout_event_missing_user_id(self):
        """Test logout sin user_id"""
        response = self.client.post(
            '/api/notify/logout',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_logout_event_with_extra_fields(self):
        """Test logout con campos extra"""
        payload = {
            'user_id': 123,
            'extra_field': 'ignored'
        }
        
        response = self.client.post(
            '/api/notify/logout',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)


class RecoveryLogEndpointTest(FlaskLoggingTestCase):
    """Tests para el endpoint /api/notify/recovery"""
    
    def test_recovery_event_success(self):
        """Test POST exitoso para recovery"""
        payload = {
            'user_id': 123,
            'email': 'user@example.com'
        }
        
        response = self.client.post(
            '/api/notify/recovery',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['log']['event'], 'password_recovery')
        self.assertIn('user@example.com', data['log']['details'])
    
    def test_recovery_event_missing_user_id(self):
        """Test recovery sin user_id"""
        payload = {
            'email': 'user@example.com'
        }
        
        response = self.client.post(
            '/api/notify/recovery',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_recovery_event_missing_email(self):
        """Test recovery sin email"""
        payload = {
            'user_id': 123
        }
        
        response = self.client.post(
            '/api/notify/recovery',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_recovery_event_with_invalid_email(self):
        """Test recovery con email inválido (pero se acepta)"""
        payload = {
            'user_id': 123,
            'email': 'not-an-email'
        }
        
        response = self.client.post(
            '/api/notify/recovery',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)


class UserDataLogEndpointTest(FlaskLoggingTestCase):
    """Tests para el endpoint /api/notify/user-data"""
    
    def test_user_data_log_success(self):
        """Test POST exitoso para user-data"""
        payload = {
            'user_id': 123,
            'action': 'create',
            'fields': {'bio': 'Developer', 'phone': '+34 123'}
        }
        
        response = self.client.post(
            '/api/notify/user-data',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['log']['event'], 'user_data')
    
    def test_user_data_log_missing_user_id(self):
        """Test user-data sin user_id"""
        payload = {
            'action': 'create'
        }
        
        response = self.client.post(
            '/api/notify/user-data',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_user_data_log_missing_action(self):
        """Test user-data sin action"""
        payload = {
            'user_id': 123
        }
        
        response = self.client.post(
            '/api/notify/user-data',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_user_data_log_without_fields(self):
        """Test user-data sin campos asociados"""
        payload = {
            'user_id': 123,
            'action': 'delete'
        }
        
        response = self.client.post(
            '/api/notify/user-data',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)


class ProductsLogEndpointTest(FlaskLoggingTestCase):
    """Tests para el endpoint /api/notify/products"""
    
    def test_products_log_success(self):
        """Test POST exitoso para products"""
        payload = {
            'user_id': 123,
            'action': 'view',
            'query': 'laptops'
        }
        
        response = self.client.post(
            '/api/notify/products',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('products_view', data['log']['event'])
    
    def test_products_log_empty_payload(self):
        """Test products con payload vacío (usa valores por defecto)"""
        response = self.client.post(
            '/api/notify/products',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['log']['user_id'], 'anon')
        self.assertIn('products_', data['log']['event'])
    
    def test_products_log_with_only_user_id(self):
        """Test products con solo user_id"""
        payload = {
            'user_id': 999
        }
        
        response = self.client.post(
            '/api/notify/products',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
    
    def test_products_log_different_actions(self):
        """Test products con diferentes acciones"""
        actions = ['view', 'filter', 'search', 'browse']
        
        for action in actions:
            payload = {
                'user_id': 1,
                'action': action
            }
            
            response = self.client.post(
                '/api/notify/products',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertIn(f'products_{action}', data['log']['event'])


class EventLogEndpointTest(FlaskLoggingTestCase):
    """Tests para el endpoint /api/notify/event"""
    
    def test_event_log_success(self):
        """Test POST exitoso para event"""
        payload = {
            'event': 'custom_event',
            'user_id': 123,
            'details': 'Some custom details'
        }
        
        response = self.client.post(
            '/api/notify/event',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['log']['event'], 'custom_event')
    
    def test_event_log_missing_event(self):
        """Test event sin event field"""
        payload = {
            'user_id': 123
        }
        
        response = self.client.post(
            '/api/notify/event',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_event_log_missing_user_id(self):
        """Test event sin user_id"""
        payload = {
            'event': 'test_event'
        }
        
        response = self.client.post(
            '/api/notify/event',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_event_log_without_details(self):
        """Test event sin detalles (usa valor por defecto)"""
        payload = {
            'event': 'simple_event',
            'user_id': 1
        }
        
        response = self.client.post(
            '/api/notify/event',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['log']['details'], 'N/A')


class HTTPMethodTest(FlaskLoggingTestCase):
    """Tests para verificar que solo se acepten métodos HTTP POST"""
    
    def test_get_request_not_allowed(self):
        """Test GET en endpoints que esperan POST"""
        response = self.client.get('/api/notify/log')
        self.assertEqual(response.status_code, 405)
    
    def test_put_request_not_allowed(self):
        """Test PUT en endpoint"""
        response = self.client.put(
            '/api/notify/login',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)
    
    def test_delete_request_not_allowed(self):
        """Test DELETE en endpoint"""
        response = self.client.delete('/api/notify/logout')
        self.assertEqual(response.status_code, 405)


class EdgeCasesTest(FlaskLoggingTestCase):
    """Tests para casos extremos"""
    
    def test_very_large_user_id(self):
        """Test con user_id muy grande"""
        payload = {
            'event': 'event',
            'user_id': 999999999999
        }
        
        response = self.client.post(
            '/api/notify/log',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
    
    def test_unicode_in_payload(self):
        """Test con caracteres Unicode"""
        payload = {
            'event': 'evento_español',
            'user_id': 1,
            'details': 'Detalles en español con acentos: á, é, í, ó, ú'
        }
        
        response = self.client.post(
            '/api/notify/log',
            data=json.dumps(payload, ensure_ascii=False),
            content_type='application/json; charset=utf-8'
        )
        
        self.assertEqual(response.status_code, 201)
    
    def test_very_long_details(self):
        """Test con detalles muy largos"""
        payload = {
            'event': 'event',
            'user_id': 1,
            'details': 'x' * 10000
        }
        
        response = self.client.post(
            '/api/notify/log',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
    
    def test_nested_json_structure(self):
        """Test con estructuras JSON anidadas complejas"""
        payload = {
            'event': 'complex_event',
            'user_id': 1,
            'details': {
                'nested': {
                    'deep': {
                        'data': 'value'
                    }
                }
            }
        }
        
        response = self.client.post(
            '/api/notify/log',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)


class ContentTypeTest(FlaskLoggingTestCase):
    """Tests para diferentes tipos de contenido"""
    
    def test_json_content_type(self):
        """Test con content-type application/json"""
        payload = {'event': 'test', 'user_id': 1}
        
        response = self.client.post(
            '/api/notify/log',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
    
    def test_missing_content_type(self):
        """Test sin especificar content-type"""
        response = self.client.post(
            '/api/notify/log',
            data=json.dumps({'event': 'test', 'user_id': 1})
        )
        
        # Flask rechaza JSON sin content-type apropido (415 Unsupported Media Type)
        self.assertIn(response.status_code, [400, 415, 201])


if __name__ == '__main__':
    unittest.main()
