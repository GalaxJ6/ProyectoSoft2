<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\{Hash, Validator};

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

        // 1. Creamos el usuario
        $user = User::create([
            'name' => $request->name,
            'email' => $request->email,
            'password' => Hash::make($request->password),
            'security_question' => $request->security_question,
            'security_answer' => Hash::make(strtolower($request->security_answer)),
        ]);

        // 2. GENERAMOS EL TOKEN INMEDIATAMENTE (Aquí está el truco)
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
        // Revocar (borrar) el token que se está usando en esta petición
        $request->user()->currentAccessToken()->delete();

        return response()->json([
            'message' => 'Sesión cerrada exitosamente. El token ha sido eliminado.'
        ], 200);
    }
}