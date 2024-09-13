from fastapi import APIRouter, status, HTTPException
from greenfootapi.dependencies import db_dependency
from greenfootapi import schemas
from greenfootapi import crud_queries as crud
from greenfootapi import enum_input_options as enum_opt

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/row-level-data/", response_model=list[schemas.AllTreeDetailsAdmin], status_code=status.HTTP_200_OK)
async def get_discrete_table_options(db: db_dependency, filter_dict: dict, limit: int = 50):
    return crud.get_analytics_row_data(db=db, filter_dict=filter_dict, limit=limit)

@router.post("/row-level-data-loc/", response_model=list[schemas.AllTreeDetailsLoc], status_code=status.HTTP_200_OK)
async def get_discrete_table_options(db: db_dependency, lat: str, long: str, filter_dict: dict, limit: int = 50):
    return crud.get_all_tree_details_full_history_query_by_location(db=db, lat=lat, long=long, query_dict=filter_dict,
                                                                    limit=limit)

@router.post("/group-by-counts/", response_model=schemas.AnalyticsGroupBy,
            status_code=status.HTTP_200_OK)
async def get_discrete_table_options(db: db_dependency, val_for_groupby: enum_opt.ValidTableOptionTables,
                                     filter_dict: dict = None):
    return crud.get_analytics_groupby(db=db, group_by_name=val_for_groupby, filter_dict=filter_dict)
