from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Testing API")

# Request Body එකට අදාළ Schema එක
class ItemData(BaseModel):
    name: str
    price: float
    description: str | None = None

@app.get("/")
def root():
    return {
        "status": "success",
        "message": "FastAPI CI/CD pipeline working perfectly!",
        "host": "testing.swapgate-store.com"
    }

@app.get("/health")
def health():
    return {"health": "ok"}

# අලුත් POST endpoint එක:
# 1. item_id -> Path Parameter (URL එකේ එන අගය: /items/10)
# 2. category -> Query Parameter (URL එකේ ?category=electronics විදිහට)
# 3. item -> Request Body (JSON Data)
@app.post("/items/{item_id}")
def create_or_update_item(item_id: int, category: str, item: ItemData):
    return {
        "status": "created",
        "received_path_param": {"item_id": item_id},
        "received_query_param": {"category": category},
        "received_body": {
            "name": item.name,
            "price": item.price,
            "description": item.description
        },
        "message": f"Item {item_id} in {category} created successfully!"
    }