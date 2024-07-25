import os
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv
from models import Item
from typing import List

# Load environment variables from the .env file
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
    item_dict = item.model_dump()  # Serialize the Pydantic model to a dictionary
    new_item = await item_collection.insert_one(item_dict)  # Insert the document into MongoDB
    created_item = await item_collection.find_one({"_id": new_item.inserted_id})  # Fetch the newly created item
    if created_item is None:
        raise HTTPException(status_code=500, detail="Item creation failed")
    return item_helper(created_item)  # Format and return the item

# @app.get("/allitems", response_model=List[Item])
# async def read_all_items():
#     items_cursor = item_collection.find()  # Get all items
#     items = await items_cursor.to_list(length=100)  # Convert cursor to list (limit to 100 items for example)
#     return [item_helper(item) for item in items]  # Return a list of item dictionaries

# fetch all items
# @app.get("/allitems/")
# async def read_all_items():
#     # return hello world
#     return [{"name": "hello world"}]
#     # items = []
#     # async for item in item_collection.find():
#     #     items.append(item_helper(item))
#     # return items

# @app.get("/")
# def read_all_items():
#     return {"message": "hello world"}

