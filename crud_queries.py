import greenfootapi.models as m
import greenfootapi.schemas as s
from sqlalchemy.orm import Session
from sqlalchemy import func, text, exists, inspect, case, desc
from sqlalchemy.sql import literal, column
import greenfootapi.enum_input_options as enum_opt
from datetime import datetime, date
from fastapi import File, UploadFile
import os
import random
import boto3
from dotenv import load_dotenv
from time import sleep


def get_all_tree_details_full_history_query_by_location(db: Session, lat: str, long: str, limit: int, query_dict: dict
= None):
    """
    Base query returns the query object for all tree details for all their history
    :param db:
    :return:
    """

    params = {"lat": lat, "long": long, "limit": limit}
    filters_str = ""
    if query_dict:
        query_list = []
        for col_name, value in query_dict.items():
            params[col_name] = value
            query_list.append(f"AND m1.{col_name} = :{col_name}")
        filters_str = "\n".join(query_list)
    return db.execute(
        text(

            f"""
SELECT m1.tree_id, 
m1.tree_change_datetime, 
m1.diameter_cm, 
m1.spread_radius_m, 
m1.tree_height_m, 
m1.longitude, 
m1.latitude, 
m1.tree_species_desc, 
m1.tree_species_type_desc, 
m1.tree_age_group_desc, 
m1.tree_surround_desc, 
m1.tree_vigour_desc, 
m1.tree_condition_desc, 
m1.tree_type_desc,
m1.tree_data_quality_id,
m1.tree_data_quality_desc,
m1.nickname, 
m1.tree_change_desc ,
t1.image_paths,
ROUND((ST_DISTANCE_SPHERE(
        POINT(m1.longitude, m1.latitude), 
        POINT(:long, :lat)) / 1000
        ), 2) tree_distance
FROM (
            SELECT tree.tree_id AS tree_id, 
            tree_history.tree_change_datetime AS tree_change_datetime, 
            tree_history.diameter_cm AS diameter_cm, 
            tree_history.spread_radius_m AS spread_radius_m, 
            tree_history.tree_height_m AS tree_height_m, 
            tree_history.longitude AS longitude, 
            tree_history.latitude AS latitude, 
            tree_species.tree_species_desc AS tree_species_desc, 
            tree_species_type.tree_species_type_desc AS tree_species_type_desc, 
            tree_age_group.tree_age_group_desc AS tree_age_group_desc, 
            tree_surround.tree_surround_desc AS tree_surround_desc, 
            tree_vigour.tree_vigour_desc AS tree_vigour_desc, 
            tree_type.tree_type_desc AS tree_type_desc,
            tree_condition.tree_condition_desc AS tree_condition_desc, 
            tree_data_quality.tree_data_quality_id AS tree_data_quality_id,
            tree_data_quality.tree_data_quality_desc AS tree_data_quality_desc,
            user.nickname AS nickname, 
            tree_history.tree_change_desc AS tree_change_desc 
            FROM tree_history 
            LEFT OUTER JOIN tree_species ON tree_history.tree_species_id = tree_species.tree_species_id 
            LEFT OUTER JOIN tree_species_type ON tree_species.tree_species_type_id = tree_species_type.tree_species_type_id 
            LEFT OUTER JOIN tree_age_group ON tree_age_group.tree_age_group_id = tree_history.tree_age_group_id 
            LEFT OUTER JOIN tree_condition ON tree_condition.tree_condition_id = tree_history.tree_condition_id 
            LEFT OUTER JOIN tree_data_quality ON tree_data_quality.tree_data_quality_id = tree_history.tree_data_quality_id 
            LEFT OUTER JOIN tree_surround ON tree_surround.tree_surround_id = tree_history.tree_surround_id 
            LEFT OUTER JOIN tree_vigour ON tree_vigour.tree_vigour_id = tree_history.tree_vigour_id 
            LEFT OUTER JOIN tree_type ON tree_type.tree_type_id = tree_history.tree_type_id
            INNER JOIN tree ON tree.tree_id = tree_history.tree_id 
            LEFT OUTER JOIN user ON user.user_id = tree_history.user_id 
            WHERE tree.inactive_datetime IS NULL
            ) AS m1 
JOIN (SELECT tree_history.tree_id AS tree_id, 
max(tree_history.tree_change_datetime) AS maxdate,
GROUP_CONCAT(image.image_path ORDER BY image.image_id ASC SEPARATOR ';') AS image_paths
FROM tree_history 
LEFT OUTER JOIN tree_image ti ON tree_history.tree_id = ti.tree_id
LEFT OUTER JOIN image ON ti.image_id = image.image_id
WHERE tree_history.is_live_change_ind > 0 
AND (ti.image_approved_ind = 1 OR ti.image_approved_ind IS NULL)
AND tree_history.latitude IS NOT NULL
GROUP BY tree_history.tree_id
) AS t1 
ON m1.tree_id = t1.tree_id 
WHERE m1.tree_change_datetime = t1.maxdate 
    AND m1.tree_id = t1.tree_id
    {filters_str}
ORDER BY ST_DISTANCE_SPHERE(
        POINT(m1.longitude, m1.latitude), 
        POINT(:long, :lat))
        LIMIT :limit
        """
        ), params
    ).all()


