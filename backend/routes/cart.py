from fastapi import APIRouter, Depends, HTTPException
from typing import List
from backend import models, database
from bson import ObjectId

router = APIRouter()


@router.post("/add")
async def add_item_to_cart(menu_item_id: str, quantity: int):
    """Add item to cart"""
    menu_item = database.database["menu_items"].find_one({"_id": ObjectId(menu_item_id)})
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    cart_item = models.CartItem(menu_item_id=menu_item_id, quantity=quantity)
    result = database.database["cart_items"].insert_one(cart_item.to_dict())
    if result.inserted_id:
        cart_item_id = str(result.inserted_id)
        return {"message": "Cart item added successfully", "id": cart_item_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to add cart item")


@router.get("/")
async def view_cart():
    """View cart"""
    cart_items = list(database.database["cart_items"].find())
    return cart_items


@router.post("/checkout")
async def checkout():
    """Place order"""
    cart_items = list(database.database["cart_items"].find())
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = 0.0
    order_items = []

    for cart_item in cart_items:
        menu_item = database.database["menu_items"].find_one({"_id": ObjectId(cart_item["menu_item_id"])})
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item not found for cart item {cart_item['_id']}")

        total += float(menu_item["price"]) * cart_item["quantity"]

        order_items.append({
            "menu_item_id": str(menu_item["_id"]),
            "quantity": cart_item["quantity"]
        })

    order = models.Order(total=total, items=order_items, status="pending", is_prepared=False, is_completed=False)
    if result.inserted_id:
        database.database["cart_items"].delete_many({})
        return {"message": "Checkout complete", "order_id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Failed to create order")
