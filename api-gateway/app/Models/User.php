<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;


    protected $fillable = [
        'name',
        'email',
        'password',
        'security_question',
        'security_answer',
    ];


    protected $hidden = [
        'password',
        'remember_token',
        'security_answer',
    ];


    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'password' => 'hashed',          // Encripta la contraseña
            'security_answer' => 'hashed',   // Encripta la respuesta secreta
        ];
    }
}