def get_all_tree_details_full_history_query(db: Session):
    """
    Base query returns the query object for all tree details for all their history
    :param db:
    :return:
    """
    return db.query(
        m.Tree.tree_id,
        m.Tree.inactive_datetime,
        m.TreeHistory.tree_history_id,
        m.TreeHistory.tree_change_datetime,
        m.TreeHistory.diameter_cm,
        m.TreeHistory.spread_radius_m,
        m.TreeHistory.tree_height_m,
        m.TreeHistory.location_x,
        m.TreeHistory.location_y,
        m.TreeHistory.longitude,
        m.TreeHistory.latitude,
        m.TreeHistory.tree_tag,
        m.TreeHistory.tree_change_desc,
        m.TreeType.tree_type_id,
        m.TreeType.tree_type_desc,
        m.TreeSpecies.tree_species_id,
        m.TreeSpecies.tree_species_desc,
        m.TreeSpeciesType.tree_species_type_desc,
        m.TreeAgeGroup.tree_age_group_id,
        m.TreeAgeGroup.tree_age_group_desc,
        m.TreeSurround.tree_surround_id,
        m.TreeSurround.tree_surround_desc,
        m.TreeVigour.tree_vigour_id,
        m.TreeVigour.tree_vigour_desc,
        m.TreeCondition.tree_condition_id,
        m.TreeCondition.tree_condition_desc,
        m.TreeDataQuality.tree_data_quality_id,
        m.TreeDataQuality.tree_data_quality_desc,
        m.User.user_id,
        m.User.nickname,
        m.User.noti_last_clicked

    ).join(
        m.TreeSpecies, m.TreeHistory.tree_species_id == m.TreeSpecies.tree_species_id, isouter=True).join(
        m.TreeSpeciesType, m.TreeSpecies.tree_species_type_id == m.TreeSpeciesType.tree_species_type_id,
        isouter=True).join(
        m.TreeAgeGroup, isouter=True).join(
        m.TreeType, isouter=True).join(
        m.TreeCondition, isouter=True).join(
        m.TreeDataQuality, isouter=True).join(
        m.TreeSurround, isouter=True).join(
        m.TreeVigour, isouter=True).join(
        m.Tree).join(
        m.User, isouter=True).filter(m.Tree.inactive_datetime.is_(None))


def get_latest_live_tree_details_query_all(db: Session):
    """
    Returns the query for the latest live version of every tree.
    :param db:
    :return:
    """
    subq = db.query(
        m.TreeHistory.tree_id,
        func.max(m.TreeHistory.tree_change_datetime).label("maxdate")
    ).filter(m.TreeHistory.is_live_change_ind > 0).group_by(
        m.TreeHistory.tree_id).subquery("t1")

    subq2 = get_all_tree_details_full_history_query(db).subquery("m1")

    query = db.query(subq2).join(subq).where(
        (subq2.c.tree_change_datetime == subq.c.maxdate) &
        (subq2.c.tree_id == subq.c.tree_id)
    ).order_by(subq.c.tree_id)
    return query


def get_latest_live_tree_details_query_by_id(db: Session, tree_id: int):
    """
    Returns the query for the latest live version of every tree.
    :param db:
    :return:
    """
    subq = db.query(
        m.TreeHistory.tree_id,
        func.max(m.TreeHistory.tree_change_datetime).label("maxdate")
    ).filter(m.TreeHistory.is_live_change_ind > 0,
             m.TreeHistory.tree_id == tree_id).group_by(
        m.TreeHistory.tree_id).subquery("t1")

    subq2 = get_all_tree_details_full_history_query(db).subquery("m1")

    query = db.query(subq2).join(subq).where(
        (subq2.c.tree_change_datetime == subq.c.maxdate) &
        (subq2.c.tree_id == subq.c.tree_id)
    ).order_by(subq.c.tree_id)
    return query


