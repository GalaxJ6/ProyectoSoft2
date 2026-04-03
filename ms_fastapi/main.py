from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Definimos el esquema que espera el servicio
class Item(BaseModel):
    price: float

@app.post("/api/logic/calculate-tax")
async def calculate_tax(item: Item):
    # Validación: Si el precio es menor o igual a 0, lanzamos error
    if item.price <= 0:
        return {"error": "El precio debe ser mayor a 0"}, 400
    
    tax = item.price * 0.19
    total = item.price + tax
    return {"total_price": total}