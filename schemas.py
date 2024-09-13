from pydantic import BaseModel
from typing import Optional
import datetime


class PostBase(BaseModel):
    title: str
    content: str
    user_id: int


class SpeciesTypeBase(BaseModel):
    tree_species_type_id: int
    tree_species_type_desc: str

    class Config:
        from_attributes = True


class SpeciesBase(BaseModel):
    tree_species_id: int
    tree_species_desc: str

    class Config:
        from_attributes = True


class AllTreeDetailsBase(BaseModel):
    tree_id: int
    tree_change_datetime: datetime.datetime
    tree_species_type_desc: Optional[str]
    tree_species_desc: Optional[str]
    diameter_cm: Optional[int]
    spread_radius_m: Optional[int]
    tree_height_m: Optional[int]
    longitude: Optional[float]
    latitude: Optional[float]
    tree_age_group_desc: Optional[str]
    tree_surround_desc: Optional[str]
    tree_vigour_desc: Optional[str]
    tree_condition_desc: Optional[str]
    nickname: Optional[str]
    tree_change_desc: Optional[str]

    class Config:
        from_attributes = True


class AllTreeDetailsLoc(BaseModel):
    tree_id: int
    tree_distance: float
    tree_change_datetime: datetime.datetime
    tree_species_type_desc: Optional[str]
    tree_species_desc: Optional[str]
    diameter_cm: Optional[int]
    spread_radius_m: Optional[int]
    tree_height_m: Optional[int]
    longitude: Optional[float]
    latitude: Optional[float]
    tree_age_group_desc: Optional[str]
    tree_surround_desc: Optional[str]
    tree_data_quality_id: Optional[int]
    tree_data_quality_desc: Optional[str]
    tree_vigour_desc: Optional[str]
    tree_condition_desc: Optional[str]
    tree_type_desc: Optional[str]
    nickname: Optional[str]
    tree_change_desc: Optional[str]
    image_paths: Optional[str] = None

    class Config:
        from_attributes = True


class TreeStatusUpdateBase(BaseModel):
    tree_history_id: int
    is_live_change_ind: int


class AllTreeDetailsAdmin(AllTreeDetailsBase):
    tree_history_id: int


class AllTreeDetailsAdminFullHistory(AllTreeDetailsAdmin):
    tree_type_desc: Optional[str]
    tree_type_id: Optional[int]
    tree_species_id: Optional[int]
    tree_age_group_id: Optional[int]
    tree_surround_id: Optional[int]
    tree_vigour_id: Optional[int]
    tree_condition_id: Optional[int]
    tree_data_quality_id: Optional[int]


class AllTreeHistoryTable(BaseModel):
    diameter_cm: Optional[int]
    spread_radius_m: Optional[int]
    tree_height_m: Optional[int]
    location_x: Optional[float]
    location_y: Optional[float]
    longitude: Optional[float]
    latitude: Optional[float]
    tree_change_desc: Optional[str]
    tree_tag: Optional[int]
    tree_type_id: Optional[int]
    tree_species_id: Optional[int]
    tree_age_group_id: Optional[int]
    tree_surround_id: Optional[int]
    tree_vigour_id: Optional[int]
    tree_condition_id: Optional[int]
    tree_data_quality_id: Optional[int]
    tree_id: int


class AddANewTree(BaseModel):
    diameter_cm: int
    spread_radius_m: int
    tree_height_m: int
    longitude: float
    latitude: float
    tree_change_desc: str
    tree_type_id: int
    tree_species_id: int
    tree_age_group_id: int
    tree_surround_id: int
    tree_vigour_id: int
    tree_condition_id: int
    tree_data_quality_id: int
    user_id: int


class TreeDetailsNewUpdate(BaseModel):
    tree_history_id: int
    diameter_cm: Optional[int] = None
    spread_radius_m: Optional[int] = None
    tree_height_m: Optional[int] = None
    location_x: Optional[float] = None
    location_y: Optional[float] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    is_live_change_ind: int
    tree_tag: Optional[int] = None
    tree_type_id: Optional[int] = None
    tree_species_id: Optional[int] = None
    tree_age_group_id: Optional[int] = None
    tree_surround_id: Optional[int] = None
    tree_vigour_id: Optional[int] = None
    tree_condition_id: Optional[int] = None
    tree_data_quality_id: Optional[int] = None
    tree_id: int = None


class TreeStatusUpdateReturn(AllTreeHistoryTable):
    is_live_change_ind: int


class AllTreeHistoryTableAdd(AllTreeHistoryTable):
    user_id: int
    is_live_change_ind: int


class TreeInactive(BaseModel):
    tree_id: int
    inactive_datetime: datetime.datetime


class UserBase(BaseModel):
    nickname: str = "default"
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    email_verified: Optional[int] = None


class UserDetails(UserBase):
    user_type_desc: str
    user_id: int
    user_type_id: Optional[int] = 1


class UserAdd(UserBase):
    user_auth0_sub: str = "default"
    email: str = None
    is_active: Optional[int] = 1
    user_type_id: Optional[int] = 1


class UserAuth(BaseModel):
    user_auth0_sub: str


class UserAvailable(BaseModel):
    user_available: bool


class DiscreteTableTypeValues(BaseModel):
    table_id: int
    table_desc: str


class RowsChangedBase(BaseModel):
    row_changed_count: int
    tree_ids_updated: list[int]


class ImageUploadResponse(BaseModel):
    filename: str
    url: str


class ImageDisplayBase(BaseModel):
    image_path: str


class ImageForApproval(ImageDisplayBase):
    image_id: int
    tree_id: int
    image_approved_ind: int
    image_add_datetime: datetime.datetime
    nickname: str


class CheckImageApproved(BaseModel):
    image_approved_ind: int


class AnalyticsGroupBy(BaseModel):
    group_by_counts: list[dict]


class NotificationData(BaseModel):
    tree_id: int
    user_id: int
    nickname: str
    comb_date: datetime.datetime
    change_type: str
    noti_clicked_ind: int
    change_ind: int


class NotificationUpdate(BaseModel):
    noti_last_clicked: datetime.datetime


class ImageValidation(BaseModel):
    Name: str
    Confidence: float


class CustomAnalysisBase(BaseModel):
    tree_id: int
    tree_change_datetime: datetime.datetime
    image_add_datetime: datetime.datetime
    nickname: str
    tree_species_type_desc: str


class CustomAnalysisOutput(CustomAnalysisBase):
    labels: list[dict]


class UserID(BaseModel):
    user_id: int


class ImageModelRunning(BaseModel):
    a_model_status: str


class CustomAnalysisShow(CustomAnalysisBase):
    latest_labels: str
    image_user_id: int
    image_path: str
    image_nickname: str
    last_ai_analysis: datetime.datetime
    tree_image_id: int
