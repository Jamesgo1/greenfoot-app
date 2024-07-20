from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from database import Base


class Badge(Base):
    __tablename__ = 'badge'

    badge_id = Column(Integer(), primary_key=True)
    badge_name = Column(String(255), nullable=False)
    badge_desc = Column(Text, nullable=False)


class Image(Base):
    __tablename__ = 'image'

    image_id = Column(Integer(), primary_key=True)
    image_path = Column(String(255), nullable=False)
    image_type_id = Column(Integer(), nullable=False)


class ImageType(Base):
    __tablename__ = 'image_type'

    image_type_id = Column(Integer(), primary_key=True)
    image_desc = Column(String(255), nullable=False)


class TreeAgeGroup(Base):
    __tablename__ = 'tree_age_group'

    tree_age_group_id = Column(Integer(), primary_key=True)
    tree_age_group_desc = Column(String(255), nullable=False)


class TreeCondition(Base):
    __tablename__ = 'tree_condition'

    tree_condition_id = Column(Integer(), primary_key=True)
    tree_condition_desc = Column(String(255), nullable=False)


class TreeDataQuality(Base):
    __tablename__ = 'tree_data_quality'

    tree_data_quality_id = Column(Integer(), primary_key=True)
    tree_data_quality_desc = Column(String(255), nullable=False)


class TreeImage(Base):
    __tablename__ = 'tree_image'

    tree_image_id = Column(Integer(), primary_key=True)
    image_id = Column(Integer(), nullable=False)
    tree_id = Column(Integer(), nullable=False)


class TreeSpeciesType(Base):
    __tablename__ = 'tree_species_type'

    tree_species_type_id = Column(Integer(), primary_key=True)
    tree_species_type_desc = Column(String(255), nullable=False)


class TreeSurround(Base):
    __tablename__ = 'tree_surround'

    tree_surround_id = Column(Integer(), primary_key=True)
    tree_surround_desc = Column(String(255), nullable=False)


class TreeType(Base):
    __tablename__ = 'tree_type'

    tree_type_id = Column(Integer(), primary_key=True)
    tree_type_desc = Column(String(255), nullable=False)


class TreeVigour(Base):
    __tablename__ = 'tree_vigour'

    tree_vigour_id = Column(Integer(), primary_key=True)
    tree_vigour_desc = Column(String(255), nullable=False)


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer(), primary_key=True)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)


class UserBadgeLink(Base):
    __tablename__ = 'user_badge_link'

    user_badge_link_id = Column(Integer(), primary_key=True)
    badge_id = Column(Integer(), nullable=False)
    user_id = Column(Integer(), nullable=False)


class UserDetail(Base):
    __tablename__ = 'user_details'

    user_details_id = Column(Integer(), primary_key=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    postcode = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    creation_datetime = Column(String(255), nullable=False)
    end_datetime = Column(String(255), nullable=False)
    image_id = Column(Integer(), nullable=False)
    user_id = Column(Integer(), nullable=False)


class UserLoginHist(Base):
    __tablename__ = 'user_login_hist'

    user_login_hist_id = Column(Integer(), primary_key=True)
    login_datetime = Column(Integer(), nullable=False)
    success_ind = Column(Integer(), nullable=False)
    user_id = Column(Integer(), nullable=False)


class TreeSpecies(Base):
    __tablename__ = 'tree_species'

    tree_species_id = Column(Integer(), primary_key=True)
    tree_species_desc = Column(String(255), nullable=False)
    tree_species_type_id = Column(ForeignKey('tree_species_type.tree_species_type_id'), nullable=False, index=True)

    tree_species_type = relationship('TreeSpeciesType', primaryjoin=tree_species_type_id ==
                                                                    TreeSpeciesType.tree_species_type_id)


class Tree(Base):
    __tablename__ = 'tree'

    tree_id = Column(Integer(), primary_key=True)
    diameter_cm = Column(Integer())
    spread_radius_m = Column(Integer())
    tree_height_m = Column(Integer())
    location_x = Column(Float(9))
    location_y = Column(Float(9))
    longitude = Column(Float(9))
    latitude = Column(Float(8))
    tree_tag = Column(Integer())
    tree_type_id = Column(ForeignKey('tree_type.tree_type_id'), index=True)
    tree_species_id = Column(ForeignKey('tree_species.tree_species_id'), index=True)
    tree_age_group_id = Column(ForeignKey('tree_age_group.tree_age_group_id'), index=True)
    tree_surround_id = Column(ForeignKey('tree_surround.tree_surround_id'), index=True)
    tree_vigour_id = Column(ForeignKey('tree_vigour.tree_vigour_id'), index=True)
    tree_condition_id = Column(ForeignKey('tree_condition.tree_condition_id'), index=True)
    tree_data_quality_id = Column(ForeignKey('tree_data_quality.tree_data_quality_id'), index=True)

    tree_age_group = relationship('TreeAgeGroup')
    tree_condition = relationship('TreeCondition')
    tree_data_quality = relationship('TreeDataQuality')
    tree_species = relationship('TreeSpecies')
    tree_surround = relationship('TreeSurround')
    tree_type = relationship('TreeType')
    tree_vigour = relationship('TreeVigour')
