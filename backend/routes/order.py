from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from backend import models, database
import json
from backend.utils.websocket import manager
from typing import List
from bson import ObjectId

router = APIRouter()


@router.post("/create")
async def create_order(user_id: str, cart_item_ids: List[str]):
    """
    Create a new order.  Assumes cart_item_ids is a list of cart item IDs.
    """
    total = 0.0
    order_items = []

    for cart_item_id in cart_item_ids:
        cart_item = database.database["cart_items"].find_one({"_id": ObjectId(cart_item_id)})
        if not cart_item:
            raise HTTPException(status_code=404, detail=f"Cart item {cart_item_id} not found")

        menu_item = database.database["menu_items"].find_one({"_id": ObjectId(cart_item["menu_item_id"])})
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item for cart item {cart_item_id} not found")

        total += menu_item["price"] * cart_item["quantity"]

        order_item = models.OrderItem(
            menu_item_id=str(menu_item["_id"]),
            quantity=cart_item["quantity"]
        )
        order_items.append(order_item)

    order = models.Order(user_id=user_id, total=total, items=order_items)
    result = database.database["orders"].insert_one(order.to_dict())
    if result.inserted_id:
        order_data = database.database["orders"].find_one({"_id": result.inserted_id})
        await manager.broadcast(json.dumps(order_data))
        return {"message": f"Order created with ID: {result.inserted_id}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to create order")


@router.post("/api/orders")
async def receive_order(request: Request):
    order = await request.json()
    # TODO: Notify chef here (e.g., send email, update dashboard, etc.)
    print("New order received:", order)
    return JSONResponse(content={"message": "Order received and chef notified!"})
