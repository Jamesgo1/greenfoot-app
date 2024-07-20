from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors  import CORSMiddleware
from typing import Annotated
import models as m
import schemas
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import get_funcs as get


app = FastAPI()
m.Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# cols_to_return = [m.Tree.tree_id,
#                   m.Tree.diameter_cm,
#                   m.Tree.spread_radius_m,
#                   m.Tree.tree_height_m,
#                   m.Tree.longitude,
#                   m.Tree.latitude,
#                   m.TreeSpecies.tree_species_desc,
#                   m.TreeSpeciesType.tree_species_type_desc,
#                   m.TreeAgeGroup.tree_age_group_desc,
#                   m.TreeSurround.tree_surround_desc,
#                   m.TreeVigour.tree_vigour_desc,
#                   m.TreeCondition.tree_condition_desc, ]
#
# db = SessionLocal()
# db.query(*cols_to_return)
# tree_data = db.query(
# *cols_to_return
# ).join(
#     m.TreeSpecies, m.Tree.tree_species_id == m.TreeSpecies.tree_species_id).join(
#     m.TreeSpeciesType, m.TreeSpecies.tree_species_type_id == m.TreeSpeciesType.tree_species_type_id).join(
#     m.TreeAgeGroup).join(
#     m.TreeCondition).join(
#     m.TreeDataQuality).join(
#     m.TreeSurround).join(
#     m.TreeVigour).filter(m.Tree.tree_id < 100).order_by(m.Tree.tree_id).limit(50).all()
# print(tree_data)
# quit()
# for row in q1:
#     print(row.__dict__)
# quit()

db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/tree-species-type/{species_id}", response_model=schemas.SpeciesBase, status_code=status.HTTP_200_OK)
async def read_species_type(species_id: int, db: db_dependency):
    species = db.query(m.TreeSpecies).filter(m.TreeSpecies.tree_species_id == species_id).first()
    if species is None:
        raise HTTPException(status_code=404, detail="Tree species not found")
    return species


@app.get("/all-tree-details/{tree_id}", response_model=list[schemas.AllTreeDetailsBase], status_code=status.HTTP_200_OK)
async def get_all_tree_details(tree_id: int, db: db_dependency):
    return db.query(
        m.Tree.tree_id,
        m.Tree.diameter_cm,
        m.Tree.spread_radius_m,
        m.Tree.tree_height_m,
        m.Tree.longitude,
        m.Tree.latitude,
        m.TreeSpecies.tree_species_desc,
        m.TreeSpeciesType.tree_species_type_desc,
        m.TreeAgeGroup.tree_age_group_desc,
        m.TreeSurround.tree_surround_desc,
        m.TreeVigour.tree_vigour_desc,
        m.TreeCondition.tree_condition_desc,
    ).join(
        m.TreeSpecies, m.Tree.tree_species_id == m.TreeSpecies.tree_species_id).join(
        m.TreeSpeciesType, m.TreeSpecies.tree_species_type_id == m.TreeSpeciesType.tree_species_type_id).join(
        m.TreeAgeGroup).join(
        m.TreeCondition).join(
        m.TreeDataQuality).join(
        m.TreeSurround).join(
        m.TreeVigour).filter(m.Tree.tree_id == tree_id).all()


@app.get("/all-tree-info/", response_model=list[schemas.AllTreeDetailsBase], status_code=status.HTTP_200_OK)
async def get_tree_details_alt(db: db_dependency, limit:int = 50, tree_id: int | None = None):
    if not tree_id:
        return get.get_all_tree_details_all(db=db, limit=limit)
    else:
        return get.get_all_tree_details_by_id(db=db, tree_id=tree_id, limit=limit)
