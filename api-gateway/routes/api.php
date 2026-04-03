<?php

use App\Http\Controllers\AuthController;
use App\Models\User;
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

        // --- VALIDACIÓN ESPECÍFICA PARA EL SERVICIO 'users' ---
        if ($service === 'users' && strpos($path, 'profile/') !== false) {
            // Extraer el ID del usuario de la ruta (ej: profile/1 -> user_id = 1)
            preg_match('/profile\/(\d+)/', $path, $matches);
            
            if (isset($matches[1])) {
                $user_id = intval($matches[1]);
                
                // Verificar si el usuario existe en la BD de Laravel
                $user = User::find($user_id);
                
                if (!$user) {
                    return response()->json(
                        ['error' => "El usuario con ID $user_id no existe en el sistema de Laravel"],
                        404
                    );
                }
            }
        }

        // Construimos la URL final (ej: http://localhost:8001/api/users/profile/1)
        $url = $map[$service] . '/' . $service . '/' . $path;

        // Reenviamos la petición, pero filtramos headers que causan problemas
        $headers = collect(request()->headers->all())
            ->except(['host', 'connection', 'content-length'])
            ->map(fn($value) => $value[0] ?? $value)
            ->toArray();

        // Preparamos el contenido del cuerpo
        $body = request()->getContent();
        
        // Reenviamos según el método HTTP
        $client = Http::withHeaders($headers);
        
        if (request()->method() === 'GET') {
            $response = $client->get($url);
        } else {
            $response = $client->send(request()->method(), $url, ['body' => $body]);
        }

        // Retornamos la respuesta del microservicio tal cual la recibimos
        return response()->json($response->json(), $response->status());

    })->where('path', '.*'); // El '.*' permite que el path tenga varias barras (ej: /v1/search)

});