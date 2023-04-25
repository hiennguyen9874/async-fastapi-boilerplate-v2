from datetime import datetime

from pydantic import BaseModel, EmailStr

__all__ = ["UserBase", "UserCreate", "UserLogin", "UserUpdate", "UserInDBBase", "User", "UserInDB"]


# Shared properties
class UserBase(BaseModel):
    email: EmailStr | None = None
    is_active: bool | None = True
    is_superuser: bool = False
    full_name: str | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: str | None = None


class UserInDBBase(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    email: EmailStr
    full_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
