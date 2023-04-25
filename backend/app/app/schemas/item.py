from pydantic import BaseModel

from app.schemas.user import User, UserInDB, UserInDBBase

__all__ = [
    "ItemBase",
    "ItemCreate",
    "ItemUpdate",
    "ItemInDBBase",
    "Item",
    "ItemInDB",
]


# Shared properties
class ItemBase(BaseModel):
    title: str | None = None
    description: str | None = None


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str


# Properties to receive on item update
class ItemUpdate(ItemBase):
    pass


# Properties shared by models stored in DB
class ItemInDBBase(ItemBase):
    class Config:
        orm_mode = True

    id: int
    title: str
    owner: UserInDBBase


# Properties to return to client
class Item(ItemInDBBase):
    class Config:
        orm_mode = True

    owner: User


# Properties properties stored in DB
class ItemInDB(ItemInDBBase):
    class Config:
        orm_mode = True

    owner: UserInDB
