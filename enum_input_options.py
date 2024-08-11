from enum import Enum


class ValidTableOptionTables(str, Enum):
    species = 'tree_species'
    vigour = 'tree_vigour'
    surround = 'tree_surround'
    species_type = 'tree_species_type'
    data_quality = 'tree_data_quality'
    condition = 'tree_condition'
    age_group = 'tree_age_group'
