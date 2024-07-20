import models as m
from sqlalchemy.orm import Session


def get_all_tree_details_query(db: Session):
    return db.query(
        m.Tree.tree_id,
        m.Tree.diameter_cm,
        m.Tree.spread_radius_m,
        m.Tree.tree_height_m,
        m.Tree.longitude,
        m.Tree.latitude,
        m.TreeSpecies.tree_species_desc,
        m.TreeSpeciesType.tree_species_type_desc,
        m.TreeAgeGroup.tree_age_group_desc,
        m.TreeSurround.tree_surround_desc,
        m.TreeVigour.tree_vigour_desc,
        m.TreeCondition.tree_condition_desc,
    ).join(
        m.TreeSpecies, m.Tree.tree_species_id == m.TreeSpecies.tree_species_id).join(
        m.TreeSpeciesType, m.TreeSpecies.tree_species_type_id == m.TreeSpeciesType.tree_species_type_id).join(
        m.TreeAgeGroup).join(
        m.TreeCondition).join(
        m.TreeDataQuality).join(
        m.TreeSurround).join(
        m.TreeVigour)


def get_all_tree_details_by_id(db: Session, tree_id: int, limit: int):
    query = get_all_tree_details_query(db)
    return query.filter(m.Tree.tree_id == tree_id).order_by(m.Tree.tree_id).limit(limit).all()


def get_all_tree_details_all(db: Session, limit: int):
    query = get_all_tree_details_query(db)
    return query.order_by(m.Tree.tree_id).limit(limit).all()
