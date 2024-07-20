from pydantic import BaseModel


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


class AllTreeDetailsBase(BaseModel):
    tree_species_type_desc: str
    tree_species_desc: str
    tree_id: int
    diameter_cm: int
    spread_radius_m: int
    tree_height_m: int
    longitude: float
    latitude: float
    tree_age_group_desc: str
    tree_surround_desc: str
    tree_vigour_desc: str
    tree_condition_desc: str

    class Config:
        orm_mode = True
