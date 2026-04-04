from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    price: float

@app.post("/api/logic/calculate-tax")
async def calculate_tax(item: Item):
    if item.price <= 0:
        return {"error": "El precio debe ser mayor a 0"}, 400
    
    tax = item.price * 0.19
    total = item.price + tax
    return {"total_price": total}