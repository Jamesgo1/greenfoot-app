from enum import Enum


class ValidTableOptionTables(str, Enum):
    species = 'tree_species'
    vigour = 'tree_vigour'
    surround = 'tree_surround'
    species_type = 'tree_species_type'
    data_quality = 'tree_data_quality'
    condition = 'tree_condition'
    age_group = 'tree_age_group'
    tree_type = 'tree_type'


class AutomatedChanges(str, Enum):
    diameter = "diameter_cm"
    spread_radius = "spread_radius_m"

class ValidTableOptionTables(str, Enum):
    species = 'tree_species'
    vigour = 'tree_vigour'
    surround = 'tree_surround'
    species_type = 'tree_species_type'
    data_quality = 'tree_data_quality'
    condition = 'tree_condition'
    age_group = 'tree_age_group'
    tree_type = 'tree_type'