def run_automated_changes(db: Session, col_to_update: enum_opt.AutomatedChanges):
    col_val = col_to_update.value
    filter_col = getattr(m.TreeHistory, col_val)
    latest_live_trees = get_latest_live_tree_details_query_all(db).subquery()
    rows_to_update = db.query(
        m.TreeHistory.diameter_cm,
        m.TreeHistory.spread_radius_m,
        m.TreeHistory.tree_height_m,
        m.TreeHistory.location_x,
        m.TreeHistory.location_y,
        m.TreeHistory.longitude,
        m.TreeHistory.latitude,
        m.TreeHistory.tree_tag,
        m.TreeHistory.tree_type_id,
        m.TreeHistory.tree_species_id,
        m.TreeHistory.tree_age_group_id,
        m.TreeHistory.tree_surround_id,
        m.TreeHistory.tree_vigour_id,
        m.TreeHistory.tree_condition_id,
        m.TreeHistory.tree_data_quality_id,
        m.TreeHistory.tree_id
    ).filter(latest_live_trees.c.tree_history_id == m.TreeHistory.tree_history_id, filter_col < 0).all()
    rows_to_update = [row._asdict() for row in rows_to_update]

    for row_dict in rows_to_update:
        row_dict[col_val] = abs(row_dict[col_val])
        row_dict["tree_change_desc"] = f"Automated change: negative {col_val} changed to positive equivalent"
        row_dict["user_id"] = 1
        row_dict["is_live_change_ind"] = 1
        new_row = m.TreeHistory(**row_dict)
        db.add(new_row)
        db.commit()

    return {"row_changed_count": len(rows_to_update),
            "tree_ids_updated": [row_dict["tree_id"] for row_dict in rows_to_update]
            }


def get_latest_tree_details_all(db: Session, limit: int):
    query = get_latest_live_tree_details_query_all(db)
    return query.limit(limit).all()


def get_latest_tree_details_all_from_list(db: Session, trees_to_get: list):
    subq = db.query(
        m.TreeHistory.tree_id,
        func.max(m.TreeHistory.tree_change_datetime).label("maxdate")
    ).filter(m.TreeHistory.is_live_change_ind > 0, m.TreeHistory.tree_id.in_(trees_to_get)).group_by(
        m.TreeHistory.tree_id).subquery("t1")

    subq2 = get_all_tree_details_full_history_query(db).subquery("m1")

    query = db.query(subq2).join(subq).where(
        (subq2.c.tree_change_datetime == subq.c.maxdate) &
        (subq2.c.tree_id == subq.c.tree_id)
    ).order_by(subq.c.tree_id)
    return query.all()


def get_latest_tree_details_by_id(db: Session, tree_id: int):
    query = get_latest_live_tree_details_query_by_id(db, tree_id)
    return query.all()


def get_all_tree_details_by_id(db: Session, tree_id: int, limit: int, show_non_live: bool | None):
    query = get_all_tree_details_full_history_query(db)
    if show_non_live:
        q = query.filter(m.Tree.tree_id == tree_id)
    else:
        q = query.filter(m.Tree.tree_id == tree_id, m.TreeHistory.is_live_change_ind > 0)
    return q.order_by(m.TreeHistory.tree_change_datetime.desc()).limit(limit).all()


def get_all_tree_details_all(db: Session, limit: int, show_non_live: bool | None):
    query = get_all_tree_details_full_history_query(db)
    if not show_non_live:
        query = query.filter(m.TreeHistory.is_live_change_ind > 0)
    return query.order_by(m.Tree.tree_id, m.TreeHistory.tree_change_datetime.desc()).limit(limit).all()


def get_latest_tree_changes_home_page(db: Session, limit: int):
    query = get_all_tree_details_full_history_query(db)
    return query.filter(m.TreeHistory.is_live_change_ind > 0).order_by(
        m.TreeHistory.tree_change_datetime.desc()
    ).limit(limit).all()


def get_all_tree_details_to_approve_base(db: Session):
    sub_query = db.query(m.TreeHistory.tree_id).filter(m.TreeHistory.is_live_change_ind > 0).subquery()
    query = get_all_tree_details_full_history_query(db)
    query = query.filter(m.TreeHistory.is_live_change_ind == 0, m.TreeHistory.tree_id.in_(sub_query))
    return query


