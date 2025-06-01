from pydantic import BaseModel
from typing import Optional

class MenuItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    image_url: str | None = None


class MenuItemCreate(MenuItemBase):
    pass


class MenuItem(MenuItemBase):

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    google_id: str
    email: str
    name: str
    picture: str | None = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    class Config:
        orm_mode = True
