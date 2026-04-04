<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class ProductController extends Controller
{
    /**
     * Orquestación: Envía datos a FastAPI, luego a Express y finalmente a Flask.
     */
    public function store(Request $request)
    {
        // VALIDACIÓN EN EL GATEWAY
        $data = $request->validate([
            'name'        => 'required|string',
            'price'       => 'required|numeric',
            'description' => 'required|string',
            'stock'       => 'required|integer',
            'category'    => 'required|string',
            'user_id'     => 'required|integer' // ID del usuario autenticado en Laravel
        ]);

        try {
            // LLAMADA A FASTAPI (MS_LOGIC - Puerto 8050)
            // Enviamos el precio para calcular el IVA del 19%
            $logicResponse = Http::post('http://127.0.0.1:8050/api/logic/calculate-tax', [
                'price' => $data['price']
            ]);

            if ($logicResponse->successful()) {
                // Reemplazamos el precio original por el precio con IVA devuelto por FastAPI
                $data['price'] = $logicResponse->json()['total_price'];
            }

            // LLAMADA A EXPRESS (MS_CATALOG - Puerto 3000)
            // Enviamos el producto final para persistencia en MongoDB 
            $catalogResponse = Http::post('http://127.0.0.1:3000/api/catalog/products', $data);

            if ($catalogResponse->failed()) {
                return response()->json(['error' => 'Error al guardar en el catálogo de MongoDB'], 500);
            }

            // LLAMADA A FLASK (MS_NOTIFY - Puerto 5000) 
            // Registramos el evento (Log)
            try {
                Http::post(env('MS_NOTIFY_URL') . '/api/notify/products', [
                    'user_id' => $data['user_id'],
                    'action' => 'create',
                    'query' => $data['name']
                ]);
            } catch (\Exception $e) {
            }

            return response()->json([
                'message' => 'Flujo completado exitosamente',
                'final_product' => $catalogResponse->json()
            ], 201);

        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Error de comunicación entre microservicios',
                'details' => $e->getMessage()
            ], 500);
        }
    }
}