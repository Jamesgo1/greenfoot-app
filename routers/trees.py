from fastapi import APIRouter, status, HTTPException
from greenfootapi.dependencies import db_dependency
from greenfootapi import schemas
from greenfootapi import crud_queries as crud
from greenfootapi import enum_input_options as enum_opt
from greenfootapi import models as m

router = APIRouter(prefix="/tree", tags=["trees"])


@router.get("/tree-species-type/{species_id}", response_model=schemas.SpeciesBase, status_code=status.HTTP_200_OK)
async def read_species_type(species_id: int, db: db_dependency):
    species = db.query(m.TreeSpecies).filter(m.TreeSpecies.tree_species_id == species_id).first()
    if species is None:
        raise HTTPException(status_code=404, detail="Tree species not found")
    return species


@router.get("/all-tree-info/", response_model=list[schemas.AllTreeDetailsBase], status_code=status.HTTP_200_OK)
async def get_tree_details_alt(db: db_dependency, limit: int = 50, tree_id: int | None = None):
    if not tree_id:
        return crud.get_latest_tree_details_all(db=db, limit=limit)
    else:
        return crud.get_latest_tree_details_by_id(db=db, tree_id=tree_id)


@router.post("/all-tree-info-list-input/", response_model=list[schemas.AllTreeDetailsAdmin],
             status_code=status.HTTP_200_OK)
async def get_tree_details_alt(db: db_dependency, id_list: list[int]):
    return crud.get_latest_tree_details_all_from_list(db=db, trees_to_get=id_list)


@router.get("/all-tree-info-full-table/", response_model=list[schemas.AllTreeHistoryTable],
            status_code=status.HTTP_200_OK)
async def get_tree_details_full(db: db_dependency, tree_id: int):
    return crud.get_latest_tree_details_by_id(db=db, tree_id=tree_id)


@router.get("/all-tree-info-by-loc", response_model=list[schemas.AllTreeDetailsLoc], status_code=status.HTTP_200_OK)
async def get_tree_details_loc(db: db_dependency, lat: str, long: str, limit: int = 50):
    return crud.get_all_tree_details_full_history_query_by_location(db=db, lat=lat, long=long, limit=limit)


@router.get("/all-tree-info-hist/", response_model=list[schemas.AllTreeDetailsBase], status_code=status.HTTP_200_OK)
async def get_tree_details_alt(db: db_dependency,
                               limit: int = 50,
                               tree_id: int | None = None,
                               show_non_live: bool | None = None):
    if not tree_id:
        return crud.get_all_tree_details_all(db=db, limit=limit, show_non_live=show_non_live)
    else:
        return crud.get_all_tree_details_by_id(db=db, tree_id=tree_id, limit=limit, show_non_live=show_non_live)


@router.get("/latest-tree-edits-approved/", response_model=list[schemas.AllTreeDetailsBase],
            status_code=status.HTTP_200_OK)
async def get_latest_tree_edits_approved(db: db_dependency, limit: int = 5):
    return crud.get_latest_tree_changes_home_page(db=db, limit=limit)


@router.post("/add-new-tree/", response_model=schemas.AllTreeHistoryTableAdd, status_code=status.HTTP_201_CREATED)
async def add_a_new_tree(db: db_dependency, new_tree_details: schemas.AddANewTree):
    return crud.add_a_new_tree(db=db, tree_details=new_tree_details)


@router.post("/add-new-tree-detail/", response_model=schemas.AllTreeHistoryTableAdd,
             status_code=status.HTTP_201_CREATED)
async def add_new_tree_history(db: db_dependency, tree_hist_details: schemas.AllTreeHistoryTableAdd):
    return crud.create_new_tree_history(db=db, tree_hist=tree_hist_details)


@router.get("/approved-images/{tree_id}/", response_model=list[schemas.ImageForApproval],
            status_code=status.HTTP_200_OK)
async def get_approved_images(db: db_dependency, tree_id: int, limit: int = 10):
    return crud.get_approved_images(db=db, tree_id=tree_id, limit=limit)


@router.get("/get-daily-image/", response_model=schemas.ImageForApproval, status_code=status.HTTP_200_OK)
async def get_daily_image(db: db_dependency):
    return crud.get_daily_image(db)
