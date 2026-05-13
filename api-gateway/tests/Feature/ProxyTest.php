<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\WithFaker;
use Tests\TestCase;

class ProxyTest extends TestCase
{
    /**
     * A basic feature test example.
     */
    public function test_protected_routes_fail_without_token() {
        $this->postJson('/api/products')->assertStatus(401);
        $this->getJson('/api/catalog/products')->assertStatus(401);
        $this->getJson('/api/users/profile/1')->assertStatus(401);
    }
}
