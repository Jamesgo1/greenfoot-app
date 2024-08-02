from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import models as m
import schemas
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import crud_queries as crud

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
        return crud.get_all_tree_details_full_history(db=db, limit=limit)
    else:
        return crud.get_all_tree_details_by_id(db=db, tree_id=tree_id, limit=limit)

@app.get("/username-exists/", response_model=schemas.UserExists, status_code=status.HTTP_200_OK)
async def check_nickname_exists(db: db_dependency, nickname: str):
    return crud.check_nickname_exists(db=db, nickname=nickname)

@app.post("/user-details/", response_model=list[schemas.UserBase], status_code=status.HTTP_200_OK)
async def get_user_details(db: db_dependency, id_details: schemas.UserAuth):
    return crud.get_user_by_sub(db=db, sub=id_details)


@app.post("/add-user/", response_model=schemas.UserBase, status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_details: schemas.UserBase):
    current_user = crud.get_user_by_sub(db=db, sub=user_details.user_auth0_sub)
    if current_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db=db, user=user_details)
