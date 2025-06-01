from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from backend import models, database
import json
from backend.utils.websocket import manager
from typing import List
from bson import ObjectId

router = APIRouter()


from fastapi import Query
import json

@router.post("/create")
async def create_order(cart_item_ids: str = Query(...)):
    """
    Create a new order.  Assumes cart_item_ids is a list of cart item IDs.
    """
    cart_item_ids = json.loads(cart_item_ids)
    total = 0.0
    order_items = []

    for cart_item_id in cart_item_ids:
        cart_item_record = database.database["cart_items"].find_one({"_id": ObjectId(cart_item_id)})
        if not cart_item_record:
            raise HTTPException(status_code=404, detail=f"Cart item {cart_item_id} not found")

        menu_item = database.database["menu_items"].find_one({"_id": ObjectId(cart_item_record["menu_item_id"])})
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item for cart item {cart_item_id} not found")

        total += float(menu_item["price"]) * cart_item_record["quantity"]

        order_item = models.OrderItem(
            menu_item_id=str(menu_item["_id"]),
            quantity=cart_item_record["quantity"]
        )
        order_items.append(order_item.to_dict())

    order = models.Order(total=total, items=order_items, status="pending", is_prepared=False, is_completed=False)
    result = database.database["orders"].insert_one(order.to_dict())
    if result.inserted_id:
        order_data = database.database["orders"].find_one({"_id": result.inserted_id})
        await manager.broadcast(json.dumps(order_data))
        return {"message": f"Order created with ID: {result.inserted_id}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to create order")
