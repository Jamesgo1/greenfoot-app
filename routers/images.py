from fastapi import APIRouter, status, HTTPException, File, UploadFile
from greenfootapi.dependencies import db_dependency
from greenfootapi import schemas
from greenfootapi import crud_queries as crud
from greenfootapi import enum_input_options as enum_opt

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/uploadfile/{tree_id}/{user_id}", response_model=schemas.ImageUploadResponse,
             status_code=status.HTTP_201_CREATED)
async def upload_image(db: db_dependency, tree_id: int, user_id: int, file: UploadFile = File(...)):
    upload_return_object = await crud.upload_image(db, tree_id, user_id, file)
    print(upload_return_object)
    if upload_return_object == "image_already_exists":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Image name already exists for this tree")
    else:
        return upload_return_object


@router.post("/image-validation/", response_model=list[schemas.ImageValidation], status_code=status.HTTP_200_OK)
async def validate_image(file: UploadFile = File(...)):
    image_analysis = await crud.check_image_contains_tree(file=file)
    if image_analysis == "invalid_extension":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid extension: only .jpg or .png files are allowed")
    elif image_analysis == "processing_error":
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Unable to process your image. Please ensure that the file size is less than 5mb")
    else:
        return image_analysis