def get_all_new_trees_to_approve(db: Session, limit: int):
    sub_query = db.query(m.TreeHistory.tree_id).filter(m.TreeHistory.is_live_change_ind > 0).subquery()
    query = get_all_tree_details_full_history_query(db)
    query = query.filter(m.TreeHistory.is_live_change_ind == 0, ~m.TreeHistory.tree_id.in_(sub_query))
    return query.order_by(m.TreeHistory.tree_change_datetime).limit(limit).all()


def get_tree_deletion_requests(db: Session, limit: int):
    query = get_all_tree_details_full_history_query(db)
    filtered_query = query.filter(m.TreeHistory.is_live_change_ind == -2)
    return filtered_query.order_by(m.TreeHistory.tree_change_datetime.asc()).limit(limit).all()


def get_all_tree_details_to_approve_list(db: Session, limit: int):
    query = get_all_tree_details_to_approve_base(db)
    return query.order_by(m.TreeHistory.tree_change_datetime).limit(limit).all()


def get_tree_details_to_approve_id(db: Session, tree_id):
    base_query = get_all_tree_details_to_approve_base(db)
    if not tree_id:
        subq = base_query.subquery()
        tree_id = db.query(m.TreeHistory.tree_id
                           ).join(subq, m.TreeHistory.tree_history_id == subq.c.tree_history_id
                                  ).order_by(m.TreeHistory.tree_change_datetime.desc()).first()
        tree_id = tree_id[0]
    return base_query.filter(m.TreeHistory.tree_id == tree_id).order_by(m.TreeHistory.tree_change_datetime.desc(
    )).all()


def get_user_by_sub(db: Session, sub: s.UserAuth, get_first=False):
    user_query = db.query(m.User.user_id,
                          m.User.nickname,
                          m.User.given_name,
                          m.User.family_name,
                          m.User.email_verified,
                          m.User.user_type_id,
                          m.UserType.user_type_desc).join(
        m.UserType).filter(
        m.User.user_auth0_sub == sub.user_auth0_sub, m.User.is_active == 1)
    if get_first:
        return user_query.first()
    else:
        return user_query.all()


def get_user_by_id(db: Session, user_id: s.UserID):
    user_query = db.query(m.User.user_id,
                          m.User.nickname,
                          m.User.given_name,
                          m.User.family_name,
                          m.User.email_verified,
                          m.User.user_type_id,
                          m.UserType.user_type_desc).join(
        m.UserType).filter(
        m.User.user_id == user_id.user_id, m.User.is_active == 1)
    return user_query.all()


