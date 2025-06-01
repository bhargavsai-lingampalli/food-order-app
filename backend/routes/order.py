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
async def create_order(cart_items: str = Query(...)):
    """
    Create a new order.  Assumes cart_items is a list of objects with menu_item_id and quantity.
    """
    cart_items = json.loads(cart_items)
    total = 0.0
    order_items = []

    for item in cart_items:
        menu_item_id = item["menu_item_id"]
        quantity = item["quantity"]

        menu_item = database.database["menu_items"].find_one({"_id": ObjectId(menu_item_id)})
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item {menu_item_id} not found")

        total += float(menu_item["price"]) * quantity

        order_item = models.OrderItem(
            menu_item_id=menu_item_id,
            quantity=quantity
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
