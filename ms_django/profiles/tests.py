from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import json
from .models import Profile
from unittest.mock import patch, MagicMock


class ProfileModelTest(TestCase):
    """Tests para el modelo Profile"""
    
    def setUp(self):
        """Configura datos iniciales para cada test"""
        self.profile = Profile.objects.create(
            user_id=1,
            bio="Software Developer",
            phone="+34 123 456 789",
            address="Madrid, Spain"
        )
    
    def test_create_profile(self):
        """Verifica que se crea un perfil correctamente"""
        profile = Profile.objects.get(user_id=1)
        self.assertEqual(profile.user_id, 1)
        self.assertEqual(profile.bio, "Software Developer")
        self.assertEqual(profile.phone, "+34 123 456 789")
        self.assertEqual(profile.address, "Madrid, Spain")
    
    def test_profile_string_representation(self):
        """Verifica la representación en string del modelo"""
        expected_str = f"Perfil del Usuario ID: {self.profile.user_id}"
        self.assertEqual(str(self.profile), expected_str)
    
    def test_profile_unique_user_id(self):
        """Verifica que user_id es único"""
        with self.assertRaises(Exception):
            Profile.objects.create(
                user_id=1,  # Ya existe
                bio="Another Developer",
                phone="+34 987 654 321"
            )
    
    def test_profile_optional_fields(self):
        """Verifica que los campos opcionales pueden estar vacíos"""
        profile = Profile.objects.create(user_id=2)
        self.assertIsNone(profile.bio)
        self.assertIsNone(profile.phone)
        self.assertIsNone(profile.address)
    
    def test_profile_bio_max_length(self):
        """Verifica el límite de caracteres en bio"""
        long_bio = "x" * 501
        profile = Profile(user_id=3, bio=long_bio)
        self.assertGreater(len(long_bio), 500)
    
    def test_profile_phone_max_length(self):
        """Verifica el límite de caracteres en phone"""
        phone = "x" * 21  # Más de 20 caracteres
        profile = Profile(user_id=4, phone=phone)
        self.assertGreater(len(phone), 20)
    
    def test_update_profile_fields(self):
        """Verifica la actualización de campos del perfil"""
        self.profile.bio = "Senior Developer"
        self.profile.phone = "+34 111 222 333"
        self.profile.save()
        
        updated_profile = Profile.objects.get(user_id=1)
        self.assertEqual(updated_profile.bio, "Senior Developer")
        self.assertEqual(updated_profile.phone, "+34 111 222 333")
    
    def test_delete_profile(self):
        """Verifica que se puede eliminar un perfil"""
        profile_id = self.profile.id
        self.profile.delete()
        self.assertFalse(Profile.objects.filter(id=profile_id).exists())


