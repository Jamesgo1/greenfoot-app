from fastapi import APIRouter, status, HTTPException
from greenfootapi.dependencies import db_dependency
from greenfootapi import schemas
from greenfootapi import crud_queries as crud

router = APIRouter(prefix="/user", tags=["users"])


@router.get("/username-available/", response_model=schemas.UserAvailable, status_code=status.HTTP_200_OK)
async def check_nickname_available(db: db_dependency, nickname: str):
    return crud.check_nickname_available(db=db, nickname=nickname)


@router.get("/notif-changes/", response_model=list[schemas.NotificationData], status_code=status.HTTP_200_OK)
async def get_notification_data(db: db_dependency, user_id: int | None = None, limit: int | None = None,
                                approved_only: bool = None):
    return crud.get_user_notifications(db, user_id, limit=limit, approved_only=approved_only)


@router.post("/user-details/", response_model=list[schemas.UserDetails], status_code=status.HTTP_200_OK)
async def get_user_details(db: db_dependency, id_details: schemas.UserAuth | None):
    if not id_details:
        return []
    return crud.get_user_by_sub(db=db, sub=id_details)


@router.post("/user-details-alt/", response_model=list[schemas.UserDetails], status_code=status.HTTP_200_OK)
async def get_user_details_by_id(db: db_dependency, id_details: schemas.UserID):
    return crud.get_user_by_id(db=db, user_id=id_details)


@router.post("/user-details-obj/", response_model=schemas.UserDetails, status_code=status.HTTP_200_OK)
async def get_user_details(db: db_dependency, id_details: schemas.UserAuth):
    return crud.get_user_by_sub(db=db, sub=id_details, get_first=True)


@router.patch("/change-user-details/{auth0_sub}", response_model=list[schemas.UserAdd], status_code=status.HTTP_200_OK)
async def update_user_details(db: db_dependency, auth0_sub: str, user_details: schemas.UserAdd):
    user_details_to_update = user_details.dict(exclude_unset=True)
    return crud.update_user_details(db=db, user_auth0_sub=auth0_sub, update_vals=user_details_to_update)


@router.patch("/update-notification-date/", response_model=schemas.NotificationUpdate,
              status_code=status.HTTP_200_OK)
async def update_notification_date(db: db_dependency, user_id: int):
    return crud.update_user_notification_date(db=db, user_id=user_id)


@router.post("/add-user/", response_model=schemas.UserAdd, status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_details: schemas.UserAdd):
    return crud.create_user(db=db, user=user_details)