def create_user(db: Session, user: s.UserAdd):
    new_user = m.User(
        nickname=user.nickname,
        given_name=user.given_name,
        family_name=user.family_name,
        email_verified=user.email_verified,
        user_auth0_sub=user.user_auth0_sub,
        email=user.email,
        is_active=user.is_active,
        user_type_id=user.user_type_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def add_a_new_tree(db: Session, tree_details: s.AddANewTree):
    new_row = m.Tree()
    db.add(new_row)
    db.flush()
    new_tree_id = new_row.tree_id
    new_tree_history = m.TreeHistory(
        diameter_cm=tree_details.diameter_cm,
        spread_radius_m=tree_details.spread_radius_m,
        tree_height_m=tree_details.tree_height_m,
        longitude=tree_details.longitude,
        latitude=tree_details.latitude,
        tree_change_desc=tree_details.tree_change_desc,
        tree_type_id=tree_details.tree_type_id,
        tree_species_id=tree_details.tree_species_id,
        tree_age_group_id=tree_details.tree_age_group_id,
        tree_surround_id=tree_details.tree_surround_id,
        tree_vigour_id=tree_details.tree_vigour_id,
        tree_condition_id=tree_details.tree_condition_id,
        tree_data_quality_id=tree_details.tree_data_quality_id,
        tree_id=new_tree_id,
        user_id=tree_details.user_id
    )
    db.add(new_tree_history)
    db.commit()
    db.refresh(new_tree_history)
    return new_tree_history


def create_new_tree_history(db: Session, tree_hist: s.AllTreeHistoryTableAdd):
    new_tree_history = m.TreeHistory(
        diameter_cm=tree_hist.diameter_cm,
        spread_radius_m=tree_hist.spread_radius_m,
        tree_height_m=tree_hist.tree_height_m,
        location_x=tree_hist.location_x,
        location_y=tree_hist.location_y,
        longitude=tree_hist.longitude,
        latitude=tree_hist.latitude,
        tree_change_desc=tree_hist.tree_change_desc,
        is_live_change_ind=tree_hist.is_live_change_ind,
        tree_tag=tree_hist.tree_tag,
        tree_type_id=tree_hist.tree_type_id,
        tree_species_id=tree_hist.tree_species_id,
        tree_age_group_id=tree_hist.tree_age_group_id,
        tree_surround_id=tree_hist.tree_surround_id,
        tree_vigour_id=tree_hist.tree_vigour_id,
        tree_condition_id=tree_hist.tree_condition_id,
        tree_data_quality_id=tree_hist.tree_data_quality_id,
        tree_id=tree_hist.tree_id,
        user_id=tree_hist.user_id
    )
    db.add(new_tree_history)
    db.commit()
    db.refresh(new_tree_history)
    return new_tree_history


def update_user_details(db: Session, user_auth0_sub: str, update_vals: dict):
    db.query(m.User).filter(m.User.user_auth0_sub == user_auth0_sub).update(update_vals)
    db.commit()
    return db.query(m.User).filter(m.User.user_auth0_sub == user_auth0_sub).first()


def update_tree_status(db: Session, update_vals: [dict]):
    output_list = []
    for update_dict in update_vals:
        vals_to_update = {k: v for k, v in update_dict.items() if k != "tree_history_id"}
        db.query(m.TreeHistory).filter(m.TreeHistory.tree_history_id == update_dict["tree_history_id"]).update(
            vals_to_update)
        db.commit()
        output_list.append(db.query(m.TreeHistory).filter(m.TreeHistory.tree_history_id == update_dict[
            "tree_history_id"]).first())
    return output_list


def update_tree_inactive(db: Session, tree_id: int):
    update_dict = {"inactive_datetime": datetime.now()}
    db.query(m.Tree).filter(m.Tree.tree_id == tree_id).update(update_dict)
    db.commit()
    return db.query(m.Tree).filter(m.Tree.tree_id == tree_id).first()


def check_nickname_available(db: Session, nickname: str):
    users_found = db.query(m.User).filter(m.User.nickname == nickname).all()
    nickname_available = False
    if len(users_found) == 0:
        nickname_available = True
    return {"user_available": nickname_available}


def get_discrete_tree_desc_options(db: Session, table_name: enum_opt):
    table_to_table_obj_dict = {
        'tree_vigour': m.TreeVigour,
        'tree_surround': m.TreeSurround,
        'tree_data_quality': m.TreeDataQuality,
        'tree_condition': m.TreeCondition,
        'tree_age_group': m.TreeAgeGroup,
        'tree_type': m.TreeType
    }
    table_name_str = table_name.value
    table_model = table_to_table_obj_dict[table_name_str]
    q_output = db.query(table_model).all()

    values_list = []
    for obj in q_output:
        output_dict = {}
        for k, v in obj.__dict__.items():
            if k == f"{table_name_str}_id":
                output_dict["table_id"] = v
            elif k == f"{table_name_str}_desc":
                output_dict["table_desc"] = v
        values_list.append(output_dict)

    return values_list


def get_discrete_tree_species_options(db: Session, tree_species_type: str):
    output_list = db.query(m.TreeSpecies.tree_species_id, m.TreeSpecies.tree_species_desc).join(
        m.TreeSpeciesType).filter(m.TreeSpeciesType.tree_species_type_desc == tree_species_type).distinct().all()
    output_dict = [{"table_id": i[0], "table_desc": i[1]} for i in output_list]
    return output_dict


def get_discrete_tree_species_type_options(db: Session):
    output_list = db.query(m.TreeSpeciesType.tree_species_type_id, m.TreeSpeciesType.tree_species_type_desc).join(
        m.TreeSpecies).distinct().all()
    output_dict = [{"table_id": i[0], "table_desc": i[1]} for i in output_list]
    return output_dict


def check_if_model_is_running():
    session = boto3.Session(aws_access_key_id=os.getenv("ACCESS_KEY"),
                            aws_secret_access_key=os.getenv("ACCESS_SECRET")
                            )
    rekognition_client = session.client("rekognition")
    project_arn = os.getenv("REKO_PROJECT_ARN")
    project_version = os.getenv("REKO_PROJECT_VERSION")
    describe_response = rekognition_client.describe_project_versions(ProjectArn=project_arn,
                                                                     VersionNames=[project_version])
    model_status = None
    for model in describe_response['ProjectVersionDescriptions']:
        model_status = model['Status']
    return {"a_model_status": model_status}


def get_latest_species_type_analysis(db: Session):
    subq = get_latest_live_tree_details_query_all(db).subquery("m1")
    all_tree_details = (db.query(subq.c.tree_id,
                                 subq.c.tree_species_type_desc,
                                 subq.c.tree_change_datetime,
                                 subq.c.nickname,
                                 m.Image.image_id,
                                 m.Image.image_path,
                                 m.TreeImage.tree_image_id,
                                 m.TreeImage.image_add_datetime,
                                 m.TreeImage.last_ai_analysis,
                                 m.TreeImage.latest_labels,
                                 m.User.user_id.label("image_user_id"),
                                 m.User.nickname.label("image_nickname")
                                 ).join(
        m.TreeImage, subq.c.tree_id == m.TreeImage.tree_id).join(
        m.Image, m.TreeImage.image_id == m.Image.image_id).join(m.User, m.Image.user_id == m.User.user_id).filter(
        m.TreeImage.image_end_datetime.is_(None),
        m.TreeImage.image_approved_ind == 1
    ).all())
    return all_tree_details


def analyse_species_type(db: Session):
    session = boto3.Session(aws_access_key_id=os.getenv("ACCESS_KEY"),
                            aws_secret_access_key=os.getenv("ACCESS_SECRET")
                            )
    rekognition_client = session.client("rekognition")
    full_arn = os.getenv("REKO_FULL_ARN")
    project_arn = os.getenv("REKO_PROJECT_ARN")
    project_version = os.getenv("REKO_PROJECT_VERSION")

    # Starting model:
    try:
        # Start the model
        response = rekognition_client.start_project_version(ProjectVersionArn=full_arn, MinInferenceUnits=1)
        # Wait for the model to be in the running state
        print("Waiting for model to start...")
        project_version_running_waiter = rekognition_client.get_waiter('project_version_running')
        project_version_running_waiter.wait(ProjectArn=project_arn, VersionNames=[project_version])

        # Get the running status
        describe_response = rekognition_client.describe_project_versions(ProjectArn=project_arn,
                                                                         VersionNames=[project_version])
        for model in describe_response['ProjectVersionDescriptions']:
            print("Status: " + model['Status'])
            print("Message: " + model['StatusMessage'])
    except Exception as e:
        print(e)

    print('Done...')

    # Get DB images to analyse:
    subq = get_latest_live_tree_details_query_all(db).subquery("m1")
    all_tree_details = (db.query(subq.c.tree_id,
                                 subq.c.tree_species_type_desc,
                                 subq.c.tree_change_datetime,
                                 subq.c.nickname,
                                 m.Image.image_id,
                                 m.Image.image_path,
                                 m.TreeImage.tree_image_id,
                                 m.TreeImage.image_add_datetime,
                                 m.TreeImage.last_ai_analysis
                                 ).join(
        m.TreeImage, subq.c.tree_id == m.TreeImage.tree_id).join(
        m.Image, m.TreeImage.image_id == m.Image.image_id).filter(
        m.TreeImage.image_end_datetime.is_(None),
        m.TreeImage.image_approved_ind == 1
    ).all())
    cwd = os.getcwd()
    row_maps = [dict(item._mapping) for item in all_tree_details]

    all_labels = []
    for item in row_maps:
        current_custom_labels = item
        image_path = os.path.join(cwd, item["image_path"])
        image_path = image_path.replace("\\", "/")

        with open(image_path, 'rb') as image_file:
            image_bytes = image_file.read()
            # Call Rekognition to detect custom labels
            try:
                response = rekognition_client.detect_custom_labels(
                    ProjectVersionArn=full_arn,
                    Image={'Bytes': image_bytes},
                    MaxResults=3
                )
                print(response)
                response_list = response["CustomLabels"]
            except Exception:
                response_list = []
        current_custom_labels["labels"] = response_list
        print(response_list)
        update_last_run = {"last_ai_analysis": datetime.now(), "latest_labels": str(response_list)}
        db.query(m.TreeImage).filter(m.TreeImage.tree_image_id == item["tree_image_id"]).update(update_last_run)
        db.flush()
        all_labels.append(current_custom_labels)
    # Stop the model
    try:
        rekognition_client.stop_project_version(
            ProjectVersionArn=full_arn
        )
    except Exception as e:
        return "model_not_stopped"

    for i in all_labels:
        print("=" * 100)
        for k, v in i.items():
            print(k, v)

    db.commit()
    return all_labels


async def check_image_contains_tree(file: UploadFile = File(...)):
    allowed_extnesions = ["jpg", "png"]
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in allowed_extnesions:
        return "invalid_extension"
    session = boto3.Session(aws_access_key_id=os.getenv("ACCESS_KEY"),
                            aws_secret_access_key=os.getenv("ACCESS_SECRET")
                            )
    rekognition = session.client("rekognition")

    image_bytes = await file.read()

    try:
        response = rekognition.detect_labels(
            Image={'Bytes': image_bytes},
            MaxLabels=15,
            MinConfidence=40
        )
    except Exception as e:
        return "processing_error"
    labels = response["Labels"]

    labels = [{k: v for k, v in d.items() if k in ["Name", "Confidence"]} for d in labels]
    return labels


async def upload_image(db: Session, tree_id: int, user_id: int, file: UploadFile = File(...)):
    uploads_dir = "tree_images"
    tree_image_dir = os.path.join(uploads_dir, str(tree_id))
    file_location = os.path.join(tree_image_dir, file.filename)

    file_location_raw = file_location.replace("\\", "/")

    file_path_exists = db.query(exists().where(m.Image.image_path == file_location)).scalar()

    if file_path_exists:
        return "image_already_exists"

    # Add to image table
    new_image = m.Image(image_path=file_location_raw, user_id=user_id)
    db.add(new_image)
    db.flush()
    new_image_id = new_image.image_id

    # Upload the image to the server
    if not os.path.exists(tree_image_dir):
        os.makedirs(tree_image_dir)

    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Add the path to the db
    new_tree_image = m.TreeImage(image_approved_ind=0, tree_id=tree_id, image_id=new_image_id)
    db.add(new_tree_image)
    db.commit()

    return {"filename": file.filename, "url": file_location}


def get_images_to_approve(db: Session, limit: int):
    return db.query(m.Image.image_path,
                    m.Image.image_id,
                    m.TreeImage.tree_id,
                    m.TreeImage.image_add_datetime,
                    m.User.nickname,
                    m.TreeImage.image_approved_ind).join(m.TreeImage).join(m.Tree).join(m.User).filter(
        m.TreeImage.image_approved_ind == 0,
        m.Tree.inactive_datetime.is_(None)).limit(limit).all()


def get_approved_images(db: Session, tree_id: int, limit: int):
    return db.query(m.Image.image_path,
                    m.Image.image_id,
                    m.TreeImage.tree_id,
                    m.TreeImage.image_add_datetime,
                    m.User.nickname,
                    m.TreeImage.image_approved_ind).join(m.TreeImage).join(m.Tree).join(m.User).filter(
        m.TreeImage.tree_id == tree_id,
        m.TreeImage.image_approved_ind == 1).limit(limit).all()


def update_image_approval(db: Session, update_vals: dict):
    tree_id_to_update = update_vals["tree_id"]
    image_approved_dict = {k: v for k, v in update_vals.items() if k == "image_approved_ind"}
    db.query(m.TreeImage).filter(m.TreeImage.tree_id == tree_id_to_update).update(image_approved_dict)
    db.commit()
    return db.query(m.TreeImage.image_approved_ind).filter(m.TreeImage.tree_id == tree_id_to_update).first()


def _find_current_daily_image(db):
    return db.query(m.TreeDailyImage.tree_image_id).filter(
        func.date(m.TreeDailyImage.daily_image_date) == date.today()
    ).scalar()


def get_daily_image(db: Session):
    tree_image_id = _find_current_daily_image(db)
    if not tree_image_id:
        all_approved_images = db.query(m.TreeImage.tree_image_id).join(m.Tree).filter(
            m.TreeImage.image_approved_ind == 1,
            m.Tree.inactive_datetime.is_(None)
        ).all()
        new_tree_of_day = random.sample(all_approved_images, 1)[0][0]
        db.add(m.TreeDailyImage(tree_image_id=new_tree_of_day))
        db.commit()
        tree_image_id = _find_current_daily_image(db)
    return db.query(m.Image.image_path,
                    m.Image.image_id,
                    m.TreeImage.tree_id,
                    m.TreeImage.image_add_datetime,
                    m.User.nickname,
                    m.TreeImage.image_approved_ind).join(m.TreeImage).join(m.Tree).join(m.User).filter(
        m.TreeImage.tree_image_id == tree_image_id
    ).first()


def _object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def get_analytics_groupby(db: Session, group_by_name: enum_opt,
                          filter_dict: dict):
    groupby_str = group_by_name.value + "_desc"
    subq = db.query(
        m.TreeHistory.tree_id,
        func.max(m.TreeHistory.tree_change_datetime).label("maxdate")
    ).filter(m.TreeHistory.is_live_change_ind > 0).group_by(
        m.TreeHistory.tree_id).subquery("t1")

    subq2 = get_all_tree_details_full_history_query(db).subquery("m1")

    col_attr = getattr(subq2.c, groupby_str)
    query = db.query(col_attr, func.count(subq2.c.tree_history_id).label("total")).join(subq).where(
        (subq2.c.tree_change_datetime == subq.c.maxdate) &
        (subq2.c.tree_id == subq.c.tree_id)
    )
    if filter_dict:
        for col, value in filter_dict.items():
            query = query.filter(getattr(subq2.c, col) == value)
    query = query.group_by(col_attr).all()
    return {"group_by_counts": [item._mapping for item in query]}


def get_analytics_row_data(db: Session, filter_dict: dict, limit: int):
    subq = db.query(
        m.TreeHistory.tree_id,
        func.max(m.TreeHistory.tree_change_datetime).label("maxdate")
    ).filter(m.TreeHistory.is_live_change_ind > 0).group_by(
        m.TreeHistory.tree_id).subquery("t1")

    subq2 = get_all_tree_details_full_history_query(db).subquery("m1")

    query = db.query(subq2).join(subq).where(
        (subq2.c.tree_change_datetime == subq.c.maxdate) &
        (subq2.c.tree_id == subq.c.tree_id)
    )
    if filter_dict:
        for col, value in filter_dict.items():
            query = query.filter(getattr(subq2.c, col) == value)
    return query.order_by(subq2.c.tree_change_datetime.desc()).limit(limit).all()


def get_user_notifications(db: Session, user_id: int = None, limit: int = None, approved_only: bool = False):
    if not limit:
        limit = 10
    params = {"limit": limit}
    noti_clicked_order = ""
    filter_query = "WHERE subq.change_ind > 0"
    if user_id:
        params["user_id"] = user_id
        filter_query = "WHERE subq.user_id = :user_id"
        if approved_only:
            filter_query += " AND subq.change_ind > 0"
        noti_clicked_order = "noti_clicked_ind, "

    main_sql_query = f"""
       SELECT subq.*,
   CASE WHEN subq.noti_last_clicked < subq.comb_date THEN 0 ELSE 1 END noti_clicked_ind
   FROM 
   		( 
            SELECT 
            tr.tree_id,
            th.tree_change_desc,
            u.user_id,
            u.nickname,
            u.noti_last_clicked,
            th.is_live_change_ind AS change_ind,
            th.tree_change_datetime AS comb_date,
            CASE WHEN th.is_live_change_ind IN (-5, 4) THEN 'deletion'
            WHEN th.is_live_change_ind IN (1, -1) THEN 'edit'
            WHEN th.is_live_change_ind IN (2, -3) THEN 'new tree'
            END change_type

            FROM tree_history th 
            INNER JOIN tree tr 
            ON th.tree_id = tr.tree_id
            LEFT JOIN user u 
            ON th.user_id = u.user_id
            WHERE th.is_live_change_ind IN (-5, -3, -1, 1, 2, 4)

            UNION ALL 

            -- Images
            SELECT
            tr.tree_id,
            'new tree image' tree_change_desc,
            u.user_id,
            u.nickname,
            u.noti_last_clicked,
            ti.image_approved_ind AS change_ind,
            ti.image_add_datetime AS comb_date,
            'image' change_type
            FROM tree_image ti 
            INNER JOIN tree tr 
            ON ti.tree_id = tr.tree_id
            INNER JOIN image i 
            ON ti.image_id = i.image_id
            INNER JOIN user u 
            ON i.user_id = u.user_id
            WHERE tr.inactive_datetime IS NULL 
            AND ti.image_approved_ind != 0
        ) subq
   {filter_query}
  ORDER BY {noti_clicked_order} subq.comb_date DESC
  LIMIT :limit
    """
    return db.execute(text(main_sql_query), params).all()


def update_user_notification_date(db: Session, user_id: int):
    update_dict = {"noti_last_clicked": datetime.now()}
    db.query(m.User).filter(m.User.user_id == user_id).update(update_dict)
    db.commit()
    return db.query(m.User).filter(m.User.user_id == user_id).first()


def get_image_properties():
    session = boto3.Session(aws_access_key_id=os.getenv("ACCESS_KEY"),
                            aws_secret_access_key=os.getenv("ACCESS_SECRET")
                            )
    rekognition = session.client("rekognition")
    image_path = r"C:\Users\James\Documents\MSc Software\Final Project\greenfoot-app\tree_images\19461\IMG-20240824-WA0034.jpg"

    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()

    # Call Rekognition to detect labels
    response = rekognition.detect_labels(
        Image={'Bytes': image_bytes},
        MaxLabels=10,
        MinConfidence=90
    )
    print(response)
