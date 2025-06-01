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
        return {"message": "Cart item added successfully", "id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="Failed to add cart item")


@router.get("/{user_id}")
async def view_cart(user_id: str):
    """View cart"""
    cart_items = list(database.database["cart_items"].find())  # In a real application, you would filter cart items by user_id
    return cart_items


@router.post("/checkout")
async def checkout(user_id: str):
    """Place order"""
    # This is a placeholder. The actual implementation would involve:
    # 1. Creating an order
    # 2. Adding the cart items to the order
    # 3. Clearing the cart
    # 4. Returning the order details
    return {"message": "Checkout complete"}
