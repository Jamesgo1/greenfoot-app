# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, TIMESTAMP, Text, text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, LONGTEXT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import FetchedValue

Base = declarative_base()
metadata = Base.metadata


class Image(Base):
    __tablename__ = 'image'

    image_id = Column(INTEGER(11), primary_key=True)
    image_path = Column(String(255), nullable=False)
    user_id = Column(ForeignKey('user.user_id'), nullable=True, index=True)

    user = relationship('User')


class ImageTag(Base):
    __tablename__ = 'image_tag'

    image_tag_id = Column(INTEGER(11), primary_key=True)
    image_tag_desc = Column(String(255), nullable=False)


class Tree(Base):
    __tablename__ = 'tree'

    tree_id = Column(INTEGER(11), primary_key=True)
    inactive_datetime = Column(TIMESTAMP)


class TreeAgeGroup(Base):
    __tablename__ = 'tree_age_group'

    tree_age_group_id = Column(INTEGER(11), primary_key=True)
    tree_age_group_desc = Column(String(255), nullable=False)


class TreeCondition(Base):
    __tablename__ = 'tree_condition'

    tree_condition_id = Column(INTEGER(11), primary_key=True)
    tree_condition_desc = Column(String(255), nullable=False)


class TreeDataQuality(Base):
    __tablename__ = 'tree_data_quality'

    tree_data_quality_id = Column(INTEGER(11), primary_key=True)
    tree_data_quality_desc = Column(String(255), nullable=False)


class TreeDailyImage(Base):
    __tablename__ = "tree_daily_image"

    tree_daily_image_id = Column(INTEGER(11), primary_key=True)
    daily_image_date = Column(DateTime, nullable=False, server_default=text("current_timestamp()"))
    tree_image_id = Column(ForeignKey('tree_image.tree_image_id'), nullable=False, index=True)

    tree_image = relationship('TreeImage')


class TreeSpeciesType(Base):
    __tablename__ = 'tree_species_type'

    tree_species_type_id = Column(INTEGER(11), primary_key=True)
    tree_species_type_desc = Column(String(255), nullable=False)


class TreeSurround(Base):
    __tablename__ = 'tree_surround'

    tree_surround_id = Column(INTEGER(11), primary_key=True)
    tree_surround_desc = Column(String(255), nullable=False)


class TreeType(Base):
    __tablename__ = 'tree_type'

    tree_type_id = Column(INTEGER(11), primary_key=True)
    tree_type_desc = Column(String(255), nullable=False)


class TreeVigour(Base):
    __tablename__ = 'tree_vigour'

    tree_vigour_id = Column(INTEGER(11), primary_key=True)
    tree_vigour_desc = Column(String(255), nullable=False)


class UserBadgeLink(Base):
    __tablename__ = 'user_badge_link'

    user_badge_link_id = Column(INTEGER(11), primary_key=True)
    badge_id = Column(INTEGER(11), nullable=False)
    user_id = Column(INTEGER(11), nullable=False)


class Badge(Base):
    __tablename__ = 'badge'

    badge_id = Column(INTEGER(11), primary_key=True)
    badge_name = Column(String(255), nullable=False)
    badge_desc = Column(Text, nullable=False)
    image_id = Column(ForeignKey('image.image_id'), nullable=False, index=True)

    image = relationship('Image')


class ImageTagLink(Base):
    __tablename__ = 'image_tag_link'

    image_tag_link_id = Column(INTEGER(11), primary_key=True)
    image_id = Column(ForeignKey('image.image_id'), nullable=False, index=True)
    image_tag_id = Column(ForeignKey('image_tag.image_tag_id'), nullable=False, index=True)

    image = relationship('Image')
    image_tag = relationship('ImageTag')


class TreeImage(Base):
    __tablename__ = 'tree_image'

    tree_image_id = Column(INTEGER(11), primary_key=True)
    image_add_datetime = Column(DateTime, nullable=False, server_default=text("current_timestamp()"))
    image_end_datetime = Column(DateTime)
    image_approved_ind = Column(TINYINT)
    last_ai_analysis = Column(DateTime, nullable=True)
    latest_labels = Column(LONGTEXT, nullable=True)
    tree_id = Column(ForeignKey('tree.tree_id'), nullable=False, index=True)
    image_id = Column(ForeignKey('image.image_id'), nullable=False, index=True)

    image = relationship('Image')
    tree = relationship('Tree')


class TreeSpecies(Base):
    __tablename__ = 'tree_species'

    tree_species_id = Column(INTEGER(11), primary_key=True)
    tree_species_desc = Column(String(255), nullable=False)
    tree_species_type_id = Column(ForeignKey('tree_species_type.tree_species_type_id'), nullable=False, index=True)

    tree_species_type = relationship('TreeSpeciesType')


class TreeHistory(Base):
    __tablename__ = 'tree_history'

    tree_history_id = Column(INTEGER(11), primary_key=True)
    diameter_cm = Column(INTEGER(11))
    spread_radius_m = Column(INTEGER(11))
    tree_height_m = Column(INTEGER(11))
    location_x = Column(Float(9))
    location_y = Column(Float(9))
    longitude = Column(Float(9))
    latitude = Column(Float(8))
    tree_tag = Column(INTEGER(11))
    tree_change_desc = Column(String(255), nullable=True)
    tree_change_datetime = Column(TIMESTAMP, nullable=False, server_default=text("current_timestamp()"))
    is_live_change_ind = Column(TINYINT(1), nullable=False, server_default=FetchedValue())
    tree_type_id = Column(ForeignKey('tree_type.tree_type_id'), index=True)
    tree_species_id = Column(ForeignKey('tree_species.tree_species_id'), index=True)
    tree_age_group_id = Column(ForeignKey('tree_age_group.tree_age_group_id'), index=True)
    tree_surround_id = Column(ForeignKey('tree_surround.tree_surround_id'), index=True)
    tree_vigour_id = Column(ForeignKey('tree_vigour.tree_vigour_id'), index=True)
    tree_condition_id = Column(ForeignKey('tree_condition.tree_condition_id'), index=True)
    tree_data_quality_id = Column(ForeignKey('tree_data_quality.tree_data_quality_id'), index=True)
    tree_id = Column(ForeignKey('tree.tree_id'), nullable=False, index=True)
    user_id = Column(ForeignKey('user.user_id'), nullable=False, index=True)

    tree_age_group = relationship('TreeAgeGroup')
    tree_condition = relationship('TreeCondition')
    tree_data_quality = relationship('TreeDataQuality')
    tree = relationship('Tree')
    tree_species = relationship('TreeSpecies')
    tree_surround = relationship('TreeSurround')
    tree_type = relationship('TreeType')
    tree_vigour = relationship('TreeVigour')
    user = relationship('User')


class User(Base):
    __tablename__ = 'user'

    user_id = Column(INTEGER(11), primary_key=True)
    user_auth0_sub = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    nickname = Column(String(255), nullable=False)
    given_name = Column(String(255), nullable=True)
    family_name = Column(String(255), nullable=True)
    email_verified = Column(TINYINT(1), nullable=True)
    is_active = Column(TINYINT(1), nullable=False)
    noti_last_clicked = Column(TIMESTAMP, nullable=False, server_default=text("current_timestamp()"))
    user_type_id = Column(ForeignKey('user_type.user_type_id'), nullable=False, index=True)

    user_type = relationship('UserType')


class UserType(Base):
    __tablename__ = 'user_type'

    user_type_id = Column(INTEGER(11), primary_key=True)
    user_type_desc = Column(String(255), nullable=False)
