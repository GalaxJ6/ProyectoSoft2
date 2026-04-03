from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Profile
import requests

@api_view(['GET', 'POST'])
def profile_handler(request, user_id):
    
    # --- MÉTODO GET: Consultar datos de un usuario ---
    if request.method == 'GET':
        try:
            profile = Profile.objects.get(user_id=user_id)
            return Response({
                "service": "Django + PostgreSQL",
                "data": {
                    "user_id": profile.user_id,
                    "bio": profile.bio,
                    "phone": profile.phone,
                    "address": profile.address
                }
            }, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({"error": "Perfil no encontrado para este usuario"}, status=status.HTTP_404_NOT_FOUND)

    # --- MÉTODO POST: Crear o Actualizar datos de un usuario ---
    if request.method == 'POST':
        # update_or_create busca por user_id, si existe lo actualiza, si no lo crea.
        profile, created = Profile.objects.update_or_create(
            user_id=user_id,
            defaults={
                'bio': request.data.get('bio', ''),
                'phone': request.data.get('phone', ''),
                'address': request.data.get('address', '')
            }
        )

        # Informar a Flask (MS_NOTIFY) sobre cambios en datos de perfil
        try:
            requests.post('http://127.0.0.1:5000/api/notify/user-data', json={
                'user_id': user_id,
                'action': 'create' if created else 'update',
                'fields': {
                    'bio': request.data.get('bio', ''),
                    'phone': request.data.get('phone', ''),
                    'address': request.data.get('address', '')
                }
            }, timeout=3)
        except requests.RequestException:
            pass
        
        return Response({
            "status": "success",
            "message": "Perfil procesado correctamente",
            "action": "created" if created else "updated",
            "user_id": user_id
        }, status=status.HTTP_201_CREATED)