class ProfileAPIViewTest(TestCase):
    """Tests para las vistas de API de Profile"""
    
    def setUp(self):
        """Configura datos iniciales y cliente API"""
        self.client = APIClient()
        self.profile = Profile.objects.create(
            user_id=1,
            bio="Test Bio",
            phone="+34 123 456 789",
            address="Test Address"
        )
        self.base_url = reverse('profile_handler', kwargs={'user_id': 1})
    
    def test_get_existing_profile(self):
        """Test GET: obtener perfil existente"""
        response = self.client.get(reverse('profile_handler', kwargs={'user_id': 1}))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['service'], 'Django + PostgreSQL')
        self.assertEqual(data['data']['user_id'], 1)
        self.assertEqual(data['data']['bio'], 'Test Bio')
        self.assertEqual(data['data']['phone'], '+34 123 456 789')
        self.assertEqual(data['data']['address'], 'Test Address')
    
    def test_get_non_existing_profile(self):
        """Test GET: obtener perfil que no existe"""
        response = self.client.get(reverse('profile_handler', kwargs={'user_id': 999}))
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Perfil no encontrado para este usuario')
    
    def test_post_create_new_profile(self):
        """Test POST: crear nuevo perfil"""
        new_user_id = 2
        payload = {
            'bio': 'New User Bio',
            'phone': '+34 999 888 777',
            'address': 'New Address'
        }
        
        response = self.client.post(
            reverse('profile_handler', kwargs={'user_id': new_user_id}),
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        profile = Profile.objects.get(user_id=new_user_id)
        self.assertEqual(profile.bio, 'New User Bio')
        self.assertEqual(profile.phone, '+34 999 888 777')
    
    def test_post_update_existing_profile(self):
        """Test POST: actualizar perfil existente"""
        payload = {
            'bio': 'Updated Bio',
            'phone': '+34 555 666 777',
            'address': 'Updated Address'
        }
        
        response = self.client.post(
            reverse('profile_handler', kwargs={'user_id': 1}),
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        updated_profile = Profile.objects.get(user_id=1)
        self.assertEqual(updated_profile.bio, 'Updated Bio')
        self.assertEqual(updated_profile.phone, '+34 555 666 777')
        self.assertEqual(updated_profile.address, 'Updated Address')
    
    def test_post_with_partial_data(self):
        """Test POST: actualizar solo algunos campos"""
        payload = {
            'bio': 'Partially Updated'
        }
        
        response = self.client.post(
            reverse('profile_handler', kwargs={'user_id': 1}),
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        updated_profile = Profile.objects.get(user_id=1)
        self.assertEqual(updated_profile.bio, 'Partially Updated')
    
    def test_post_with_empty_payload(self):
        """Test POST: con datos vacíos"""
        new_user_id = 3
        payload = {}
        
        response = self.client.post(
            reverse('profile_handler', kwargs={'user_id': new_user_id}),
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        profile = Profile.objects.get(user_id=new_user_id)
        self.assertEqual(profile.bio, '')
    
    @patch('profiles.views.requests.post')
    def test_post_notifies_flask_on_create(self, mock_requests_post):
        """Test POST: verifica notificación a Flask en creación"""
        new_user_id = 4
        payload = {
            'bio': 'Created User',
            'phone': '+34 111 222 333'
        }
        mock_requests_post.return_value = MagicMock(status_code=200)
        
        self.client.post(
            reverse('profile_handler', kwargs={'user_id': new_user_id}),
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Verificar que se intentó notificar a Flask
        mock_requests_post.assert_called_once()
        call_args = mock_requests_post.call_args
        self.assertIn('http://127.0.0.1:5000/api/notify/user-data', call_args[0])
    
    @patch('profiles.views.requests.post')
    def test_post_notifies_flask_on_update(self, mock_requests_post):
        """Test POST: verifica notificación a Flask en actualización"""
        payload = {
            'bio': 'Updated User Bio'
        }
        mock_requests_post.return_value = MagicMock(status_code=200)
        
        self.client.post(
            reverse('profile_handler', kwargs={'user_id': 1}),
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Verificar que se intentó notificar a Flask
        mock_requests_post.assert_called_once()
        call_args = mock_requests_post.call_args
        self.assertEqual(call_args[1]['json']['action'], 'update')
    
    @patch('profiles.views.requests.post')
    def test_post_handles_flask_timeout(self, mock_requests_post):
        """Test POST: maneja timeout al contactar Flask"""
        import requests
        mock_requests_post.side_effect = requests.RequestException("Timeout")
        
        payload = {'bio': 'Test'}
        
        # Debe retornar 201 incluso si Flask no responde
        response = self.client.post(
            reverse('profile_handler', kwargs={'user_id': 5}),
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_invalid_user_id_type(self):
        """Test con user_id inválido en URL"""
        response = self.client.get('/api/users/profile/invalid')
        # Django devuelve 404 si la URL no coincide
        self.assertEqual(response.status_code, 404)
    
    def test_large_user_id(self):
        """Test con user_id muy grande"""
        large_user_id = 999999
        payload = {'bio': 'Large ID'}
        response = self.client.post(
            reverse('profile_handler', kwargs={'user_id': large_user_id}),
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        profile = Profile.objects.get(user_id=large_user_id)
        self.assertIsNotNone(profile)


class ProfileEdgeCase(TestCase):
    """Tests para casos extremos y validaciones especiales"""
    
    def test_unicode_characters_in_bio(self):
        """Test con caracteres Unicode en bio"""
        profile = Profile.objects.create(
            user_id=100,
            bio="Programador 👨‍💻 de España 🇪🇸",
            phone="+34 123"
        )
        self.assertIn("👨‍💻", profile.bio)
    
    def test_special_characters_in_fields(self):
        """Test con caracteres especiales"""
        profile = Profile.objects.create(
            user_id=101,
            bio="Bio with <html> & special chars",
            address="Street's Name, 123"
        )
        retrieved = Profile.objects.get(user_id=101)
        self.assertEqual(retrieved.bio, "Bio with <html> & special chars")
    
    def test_null_values_allowed(self):
        """Verifica que los valores null se permiten para ciertos campos"""
        profile = Profile.objects.create(user_id=102)
        self.assertIsNone(profile.bio)
        self.assertIsNone(profile.phone)
        self.assertIsNone(profile.address)
    
    def test_whitespace_handling(self):
        """Test con espacios en blanco"""
        profile = Profile.objects.create(
            user_id=103,
            bio="   Bio with spaces   ",
            phone="  +34 123 456  "
        )
        retrieved = Profile.objects.get(user_id=103)
        # No se trimean automáticamente en Django
        self.assertIn("   ", retrieved.bio)