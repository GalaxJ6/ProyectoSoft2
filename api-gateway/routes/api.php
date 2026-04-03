<?php

use App\Http\Controllers\AuthController;
use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Http;

/*
|--------------------------------------------------------------------------
| API Routes - Gateway Principal
|--------------------------------------------------------------------------
*/

// --- RUTAS PÚBLICAS DE AUTENTICACIÓN ---
// Estas rutas no requieren Token porque son para entrar al sistema
Route::post('/register', [AuthController::class, 'register']);
Route::post('/login', [AuthController::class, 'login']);
Route::post('/recovery', [AuthController::class, 'recovery']);


// --- RUTAS PROTEGIDAS (PROXY DINÁMICO) ---
// Solo usuarios con un Token de Sanctum válido pueden usar estos servicios
Route::middleware('auth:sanctum')->group(function () {

    Route::post('/logout', [AuthController::class, 'logout']);
    /**
     * Esta ruta captura cualquier petición hacia /{servicio}/{ruta}
     * Ejemplo: POST /api/catalog/products -> Redirige al Microservicio de Node.js
     */
    Route::any('/{service}/{path}', function ($service, $path) {
        
        // Mapeo de prefijos a las URLs definidas en tu archivo .env
        $map = [
            'users'   => env('MS_USERS_URL'),   // Django (Puerto 8001)
            'catalog' => env('MS_CATALOG_URL'), // Express (Puerto 3000)
            'logic'   => env('MS_LOGIC_URL'),   // FastAPI (Puerto 8080)
            'notify'  => env('MS_NOTIFY_URL'),  // Flask (Puerto 5000)
        ];

        // Validamos si el servicio solicitado existe en nuestro mapa
        if (!isset($map[$service])) {
            return response()->json(['error' => 'El microservicio solicitado no existe'], 404);
        }

        // Construimos la URL final (ej: http://localhost:3000/api/products)
        $url = $map[$service] . '/' . $path;

        // Reenviamos la petición con TODO:
        // 1. Headers originales (incluyendo el Token)
        // 2. Método original (GET, POST, PUT, DELETE)
        // 3. Body original (JSON con los datos)
        $response = Http::withHeaders(request()->headers->all())
            ->send(request()->method(), $url, request()->all());

        // Retornamos la respuesta del microservicio tal cual la recibimos
        return response()->json($response->json(), $response->status());

    })->where('path', '.*'); // El '.*' permite que el path tenga varias barras (ej: /v1/search)

});