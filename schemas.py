from pydantic import BaseModel
from typing import Optional
import datetime


class PostBase(BaseModel):
    title: str
    content: str
    user_id: int


class SpeciesTypeBase(BaseModel):
    tree_species_type_id: int
    tree_species_type_desc: str

    class Config:
        orm_mode = True


class SpeciesBase(BaseModel):
    tree_species_id: int
    tree_species_desc: str

    class Config:
        orm_mode = True


# (2, datetime.datetime(2024, 7, 26, 17, 35, 3), 32, 5, 14, -5.982504, 54.540829, 'Acer Pseudoplatanus', 'Maple', 'Young', 'Shrubs', 'Normal', 'Fair'
class AllTreeDetailsBase(BaseModel):
    tree_id: int
    tree_change_datetime: datetime.datetime
    tree_species_type_desc: Optional[str]
    tree_species_desc: Optional[str]
    diameter_cm: Optional[int]
    spread_radius_m: Optional[int]
    tree_height_m: Optional[int]
    longitude: Optional[float]
    latitude: Optional[float]
    tree_age_group_desc: Optional[str]
    tree_surround_desc: Optional[str]
    tree_vigour_desc: Optional[str]
    tree_condition_desc: Optional[str]

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    nickname: str
    given_name: Optional[str]
    family_name: Optional[str]
    email_verified: Optional[int]
    user_type_desc: str


class AddUser(UserBase):
    user_auth0_sub: str
    email: str


class UserAuth(BaseModel):
    user_auth0_sub: str

class UserExists(BaseModel):
    user_exists: bool