import os
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv
from models import Item  # Import the Item model from models.py

# Load environment variables from the ..env file
load_dotenv()

# Retrieve MongoDB details from the environment, fallback to a default value if not set
MONGO_DETAILS = os.getenv("MONGO_DETAILS")
if not MONGO_DETAILS:
    raise ValueError("MONGO_DETAILS environment variable not set.")

app = FastAPI()

# Initialize the MongoDB client
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.my_database
item_collection = database.get_collection("items")

def item_helper(item) -> dict:
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "description": item.get("description"),
        "price": item["price"],
        "tax": item.get("tax")
    }

@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    item_dict = item.model_dump()
    new_item = await item_collection.insert_one(item_dict)
    created_item = await item_collection.find_one({"_id": new_item.inserted_id})
    return item_helper(created_item)

# @app.get("/items/{id}", response_model=Item)
# async def read_item(id: str):
#     item = await item_collection.find_one({"_id": ObjectId(id)})
#     if item is None:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return item_helper(item)
#

@app.get("/allitems", response_model=Item)
async def read_all_items():
    items_cursor = item_collection.find()  # Get all items
    items = await items_cursor.to_list(length=100)  # Convert cursor to list (limit to 100 items for example)
    return [item_helper(item) for item in items]  # Return a list of item dictionaries


#
# @app.put("/items/{id}", response_model=Item)
# async def update_item(id: str, item: Item):
#     await item_collection.update_one({"_id": ObjectId(id)}, {"$set": item.dict()})
#     updated_item = await item_collection.find_one({"_id": ObjectId(id)})
#     if updated_item is None:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return item_helper(updated_item)
#
# @app.delete("/items/{id}")
# async def delete_item(id: str):
#     result = await item_collection.delete_one({"_id": ObjectId(id)})
#     if result.deleted_count == 1:
#         return {"message": "Item deleted"}
#     raise HTTPException(status_code=404, detail="Item not found")
