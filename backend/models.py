# backend/models.py
from typing import Dict, List, Optional
from bson import ObjectId

class MenuItem:
    def __init__(self, name: str, description: str, price: float, image_url: str):
        self.name = name
        self.description = description
        self.price = price
        self.image_url = image_url

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "image_url": self.image_url,
        }


class CartItem:
    def __init__(self, menu_item_id: str, quantity: int, _id: Optional[ObjectId] = None):
        self.id = _id
        self.menu_item_id = menu_item_id
        self.quantity = quantity

    def to_dict(self):
        return {
            "_id": self.id,
            "menu_item_id": self.menu_item_id,
            "quantity": self.quantity,
        }


class OrderItem:
    def __init__(self, menu_item_id: str, quantity: int):
        self.menu_item_id = menu_item_id
        self.quantity = quantity

    def to_dict(self):
        return {
            "menu_item_id": self.menu_item_id,
            "quantity": self.quantity,
        }


class Order:
    def __init__(self, user_id: str, total: float, items: List[OrderItem], status: str = "pending", is_prepared: bool = False, is_completed: bool = False, _id: Optional[ObjectId] = None):
        self.id = _id
        self.user_id = user_id
        self.total = total
        self.items = [item.to_dict() for item in items]
        self.status = status
        self.is_prepared = is_prepared
        self.is_completed = is_completed

    def to_dict(self):
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "total": self.total,
            "items": self.items,
            "status": self.status,
            "is_prepared": self.is_prepared,
            "is_completed": self.is_completed,
        }


class User:
    def __init__(self, google_id: str, email: str, name: str, picture: str = None, _id: Optional[ObjectId] = None):
        self.id = _id
        self.google_id = google_id
        self.email = email
        self.name = name
        self.picture = picture

    def to_dict(self):
        return {
            "_id": self.id,
            "google_id": self.google_id,
            "email": self.email,
            "name": self.name,
            "picture": self.picture,
        }
