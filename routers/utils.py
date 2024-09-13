from fastapi import APIRouter, status, HTTPException
from greenfootapi.dependencies import db_dependency
from greenfootapi import schemas
from greenfootapi import crud_queries as crud
from greenfootapi import enum_input_options as enum_opt

router = APIRouter(prefix="/util", tags=["utils"])


@router.get("/table-options/", response_model=list[schemas.DiscreteTableTypeValues], status_code=status.HTTP_200_OK)
async def get_discrete_table_options(db: db_dependency,
                                     table_val: enum_opt.ValidTableOptionTables,
                                     tree_species_type: str | None = None):
    if table_val.value == "tree_species":
        if not tree_species_type:
            raise HTTPException(status_code=400,
                                detail="A tree_species_type value is required to get tree_species values")
        else:
            return crud.get_discrete_tree_species_options(db, tree_species_type=tree_species_type)
    elif table_val.value == "tree_species_type":
        return crud.get_discrete_tree_species_type_options(db)
    else:
        return crud.get_discrete_tree_desc_options(db=db, table_name=table_val)

@router.get("/table-options-species_type/", response_model=list[schemas.DiscreteTableTypeValues],
            status_code=status.HTTP_200_OK)
async def get_discrete_table_options(db: db_dependency, table_val: enum_opt.ValidTableOptionTables):
    return crud.get_discrete_tree_desc_options(db=db, table_name=table_val)