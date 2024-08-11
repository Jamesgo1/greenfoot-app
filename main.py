from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import models as m
import schemas
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import crud_queries as crud
import enum_input_options as enum_opt

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


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/tree-species-type/{species_id}", response_model=schemas.SpeciesBase, status_code=status.HTTP_200_OK)
async def read_species_type(species_id: int, db: db_dependency):
    species = db.query(m.TreeSpecies).filter(m.TreeSpecies.tree_species_id == species_id).first()
    if species is None:
        raise HTTPException(status_code=404, detail="Tree species not found")
    return species


@app.get("/all-tree-info/", response_model=list[schemas.AllTreeDetailsBase], status_code=status.HTTP_200_OK)
async def get_tree_details_alt(db: db_dependency, limit: int = 50, tree_id: int | None = None):
    if not tree_id:
        return crud.get_latest_tree_details_all(db=db, limit=limit)
    else:
        return crud.get_latest_tree_details_by_id(db=db, tree_id=tree_id, limit=limit)


@app.get("/all-tree-info-by-loc", response_model=list[schemas.AllTreeDetailsBase], status_code=status.HTTP_200_OK)
async def get_tree_details_loc(db: db_dependency, lat: str, long: str, limit: int = 50):
    return crud.get_all_tree_details_full_history_query_by_location(db=db, lat=lat, long=long, limit=limit)


@app.get("/all-tree-info-hist/", response_model=list[schemas.AllTreeDetailsBase], status_code=status.HTTP_200_OK)
async def get_tree_details_alt(db: db_dependency, limit: int = 50, tree_id: int | None = None):
    if not tree_id:
        return crud.get_all_tree_details_all(db=db, limit=limit)
    else:
        return crud.get_all_tree_details_by_id(db=db, tree_id=tree_id, limit=limit)


@app.get("/username-available/", response_model=schemas.UserAvailable, status_code=status.HTTP_200_OK)
async def check_nickname_available(db: db_dependency, nickname: str):
    return crud.check_nickname_available(db=db, nickname=nickname)

@app.get("/table-options/", response_model=list[schemas.DiscreteTableTypeValues], status_code=status.HTTP_200_OK)
async def get_discrete_table_options(db: db_dependency, table_val: enum_opt.ValidTableOptionTables):
    if table_val.value == "tree_species_type":
        return crud.get_discrete_tree_species_options(db)
    else:
        return crud.get_discrete_tree_desc_options(db=db, table_name=table_val)

@app.get("/table-options-species_type/", response_model=list[schemas.DiscreteTableTypeValues],
         status_code=status.HTTP_200_OK)
async def get_discrete_table_options(db: db_dependency, table_val: enum_opt.ValidTableOptionTables):
    return crud.get_discrete_tree_desc_options(db=db, table_name=table_val)

@app.post("/user-details/", response_model=list[schemas.UserDetails], status_code=status.HTTP_200_OK)
async def get_user_details(db: db_dependency, id_details: schemas.UserAuth):
    return crud.get_user_by_sub(db=db, sub=id_details)


@app.patch("/change-user-details/{auth0_sub}", response_model=list[schemas.UserAdd], status_code=status.HTTP_200_OK)
async def update_user_details(db: db_dependency, auth0_sub: str, user_details: schemas.UserAdd):
    user_details_to_update = user_details.dict(exclude_unset=True)
    return crud.update_user_details(db=db, user_auth0_sub=auth0_sub, update_vals=user_details_to_update)


@app.post("/add-user/", response_model=schemas.UserAdd, status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_details: schemas.UserAdd):
    return crud.create_user(db=db, user=user_details)

