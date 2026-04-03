<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\{Hash, Validator};
use Illuminate\Support\Facades\Http;

class AuthController extends Controller {
    public function register(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255',
            'email' => 'required|string|email|max:255|unique:users',
            'password' => 'required|string|min:8|confirmed',
            'security_question' => 'required|string',
            'security_answer' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json($validator->errors(), 400);
        }

        // 1. Creamos el usuario en MySQL (Laravel)
        $user = User::create([
            'name' => $request->name,
            'email' => $request->email,
            'password' => Hash::make($request->password),
            'security_question' => $request->security_question,
            'security_answer' => Hash::make(strtolower($request->security_answer)),
        ]);

        // --- 🚀 INTEGRACIÓN CON FLASK (MS_NOTIFY) ---
        // Registramos el evento de creación de usuario para auditoría
        try {
            Http::post(env('MS_NOTIFY_URL') . '/api/notify/login', [
                'user_id' => $user->id,
                'username' => $user->email
            ]);
        } catch (\Exception $e) {
            // Opcional: Loguear el error internamente si Flask está caído
            // pero permitir que el registro continúe.
        }
        // --------------------------------------------

        // 2. GENERAMOS EL TOKEN INMEDIATAMENTE
        $token = $user->createToken('auth_token')->plainTextToken;

        // 3. Devolvemos el usuario Y el token
        return response()->json([
            'message' => 'Usuario registrado e iniciado con éxito',
            'access_token' => $token,
            'token_type' => 'Bearer',
            'user' => $user
        ], 201);
    }

    public function login(Request $request) {
        $user = User::where('email', $request->email)->first();

        if (!$user || !Hash::check($request->password, $user->password)) {
            return response()->json(['msg' => 'Credenciales Fallidas'], 401);
        }

        // Enviar log a Flask (ms_notify)
        try {
            Http::post(env('MS_NOTIFY_URL') . '/api/notify/login', [
                'user_id' => $user->id,
                'username' => $user->email
            ]);
        } catch (\Exception $e) {
            // Ignorar error de logging para no romper auth
        }

        return response()->json([
            'message' => 'Logeo exitoso',
            'token' => $user->createToken('api')->plainTextToken,
            'user' => [
                'name' => $user->name,
                'email' => $user->email
            ]
        ], 200);
    }

    public function recovery(Request $request) {
        $request->validate([
            'email' => 'required|email', 
            'security_answer' => 'required|string', 
            'new_password' => 'required|string|min:8|confirmed'
        ]);

        $user = User::where('email', $request->email)->first();

        if (!$user || !Hash::check(strtolower($request->security_answer), $user->security_answer)) {
            return response()->json(['message' => 'Respuesta de seguridad incorrecta'], 403);
        }

        // 1. Actualizamos la contraseña
        $user->update([
            'password' => Hash::make($request->new_password)
        ]);

        // 2. GENERAMOS EL TOKEN (Igual que en el Register)
        $token = $user->createToken('auth_token')->plainTextToken;

        // Log en Flask
        try {
            Http::post(env('MS_NOTIFY_URL') . '/api/notify/recovery', [
                'user_id' => $user->id,
                'email' => $user->email
            ]);
        } catch (\Exception $e) {
            // Ignorar error de logging
        }

        // 3. Devolvemos éxito Y el nuevo token
        return response()->json([
            'message' => 'Contraseña actualizada y sesión iniciada',
            'access_token' => $token,
            'token_type' => 'Bearer',
            'user' => $user->email
        ], 200);
    }

    public function logout(Request $request)
    {
        $user = $request->user();
        // Revocar (borrar) el token que se está usando en esta petición
        $request->user()->currentAccessToken()->delete();

        // Log en Flask
        try {
            Http::post(env('MS_NOTIFY_URL') . '/api/notify/logout', [
                'user_id' => $user->id
            ]);
        } catch (\Exception $e) {
            // Continuar sin bloquear al logout
        }

        return response()->json([
            'message' => 'Sesión cerrada exitosamente. El token ha sido eliminado.'
        ], 200);
    }
}