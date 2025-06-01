from fastapi import APIRouter, Depends, HTTPException
from typing import List
from backend import models, database
from bson import ObjectId

router = APIRouter()

@router.get("/orders")
async def get_all_orders():
    orders = []
    for order in database.database["orders"].find():
        # Convert ObjectId to string for JSON serialization
        order["_id"] = str(order["_id"])
        orders.append(order)
    return orders
