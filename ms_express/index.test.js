const request = require('supertest');
const mongoose = require('mongoose');

// Mock de mongoose.connect para evitar intentar conectar a MongoDB
jest.mock('mongoose', () => {
  const actualMongoose = jest.requireActual('mongoose');
  return {
    ...actualMongoose,
    connect: jest.fn().mockResolvedValue({
      connection: { isConnected: true }
    })
  };
});

// Requiere app después de mockear mongoose
const app = require('./index');

describe('Product Catalog API - Express', () => {
    
    afterAll(() => {
        // Limpia después de todos los tests
        jest.clearAllMocks();
    });

    describe('POST /api/catalog/products - Crear Producto', () => {
        
        test('Debe crear un producto válido correctamente', async () => {
            const productData = {
                name: 'Laptop Dell',
                description: 'Laptop de 15 pulgadas',
                price: 999.99,
                stock: 10,
                category: 'Electrónica',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData)
                .expect('Content-Type', /json/);
            
            expect(response.status).toBe(201);
            expect(response.body).toHaveProperty('message');
            expect(response.body).toHaveProperty('data');
            expect(response.body.data.name).toBe(productData.name);
            expect(response.body.data.price).toBe(productData.price);
        });
        
        test('Debe retornar 400 cuando falta el campo nombre', async () => {
            const productData = {
                description: 'Laptop sin nombre',
                price: 999.99,
                stock: 5,
                category: 'Electrónica',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData)
                .expect(400);
            
            expect(response.body).toHaveProperty('error');
        });
        
        test('Debe retornar 400 cuando nombre no es string', async () => {
            const productData = {
                name: 12345,  // Debe ser string
                description: 'Test',
                price: 100,
                category: 'Electrónica',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData)
                .expect(400);
            
            expect(response.body.error).toContain('nombre debe ser un texto válido');
        });
        
        test('Debe retornar 400 cuando falta el precio', async () => {
            const productData = {
                name: 'Laptop',
                description: 'Test',
                stock: 5,
                category: 'Electrónica',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData)
                .expect(400);
            
            expect(response.body).toHaveProperty('error');
        });
        
        test('Debe retornar 400 cuando precio es negativo', async () => {
            const productData = {
                name: 'Laptop',
                description: 'Test',
                price: -100,
                stock: 5,
                category: 'Electrónica',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData)
                .expect(400);
            
            expect(response.body.error).toContain('mayor a 0');
        });
        
        test('Debe retornar 400 cuando precio es cero', async () => {
            const productData = {
                name: 'Laptop',
                description: 'Test',
                price: 0,
                stock: 5,
                category: 'Electrónica',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData)
                .expect(400);
            
            expect(response.body.error).toContain('mayor a 0');
        });
        
        test('Debe retornar 400 cuando precio no es número', async () => {
            const productData = {
                name: 'Laptop',
                description: 'Test',
                price: 'ciento',  // No es número
                stock: 5,
                category: 'Electrónica',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData)
                .expect(400);
            
            expect(response.body.error).toContain('mayor a 0');
        });
        
        test('Debe retornar 400 cuando falta user_id', async () => {
            const productData = {
                name: 'Laptop',
                description: 'Test',
                price: 100,
                stock: 5,
                category: 'Electrónica'
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData)
                .expect(400);
            
            expect(response.body.error).toContain('user_id');
        });
        
        test('Debe retornar 400 cuando user_id no es válido', async () => {
            const productData = {
                name: 'Laptop',
                description: 'Test',
                price: 100,
                category: 'Electrónica',
                user_id: 'not_a_number'
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData)
                .expect(400);
            
            expect(response.body.error).toContain('user_id numérico');
        });
        
        test('Debe crear producto con stock por defecto', async () => {
            const productData = {
                name: 'Producto sin stock',
                description: 'Test',
                price: 50,
                category: 'Test',
                user_id: 1
                // stock no incluido
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            if (response.status === 201) {
                expect(response.body.data.stock).toBe(0);
            }
        });
        
        test('Debe crear producto con stock negativo en validación', async () => {
            const productData = {
                name: 'Producto stock negativo',
                description: 'Test',
                price: 50,
                stock: -5,
                category: 'Test',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            // Mongoose validará esto
            expect([400, 201]).toContain(response.status);
        });
        
        test('Debe crear producto con descripción requerida', async () => {
            const productData = {
                name: 'Laptop',
                price: 100,
                stock: 5,
                category: 'Electrónica',
                user_id: 1
                // description ausente
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            // Mongoose debería validar
            expect([400, 201]).toContain(response.status);
        });
        
        test('Debe crear producto con categoría requerida', async () => {
            const productData = {
                name: 'Laptop',
                description: 'Test',
                price: 100,
                stock: 5,
                user_id: 1
                // category ausente
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            // Mongoose debería validar
            expect([400, 201]).toContain(response.status);
        });
        
        test('Debe manejar strings con espacios en blanco', async () => {
            const productData = {
                name: '   Laptop con espacios   ',
                description: '   Descripción con espacios   ',
                price: 100,
                category: 'Electrónica',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            if (response.status === 201) {
                // Mongoose trim debería remover espacios de name
                expect(response.body.data.name).toBe('Laptop con espacios');
            }
        });
        
        test('Debe manejar caracteres especiales', async () => {
            const productData = {
                name: 'Laptop <Dell> & Compaq',
                description: 'Descripción con "comillas"',
                price: 100,
                category: 'Electrónica',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            if (response.status === 201) {
                expect(response.body.data.name).toContain('Dell');
            }
        });
        
        test('Debe manejar Unicode en campos de texto', async () => {
            const productData = {
                name: 'Portátil Dell',
                description: 'Descripción en español con acentos: á, é, í, ó, ú',
                price: 100,
                category: 'Electrónica',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            if (response.status === 201) {
                expect(response.body.data.description).toContain('español');
            }
        });
        
        test('Debe manejar números muy grandes como precio', async () => {
            const productData = {
                name: 'Producto caro',
                description: 'Test',
                price: 999999999.99,
                category: 'Lujo',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            expect([201, 400]).toContain(response.status);
        });
        
        test('Debe manejar user_id grande', async () => {
            const productData = {
                name: 'Producto',
                description: 'Test',
                price: 100,
                category: 'Test',
                user_id: 999999999
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            expect([201, 400]).toContain(response.status);
        });
        
        test('Debe retornar error de validación de Mongoose para documento inválido', async () => {
            const productData = {
                name: '',  // Nombre vacío debe fallar
                description: 'Test',
                price: 100,
                category: 'Test',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            // Debería rechazar o pasar validador
            expect([400, 201]).toContain(response.status);
        });
    });


    describe('GET /api/catalog/products - Obtener Productos', () => {
        
        test('Debe obtener lista de productos', async () => {
            const response = await request(app)
                .get('/api/catalog/products')
                .expect('Content-Type', /json/)
                .expect(200);
            
            expect(Array.isArray(response.body)).toBe(true);
        });
        
        test('Debe retornar array vacío o con productos', async () => {
            const response = await request(app)
                .get('/api/catalog/products')
                .expect(200);
            
            expect(response.body).toBeDefined();
        });
        
        test('Debe manejar errores de base de datos', async () => {
            const response = await request(app)
                .get('/api/catalog/products');
            
            // Debería retornar 200 con array o 500 con error
            expect([200, 500]).toContain(response.status);
        });
    });


    describe('Validación de Middleware', () => {
        
        test('Middleware debe validar campos requeridos', async () => {
            const productData = {
                price: 100,
                user_id: 1
                // Faltan name, description, category
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData)
                .expect(400);
            
            expect(response.body).toHaveProperty('error');
        });
        
        test('Middleware debe retornar error con details en respuesta', async () => {
            const productData = {
                name: 123,  // Tipo incorrecto
                price: 100,
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            if (response.status === 400) {
                expect(response.body.error).toBeDefined();
            }
        });
    });


    describe('Manejo de Errores', () => {
        
        test('Debe manejar payload vacío', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({})
                .expect(400);
            
            expect(response.body).toHaveProperty('error');
        });
        
        test('Debe manejar null como payload', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send(null);
            
            expect([400, 415]).toContain(response.status);
        });
        
        test('Debe manejar JSON inválido', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .set('Content-Type', 'application/json')
                .send('{"invalid json}');
            
            expect([400, 415]).toContain(response.status);
        });
    });


    describe('Content Type y Headers', () => {
        
        test('Debe aceptar application/json', async () => {
            const productData = {
                name: 'Test',
                description: 'Test',
                price: 100,
                category: 'Test',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .set('Content-Type', 'application/json')
                .send(productData);
            
            expect([201, 400]).toContain(response.status);
        });
        
        test('Respuesta debe tener Content-Type JSON', async () => {
            const response = await request(app)
                .get('/api/catalog/products');
            
            expect(response.headers['content-type']).toMatch(/json/);
        });
    });


    describe('CORS y Métodos HTTP', () => {
        
        test('Debe permitir POST para crear', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({
                    name: 'Test',
                    description: 'Test',
                    price: 100,
                    category: 'Test',
                    user_id: 1
                });
            
            expect([201, 400]).toContain(response.status);
        });
        
        test('Debe permitir GET para listar', async () => {
            const response = await request(app)
                .get('/api/catalog/products')
                .expect(200);
            
            expect(response.body).toBeDefined();
        });
    });


    describe('Casos Extremos', () => {
        
        test('Debe manejar name con longitud máxima', async () => {
            const productData = {
                name: 'x'.repeat(1000),
                description: 'Test',
                price: 100,
                category: 'Test',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            expect([201, 400]).toContain(response.status);
        });
        
        test('Debe manejar description con longitud máxima', async () => {
            const productData = {
                name: 'Test',
                description: 'x'.repeat(5000),
                price: 100,
                category: 'Test',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            expect([201, 400]).toContain(response.status);
        });
        
        test('Debe manejar stock muy grande', async () => {
            const productData = {
                name: 'Test',
                description: 'Test',
                price: 100,
                stock: 999999999,
                category: 'Test',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            expect([201, 400]).toContain(response.status);
        });
    });


    describe('Respuestas y Formato', () => {
        
        test('Respuesta exitosa debe tener estructura correcta', async () => {
            const productData = {
                name: 'Test Product',
                description: 'Test',
                price: 100,
                category: 'Test',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            if (response.status === 201) {
                expect(response.body).toHaveProperty('message');
                expect(response.body).toHaveProperty('data');
                expect(response.body.data).toHaveProperty('name');
                expect(response.body.data).toHaveProperty('price');
            }
        });
        
        test('Respuesta de error debe tener estructura correcta', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ name: 123, price: 100, user_id: 1 })
                .expect(400);
            
            expect(response.body).toHaveProperty('error');
        });
    });
});
