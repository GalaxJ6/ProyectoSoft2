<?php
namespace Tests\Feature;
use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;

class AuthTest extends TestCase {
    use RefreshDatabase;

    public function test_user_can_register() {
        $response = $this->postJson('/api/register', [
            'name' => 'Test User',
            'email' => 'test@example.com',
            'password' => 'password123',
            'password_confirmation' => 'password123',
            'security_question' => 'Pet?',
            'security_answer' => 'Dog'
        ]);
        $response->assertStatus(201)->assertJsonStructure(['access_token']);
    }

    public function test_user_can_login() {
        // Primero registramos
        $this->postJson('/api/register', [
            'name' => 'User', 'email' => 'u@e.com', 'password' => '12345678', 
            'password_confirmation' => '12345678', 'security_question' => 'Q', 'security_answer' => 'A'
        ]);

        $response = $this->postJson('/api/login', ['email' => 'u@e.com', 'password' => '12345678']);
        $response->assertStatus(200)->assertJsonStructure(['token']);
    }

    public function test_password_recovery() {
        $this->postJson('/api/register', [
            'name' => 'User', 'email' => 'u@e.com', 'password' => '12345678', 
            'password_confirmation' => '12345678', 'security_question' => 'Q', 'security_answer' => 'MyAnswer'
        ]);

        $response = $this->postJson('/api/recovery', [
            'email' => 'u@e.com',
            'security_answer' => 'MyAnswer',
            'new_password' => 'new12345678',
            'new_password_confirmation' => 'new12345678'
        ]);
        $response->assertStatus(200);
    }
}