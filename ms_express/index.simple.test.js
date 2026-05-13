const request = require('supertest');
const createTestApp = require('./test.utils');

describe('Product Catalog API - Express (Tests Simplificados)', () => {
    let app;

    beforeAll(() => {
        app = createTestApp();
    });

    describe('POST /api/catalog/products - Crear Producto', () => {
        
        test('Debe crear un producto válido correctamente', async () => {
            const productData = {
                name: 'Laptop Dell',
                description: 'Laptop de 15 pulgadas',
                price: 999.99,
                category: 'Electrónica',
                user_id: 1
            };
            
            const response = await request(app)
                .post('/api/catalog/products')
                .send(productData);
            
            expect(response.status).toBe(201);
            expect(response.body).toHaveProperty('message');
            expect(response.body).toHaveProperty('data');
            expect(response.body.data.name).toBe('Laptop Dell');
        });
        
        test('Debe retornar 400 cuando falta el nombre', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ price: 100, user_id: 1, description: 'Test', category: 'Test' })
                .expect(400);
            
            expect(response.body).toHaveProperty('error');
        });
        
        test('Debe retornar 400 cuando nombre no es string', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ name: 123, price: 100, user_id: 1, description: 'Test', category: 'Test' })
                .expect(400);
            
            expect(response.body.error).toContain('texto válido');
        });
        
        test('Debe retornar 400 cuando falta el precio', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ name: 'Test', user_id: 1, description: 'Test', category: 'Test' })
                .expect(400);
            
            expect(response.body).toHaveProperty('error');
        });
        
        test('Debe retornar 400 cuando precio es negativo', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ name: 'Test', price: -100, user_id: 1, description: 'Test', category: 'Test' })
                .expect(400);
            
            expect(response.body.error).toContain('mayor a 0');
        });
        
        test('Debe retornar 400 cuando precio es cero', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ name: 'Test', price: 0, user_id: 1, description: 'Test', category: 'Test' })
                .expect(400);
            
            expect(response.body.error).toContain('mayor a 0');
        });
        
        test('Debe retornar 400 cuando falta user_id', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ name: 'Test', price: 100, description: 'Test', category: 'Test' })
                .expect(400);
            
            expect(response.body.error).toContain('user_id');
        });
        
        test('Debe retornar 400 cuando user_id no es válido', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ name: 'Test', price: 100, user_id: 'invalid', description: 'Test', category: 'Test' })
                .expect(400);
            
            expect(response.body.error).toContain('numérico');
        });
        
        test('Debe manejar caracteres especiales en campos', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ 
                    name: 'Laptop <Dell> & Compaq', 
                    price: 100, 
                    user_id: 1, 
                    description: 'Test', 
                    category: 'Test' 
                });
            
            expect(response.status).toBe(201);
        });
        
        test('Debe manejar Unicode en campos', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ 
                    name: 'Portátil', 
                    price: 100, 
                    user_id: 1, 
                    description: 'Descripción en español', 
                    category: 'Electrónica' 
                });
            
            expect(response.status).toBe(201);
        });

        test('Debe manejar números grandes', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ 
                    name: 'Producto caro', 
                    price: 999999999.99, 
                    user_id: 999999999, 
                    description: 'Test', 
                    category: 'Lujo' 
                });
            
            expect(response.status).toBe(201);
        });

        test('Respuesta debe tener estructura correcta', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ 
                    name: 'Test', 
                    price: 100, 
                    user_id: 1, 
                    description: 'Desc', 
                    category: 'Cat' 
                });
            
            expect(response.status).toBe(201);
            expect(response.body).toHaveProperty('message');
            expect(response.body).toHaveProperty('data');
            expect(response.body.data).toHaveProperty('_id');
        });

        test('Debe manejar payload vacío', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({})
                .expect(400);
            
            expect(response.body).toHaveProperty('error');
        });
    });

    describe('GET /api/catalog/products', () => {
        
        test('Debe retornar lista de productos', async () => {
            const response = await request(app)
                .get('/api/catalog/products')
                .expect(200);
            
            expect(Array.isArray(response.body)).toBe(true);
        });

        test('Respuesta debe ser JSON', async () => {
            const response = await request(app)
                .get('/api/catalog/products');
            
            expect(response.headers['content-type']).toMatch(/json/);
        });
    });

    describe('Validación de Middleware', () => {
        
        test('Middleware valida campos requeridos', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ price: 100, user_id: 1 })
                .expect(400);
            
            expect(response.body).toHaveProperty('error');
        });

        test('Middleware valida tipos de datos', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ name: 123, price: 100, user_id: 1 });
            
            expect(response.status).toBe(400);
        });

        test('Middleware valida rango de valores', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ name: 'Test', price: -50, user_id: 1, description: 'Test', category: 'Test' });
            
            expect(response.status).toBe(400);
        });
    });

    describe('Casos Extremos', () => {
        
        test('Nombre con mucha longitud', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ 
                    name: 'x'.repeat(5000), 
                    price: 100, 
                    user_id: 1,
                    description: 'Test',
                    category: 'Test'
                });
            
            expect([200, 201, 400]).toContain(response.status);
        });

        test('Descripción con mucha longitud', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ 
                    name: 'Test', 
                    price: 100, 
                    user_id: 1,
                    description: 'x'.repeat(10000),
                    category: 'Test'
                });
            
            expect([200, 201, 400]).toContain(response.status);
        });

        test('Espacios en blanco en campos string', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ 
                    name: '   Test Product   ', 
                    price: 100, 
                    user_id: 1,
                    description: '   Description   ',
                    category: 'Test'
                });
            
            expect(response.status).toBe(201);
        });
    });

    describe('Métodos HTTP', () => {
        
        test('GET debe ser permitido', async () => {
            const response = await request(app)
                .get('/api/catalog/products');
            
            expect(response.status).toBe(200);
        });

        test('POST debe ser permitido', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ 
                    name: 'Test', 
                    price: 100, 
                    user_id: 1,
                    description: 'Test',
                    category: 'Test'
                });
            
            expect(response.status).toBe(201);
        });

        test('PUT no debe existir', async () => {
            const response = await request(app)
                .put('/api/catalog/products')
                .send({});
            
            expect(response.status).toBe(404);
        });

        test('DELETE no debe existir', async () => {
            const response = await request(app)
                .delete('/api/catalog/products');
            
            expect(response.status).toBe(404);
        });
    });

    describe('Content-Type', () => {
        
        test('Debe aceptar application/json', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .set('Content-Type', 'application/json')
                .send({ 
                    name: 'Test', 
                    price: 100, 
                    user_id: 1,
                    description: 'Test',
                    category: 'Test'
                });
            
            expect(response.status).toBe(201);
        });

        test('Respuesta debe ser application/json', async () => {
            const response = await request(app)
                .get('/api/catalog/products');
            
            expect(response.headers['content-type']).toMatch(/application\/json/);
        });
    });

    describe('Respuestas de Error', () => {
        
        test('Error debe contener mensaje descriptivo', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ name: 'Test', price: -100, user_id: 1, description: 'Test', category: 'Test' });
            
            expect(response.body.error).toBeTruthy();
            expect(response.body.error.length).toBeGreaterThan(0);
        });

        test('400 debe devolver error JSON', async () => {
            const response = await request(app)
                .post('/api/catalog/products')
                .send({ name: 123, price: 100, user_id: 1 });
            
            expect(response.status).toBe(400);
            expect(response.body).toHaveProperty('error');
        });
    });

    describe('Persisitencia en Sesión', () => {
        
        test('Los productos creados deben ser recuperables', async () => {
            // Crear
            const createResponse = await request(app)
                .post('/api/catalog/products')
                .send({ 
                    name: 'Producto Recuperable', 
                    price: 150, 
                    user_id: 123,
                    description: 'Test',
                    category: 'Test'
                });
            
            expect(createResponse.status).toBe(201);

            // Recuperar
            const getResponse = await request(app)
                .get('/api/catalog/products');
            
            expect(getResponse.status).toBe(200);
            expect(getResponse.body.length).toBeGreaterThan(0);
        });
    });
});
