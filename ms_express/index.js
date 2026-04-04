const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(express.json()); 
app.use(cors());         

mongoose.connect('mongodb://127.0.0.1:27017/proyecto')
    .then(() => console.log("MongoDB Conectado"))
    .catch(err => console.error("Error de conexión:", err));


const ProductSchema = new mongoose.Schema({
    name: { 
        type: String, 
        required: [true, 'El nombre es obligatorio'],
        trim: true 
    },
    description: { 
        type: String, 
        required: [true, 'La descripción es obligatoria'] 
    },
    price: { 
        type: Number, 
        required: [true, 'El precio es obligatorio'],
        min: [0, 'El precio no puede ser negativo'] 
    },
    stock: { 
        type: Number, 
        default: 0,
        min: [0, 'El stock no puede ser negativo'] 
    },
    category: { 
        type: String, 
        required: [true, 'La categoría es obligatoria'] 
    },
    user_id: { 
        type: Number, 
        required: [true, 'El ID de usuario es obligatorio para la trazabilidad'] 
    }
});

const Product = mongoose.model('Product', ProductSchema);


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


app.post('/api/catalog/products', validateProductData, async (req, res) => {
    try {
        const nuevoProducto = new Product(req.body);
        await nuevoProducto.save();
        res.status(201).json({
            message: "Producto guardado con éxito",
            id_mongo: nuevoProducto._id,
            data: nuevoProducto
        });
    } catch (error) {
        // Captura errores de validación de Mongoose
        res.status(400).json({ 
            error: "Error al guardar en la base de datos", 
            details: error.message 
        });
    }
});

app.get('/api/catalog/products', async (req, res) => {
    try {
        const productos = await Product.find();
        res.json(productos);
    } catch (error) {
        res.status(500).json({ error: "Error al obtener los productos" });
    }
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Microservicio Catálogo (Express) listo en puerto ${PORT}`);
});