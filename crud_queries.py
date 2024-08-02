import models as m
import schemas as s
from sqlalchemy.orm import Session
from sqlalchemy import func


# class TreeDataGetter:
#     tree_data_rows_select = """
#     t.tree_id,
#     th.diameter_cm,
#     th.spread_radius_m,
#     th.tree_height_m,
#     th.longitude,
#     th.latitude,
#     ts.tree_species_desc,
#     tst.tree_species_type_desc,
#     tag.tree_age_group_desc,
#     m.TreeSurround.tree_surround_desc,
#     m.TreeVigour.tree_vigour_desc,
#     m.TreeCondition.tree_condition_desc
#     """
#
#     def __init__(self, db: Session):
#         self.db = db
#
#     def get_all_trees_full_history_query(self):
#         return """
#         SELECT *
#         FROM tree_history th
#         INNER JOIN tree_species ts
#         ON th.tree_species_id = ts.tree_species_id
#         INNER JOIN tree_species_type tst
#         ON ts.tree_species_type_id = tst.tree_species_type_id
#         INNER JOIN tree_age_group tag
#         ON tsh.tree_age_group_id = tag.tree_age_group_id
#         INNER JOIN tree_condition tc
#         ON th.tree_condition_id = tc.tree_condition_id
#         INNER JOIN tree_data_quality tdq
#         ON th.tree_data_quality_id = tdq.tree_data_quality_id
#         INNER JOIN tree_surround ts
#         ON th.tree_surround_id = ts.tree_surround_id
#         INNER JOIN tree_vigour tv
#         ON th.tree_vigour_id = tv.tree_vigour_id
#         INNER JOIN tree t
#         ON th.tree_history_id = t.tree_history_id
#         """


def get_all_tree_details_full_history_query(db: Session):
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

    ).join(
        m.TreeSpecies, m.TreeHistory.tree_species_id == m.TreeSpecies.tree_species_id, isouter=True).join(
        m.TreeSpeciesType, m.TreeSpecies.tree_species_type_id == m.TreeSpeciesType.tree_species_type_id,
        isouter=True).join(
        m.TreeAgeGroup, isouter=True).join(
        m.TreeCondition, isouter=True).join(
        m.TreeDataQuality, isouter=True).join(
        m.TreeSurround, isouter=True).join(
        m.TreeVigour, isouter=True).join(
        m.Tree)


def get_all_tree_details_full_history_queryv2(db: Session):
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


def get_all_tree_details_by_id(db: Session, tree_id: int, limit: int):
    query = get_all_tree_details_full_history_query(db)
    return query.filter(m.Tree.tree_id == tree_id).order_by(m.Tree.tree_id).limit(limit).all()


def get_all_tree_details_full_history(db: Session, limit: int):
    query = get_all_tree_details_full_history_queryv2(db)
    return query.limit(limit).all()


"""
    nickname: str
    given_name: Optional[str]
    family_name: Optional[str]
    email_verified: Optional[int]
    user_type_desc: str
"""


def get_user_by_sub(db: Session, sub: s.UserAuth):
    return db.query(m.User.nickname,
                    m.User.given_name,
                    m.User.family_name,
                    m.User.email_verified,
                    m.UserType.user_type_desc).join(
        m.UserType).filter(
        m.User.user_auth0_sub == sub.user_auth0_sub, m.User.is_active == 1).all()


def create_user(db: Session, user: s.UserBase):
    new_user = m.User(
        user_auth0_sub=user.user_auth0_sub,
        nickname=user.nickname,
        given_name=user.given_name,
        family_name=user.family_name,
        email_verified=user.email_verified
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def check_nickname_exists(db: Session, nickname: str):
    users_found = db.query(m.User).filter(m.User.nickname == nickname).all()
    nickname_exists = False
    if len(users_found) == 0:
        nickname_exists = True
    return {"user_exists": nickname_exists}


def put_add_new_tree_history(db: Session, tree_id: int):
    get_all_tree_details_by_id(db, tree_id)
