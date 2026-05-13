// Tests Simplificados para Express sin MongoDB
const express = require('express');
const cors = require('cors');

// Crear una versión simplificada del app para testing
const createTestApp = () => {
    const app = express();
    app.use(express.json());
    app.use(cors());

    // Mock del Product Model
    const products = [];

    const validateProductData = (req, res, next) => {
        const { name, price, user_id } = req.body;
        
        if (!name || typeof name !== 'string') {
            return res.status(400).json({ error: "Validación fallida: El nombre debe ser un texto válido." });
        }
        if (isNaN(price) || price <= 0) {
            return res.status(400).json({ error: "Validación fallida: El precio debe ser un número mayor a 0." });
        }
        if (!user_id || isNaN(user_id)) {
            return res.status(400).json({ error: "Validación fallida: Se requiere un user_id numérico válido." });
        }
        next();
    };

    app.post('/api/catalog/products', validateProductData, (req, res) => {
        try {
            const newProduct = {
                _id: `${Date.now()}`,
                ...req.body
            };
            products.push(newProduct);
            res.status(201).json({
                message: "Producto guardado con éxito",
                id_mongo: newProduct._id,
                data: newProduct
            });
        } catch (error) {
            res.status(400).json({ 
                error: "Error al guardar en la base de datos", 
                details: error.message 
            });
        }
    });

    app.get('/api/catalog/products', (req, res) => {
        try {
            res.json(products);
        } catch (error) {
            res.status(500).json({ error: "Error al obtener los productos" });
        }
    });

    return app;
};

module.exports = createTestApp;
