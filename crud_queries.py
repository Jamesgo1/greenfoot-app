import models as m
import schemas as s
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.dialects import mysql
from sqlalchemy import select, column
import enum_input_options as enum_opt


def get_all_tree_details_full_history_query_by_location(db: Session, lat: str, long: str, limit: int):
    """
    Base query returns the query object for all tree details for all their history
    :param db:
    :return:
    """
    params = {"lat": lat, "long": long, "limit": limit}
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
m1.nickname, 
m1.tree_change_desc 
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
            tree_condition.tree_condition_desc AS tree_condition_desc, 
            user.nickname AS nickname, 
            tree_change.tree_change_desc AS tree_change_desc 
            FROM tree_history 
            LEFT OUTER JOIN tree_species ON tree_history.tree_species_id = tree_species.tree_species_id 
            LEFT OUTER JOIN tree_species_type ON tree_species.tree_species_type_id = tree_species_type.tree_species_type_id 
            LEFT OUTER JOIN tree_age_group ON tree_age_group.tree_age_group_id = tree_history.tree_age_group_id 
            LEFT OUTER JOIN tree_condition ON tree_condition.tree_condition_id = tree_history.tree_condition_id 
            LEFT OUTER JOIN tree_data_quality ON tree_data_quality.tree_data_quality_id = tree_history.tree_data_quality_id 
            LEFT OUTER JOIN tree_surround ON tree_surround.tree_surround_id = tree_history.tree_surround_id 
            LEFT OUTER JOIN tree_vigour ON tree_vigour.tree_vigour_id = tree_history.tree_vigour_id 
            INNER JOIN tree ON tree.tree_id = tree_history.tree_id 
            LEFT OUTER JOIN user ON user.user_id = tree_history.user_id 
            LEFT OUTER JOIN tree_change ON tree_change.tree_change_id = tree_history.tree_change_id
            ) AS m1 
JOIN (SELECT tree_history.tree_id AS tree_id, max(tree_history.tree_change_datetime) AS maxdate 
FROM tree_history 
WHERE tree_history.is_live_change_ind = 1 
AND tree_history.latitude IS NOT NULL
GROUP BY tree_history.tree_id) AS t1 
ON m1.tree_id = t1.tree_id 
WHERE m1.tree_change_datetime = t1.maxdate 
    AND m1.tree_id = t1.tree_id 
ORDER BY ST_DISTANCE(
        POINT(m1.latitude, m1.longitude), 
        POINT(:lat, :long)
        )
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
        m.TreeHistory.tree_change_datetime,
        m.TreeHistory.diameter_cm,
        m.TreeHistory.spread_radius_m,
        m.TreeHistory.tree_height_m,
        m.TreeHistory.longitude,
        m.TreeHistory.latitude,
        m.TreeSpecies.tree_species_desc,
        m.TreeSpeciesType.tree_species_type_desc,
        m.TreeAgeGroup.tree_age_group_desc,
        m.TreeSurround.tree_surround_desc,
        m.TreeVigour.tree_vigour_desc,
        m.TreeCondition.tree_condition_desc,
        m.User.nickname,
        m.TreeChange.tree_change_desc

    ).join(
        m.TreeSpecies, m.TreeHistory.tree_species_id == m.TreeSpecies.tree_species_id, isouter=True).join(
        m.TreeSpeciesType, m.TreeSpecies.tree_species_type_id == m.TreeSpeciesType.tree_species_type_id,
        isouter=True).join(
        m.TreeAgeGroup, isouter=True).join(
        m.TreeCondition, isouter=True).join(
        m.TreeDataQuality, isouter=True).join(
        m.TreeSurround, isouter=True).join(
        m.TreeVigour, isouter=True).join(
        m.Tree).join(
        m.User, isouter=True).join(
        m.TreeChange, isouter=True)


def get_latest_live_tree_details_query(db: Session):
    """
    Returns the query for the latest live version of every tree.
    :param db:
    :return:
    """
    subq = db.query(
        m.TreeHistory.tree_id,
        func.max(m.TreeHistory.tree_change_datetime).label("maxdate")
    ).filter(m.TreeHistory.is_live_change_ind == 1).group_by(m.TreeHistory.tree_id).subquery("t1")

    subq2 = get_all_tree_details_full_history_query(db).subquery("m1")

    query = db.query(subq2).join(subq).where(
        (subq2.c.tree_change_datetime == subq.c.maxdate) &
        (subq2.c.tree_id == subq.c.tree_id)
    ).order_by(subq.c.tree_id)
    return query


def get_latest_tree_details_all(db: Session, limit: int):
    query = get_latest_live_tree_details_query(db)
    return query.limit(limit).all()


def get_latest_tree_details_by_id(db: Session, tree_id: int, limit: int):
    query = get_latest_live_tree_details_query(db)
    return query.filter(m.Tree.tree_id == tree_id).order_by(m.Tree.tree_id).limit(limit).all()


def get_all_tree_details_by_id(db: Session, tree_id: int, limit: int):
    query = get_all_tree_details_full_history_query(db)
    return query.filter(m.Tree.tree_id == tree_id).order_by(m.TreeHistory.tree_change_datetime.desc()).limit(
        limit).all()


def get_all_tree_details_all(db: Session, limit: int):
    query = get_all_tree_details_full_history_query(db)
    return query.order_by(m.Tree.tree_id, m.TreeHistory.tree_change_datetime.desc()).limit(limit).all()


def get_user_by_sub(db: Session, sub: s.UserAuth):
    return db.query(m.User.user_id,
                    m.User.nickname,
                    m.User.given_name,
                    m.User.family_name,
                    m.User.email_verified,
                    m.UserType.user_type_desc).join(
        m.UserType).filter(
        m.User.user_auth0_sub == sub.user_auth0_sub, m.User.is_active == 1).all()


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


def update_user_details(db: Session, user_auth0_sub: str, update_vals: dict):
    db.query(m.User).filter(m.User.user_auth0_sub == user_auth0_sub).update(update_vals)
    db.commit()
    return db.query(m.User).filter(m.User.user_auth0_sub == user_auth0_sub).first()


def check_nickname_available(db: Session, nickname: str):
    users_found = db.query(m.User).filter(m.User.nickname == nickname).all()
    nickname_available = False
    if len(users_found) == 0:
        nickname_available = True
    return {"user_available": nickname_available}


def put_add_new_tree_history(db: Session, tree_id: int):
    get_all_tree_details_by_id(db, tree_id)


def get_discrete_tree_desc_options(db: Session, table_name: enum_opt):
    table_to_table_obj_dict = {
        'tree_species': m.TreeSpecies,
        'tree_vigour': m.TreeVigour,
        'tree_surround': m.TreeSurround,
        'tree_data_quality': m.TreeDataQuality,
        'tree_condition': m.TreeCondition,
        'tree_age_group': m.TreeAgeGroup,
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


def get_discrete_tree_species_options(db: Session):
    output_list = db.query(m.TreeSpeciesType.tree_species_type_id, m.TreeSpeciesType.tree_species_type_desc).join(
        m.TreeSpecies).distinct().all()
    output_dict = [{"table_id": i[0], "table_desc": i[1]} for i in output_list]
    return output_dict
