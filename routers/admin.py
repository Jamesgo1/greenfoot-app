from fastapi import APIRouter, status, HTTPException
from greenfootapi.dependencies import db_dependency
from greenfootapi import schemas
from greenfootapi import crud_queries as crud
from greenfootapi import enum_input_options as enum_opt

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/all-tree-info-to-approve/", response_model=list[schemas.AllTreeDetailsAdmin],
            status_code=status.HTTP_200_OK)
async def get_tree_details_alt(db: db_dependency,
                               limit: int = 50):
    return crud.get_all_tree_details_to_approve_list(db=db, limit=limit)


@router.get("/all-new-trees-to-approve", response_model=list[schemas.AllTreeDetailsAdminFullHistory],
            status_code=status.HTTP_200_OK)
async def get_all_new_trees_to_approve(db: db_dependency, limit: int = 50):
    return crud.get_all_new_trees_to_approve(db=db, limit=limit)


@router.get("/tree-to-approve-by-id/{tree_id}", response_model=list[schemas.AllTreeDetailsAdminFullHistory],
            status_code=status.HTTP_200_OK)
async def get_tree_details_alt(db: db_dependency, tree_id: int):
    return crud.get_tree_details_to_approve_id(db=db, tree_id=tree_id)


@router.get("/trees-requested-deletion/", response_model=list[schemas.AllTreeDetailsAdminFullHistory],
            status_code=status.HTTP_200_OK)
async def get_trees_requesting_deletion(db: db_dependency, limit: int = 50):
    return crud.get_tree_deletion_requests(db, limit)


@router.post("/add-automated-tree-change/", response_model=schemas.RowsChangedBase, status_code=status.HTTP_201_CREATED)
async def add_automated_changes(db: db_dependency, col_to_change: enum_opt.AutomatedChanges):
    return crud.run_automated_changes(db=db, col_to_update=col_to_change)


@router.patch("/update-tree-status/", response_model=list[schemas.TreeStatusUpdateReturn],
              status_code=status.HTTP_200_OK)
async def update_tree_status(db: db_dependency, tree_hist_details: list[schemas.TreeDetailsNewUpdate]):
    update_list_dict = [new_details.dict(exclude_unset=True) for new_details in tree_hist_details]
    return crud.update_tree_status(db=db, update_vals=update_list_dict)


@router.patch("/authorise-tree-inactive/{tree_id}", response_model=schemas.TreeInactive, status_code=status.HTTP_200_OK)
async def authorise_tree_inactive(db: db_dependency, tree_id: int):
    return crud.update_tree_inactive(db=db, tree_id=tree_id)


@router.get("/images-to-approve", response_model=list[schemas.ImageForApproval], status_code=status.HTTP_200_OK)
async def get_all_images_to_approve(db: db_dependency, limit: int = 50):
    return crud.get_images_to_approve(db=db, limit=limit)


@router.patch("/update-image-approval/", response_model=schemas.CheckImageApproved,
              status_code=status.HTTP_200_OK)
async def update_image_approval(db: db_dependency, tree_image_updates: schemas.ImageForApproval):
    update_dict = tree_image_updates.dict()
    return crud.update_image_approval(db=db, update_vals=update_dict)


@router.get("/custom-model-species-image-analysis/", response_model=list[schemas.CustomAnalysisOutput],
            status_code=status.HTTP_200_OK)
async def run_custom_species_analysis(db: db_dependency):
    analysis_output = crud.analyse_species_type(db)
    if analysis_output == "model_not_stopped":
        raise HTTPException(status_code=504, detail="The model has not been stopped. Please contact the site "
                                                    "administrator asap as costs will be incurred.")
    else:
        return analysis_output


@router.get("/check-model-status/", response_model=schemas.ImageModelRunning, status_code=status.HTTP_200_OK)
async def check_if_model_is_running():
    return crud.check_if_model_is_running()


@router.get("/latest-species-image-analysis/", response_model=list[schemas.CustomAnalysisShow],
            status_code=status.HTTP_200_OK)
async def get_latest_analysis_results(db: db_dependency):
    return crud.get_latest_species_type_analysis(db)
