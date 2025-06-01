from fastapi import APIRouter, Depends, HTTPException
from typing import List
from backend import models, database
from bson import ObjectId

router = APIRouter()

@router.get("/admin/orders")
async def get_all_orders():
    orders = []
    for order in database.database["orders"].find():
        # Convert ObjectId to string for JSON serialization
        order["_id"] = str(order["_id"])
        orders.append(order)
    return orders


@router.put("/admin/order/{order_id}/done")
async def update_order_status(order_id: str, status: str):
    """Update order status"""
    order = database.database["orders"].find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    database.database["orders"].update_one({"_id": ObjectId(order_id)}, {"$set": {"status": status}})
    return {"message": "Order status updated successfully"}
