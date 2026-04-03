<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;

    /**
     * Campos que se pueden llenar masivamente.
     * Añadimos los campos de seguridad requeridos.
     */
    protected $fillable = [
        'name',
        'email',
        'password',
        'security_question',
        'security_answer',
    ];

    /**
     * Campos que se ocultan cuando la API responde (JSON).
     * Ocultamos la respuesta de seguridad por privacidad.
     */
    protected $hidden = [
        'password',
        'remember_token',
        'security_answer',
    ];

    /**
     * Define el comportamiento de los datos.
     */
    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'password' => 'hashed',          // Encripta la contraseña
            'security_answer' => 'hashed',   // Encripta la respuesta secreta
        ];
    }
}