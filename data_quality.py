import polars as pl
import polars.selectors as cs
from loguru import logger
from datetime import datetime
from fuzzywuzzy import process
import matplotlib.pyplot as plt


class DataInspector:

    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None

    def load_data(self):
        pl.Config(tbl_cols=-1, tbl_rows=50)
        self.df = pl.read_csv(self.file_path)
        logger.info(self.df.glimpse(return_as_string=True))

    @staticmethod
    def create_data_quality_log(log_dir="data_quality_logs", prefix=""):
        current_dt = datetime.strftime(datetime.now(), "%Y-%m-%d--%H-%M-%S")
        file_name = f"{log_dir}/{prefix}{current_dt}.log"
        logger.add(file_name)

    def non_numeric_character_check(self, col):
        filtered_df = self.df.filter(pl.col(col).str.contains(r'.*\d.*').not_())
        logger.info(f"Here are the non-numeric characters for column {col}")
        logger.info(filtered_df[[col]])

    def basic_calcs(self):
        for col in self.df.select(cs.integer() | cs.float()).columns:
            logger.info(f"Stats for column {col}:")
            stats_df = self.df.select([
                pl.max(col).alias(f"Max value {col}"),
                pl.min(col).alias(f"Min value {col}"),
                pl.median(col).alias(f"Median value {col}"),
                pl.col(col).mode().alias(f"Modal value {col}"),
                pl.mean(col).alias(f"Mean value {col}"),
            ])
            logger.info(stats_df)

    @staticmethod
    def calculate_quartile_bounds(df, col, iqr_multiple=1.5):
        q1_df = df.quantile(0.25)
        q3_df = df.quantile(0.75)

        q1 = q1_df.select(pl.col(col)).rows()[0][0]
        q3 = q3_df.select(pl.col(col)).rows()[0][0]
        logger.info(q3)
        logger.info(q1)

        iqr = (q3 - q1)
        upper_bound = q3 + iqr * iqr_multiple
        logger.info(f"{upper_bound=}")
        lower_bound = q1 - iqr * iqr_multiple
        logger.info(f"{lower_bound=}")
        return lower_bound, upper_bound

    def numeric_anomalies(self):

        for col in self.df.select(cs.integer() | cs.float()).columns:
            lower_bound, upper_bound = self.calculate_quartile_bounds(self.df, col)
            anom_df = self.df.select(pl.col(col)).filter((pl.col(col) < lower_bound) | (pl.col(col) >
                                                                                        upper_bound).sort())
            logger.info(f"Potential anomalies for column {col}:")
            logger.info(anom_df)

    def check_string_cols_values(self):
        """
        Data quality for string cols
        :return:
        """
        logger.info("Looking at the frequency of values in string columns:")
        for col in self.df.select(cs.by_dtype(pl.String)).columns:
            logger.info(self.df.group_by(col).len().sort(by="len", descending=True))

    def check_similar_strings(self, rarity_score=500, similarity_score=90):
        """
        :param rarity_score: How rarely the data occurs for it to be checked - i.e. it needs to occur at least as
        infrequently as once in every _rarity_score_ rows.
        :param similarity_score: How similar another string in the column needs to be in order to be flagged

        :return:
        """
        for col in self.df.select(cs.by_dtype(pl.String)).columns:
            grouped_df = self.df.group_by(col).len().sort(by=col)
            potential_typos_df = grouped_df.filter(pl.col("len") < (self.df.shape[0] / rarity_score))
            possible_matches = [i[0].lower() for i in grouped_df.rows()]
            anomalies_list = [i[0].lower() for i in potential_typos_df.rows()]
            anomalies_list = [i for i in anomalies_list if not i.isnumeric()]
            logger.info(f"Potential typos for column {col}:")
            logger.info(anomalies_list)
            for anom in anomalies_list:
                choices = [i for i in possible_matches if i != anom]
                best_match, score = process.extractOne(anom, choices)
                logger.trace(f"{anom=}: {best_match=}, {score=}")
                if score > similarity_score:
                    logger.warning(f"Potential typo in column {col}: {anom} is {score}% similar to {best_match}")

    def check_for_negative_values_int_cols(self):
        for col in self.df.select(cs.by_dtype(pl.Int64)).columns:
            neg_df = self.df.select(pl.col(col)).filter(pl.col(col) < 0)
            logger.info("Here are the negative values ")
            logger.info(neg_df.group_by(col).len().sort(by="len", descending=True))
            logger.info(f"Number of negative values is in column {col} is {neg_df.shape[0]}")

    def visualise_string_data(self):
        for col in self.df.select(cs.by_dtype(pl.String)).columns:
            grouped_df = self.df.group_by(col).len().sort(by=col)
            print(grouped_df)
            pd_df = grouped_df.to_pandas()
            pd_df.plot.bar(x=col, y="len")
            plt.xticks(rotation=45)
            plt.title(f"Count by type of {col}")
            plt.show()

    def visualise_numeric_data(self):
        for col in self.df.select(cs.by_dtype(pl.Int64)).columns:
            col_df = self.df.select(pl.col(col))
            pd_df = col_df.to_pandas()
            pd_df.plot.hist(bins=5)
            plt.show()

    def visualise_boxplots_integers(self):
        int_dfs = self.df.select(cs.by_dtype(pl.Int64))
        pd_df = int_dfs.to_pandas()
        pd_df.boxplot()
        plt.show()


class DataCleanser:

    def __init__(self, df):
        self.df = df

    def rename_columns(self):
        self.df = self.df.rename(lambda column_name: column_name.lower()[:64])
        logger.info(self.df.glimpse(return_as_string=True))

    def convert_string_to_integer(self, col):
        self.df = self.df.with_columns(pl.col(col).cast(pl.Int64, strict=False))
        logger.info(self.df.glimpse(return_as_string=True))

    def replace_substring(self, substring_to_remove, col, replacement=""):
        self.df = self.df.with_columns(pl.col(col)
                                       .str.replace_all(substring_to_remove, replacement)
                                       .str.replace_all(r"\s\s+", "")
                                       )
        logger.info(self.df.glimpse(return_as_string=True))

    def reverse_negative_to_positive(self, col):
        self.df = self.df.with_columns(
            pl.when(pl.col(col) < 0).then(pl.col(col) * -1).otherwise(pl.col(col))
        )
        logger.info(self.df.glimpse(return_as_string=True))

    def trim_whitespace_all_string_cols(self):
        for col in self.df.select(cs.by_dtype(pl.String)).columns:
            self.df = self.df.with_columns(pl.col(col).str.strip().str.replace_all(r"\s\s+", ""))
        logger.info(self.df.glimpse(return_as_string=True))

    def title_case_string_cols(self):
        for col in self.df.select(cs.by_dtype(pl.String)).columns:
            self.df = self.df.with_columns(pl.col(col).str.to_titlecase())
        logger.info(self.df.glimpse(return_as_string=True))

    def drop_column(self, col):
        self.df = self.df.drop(col)
        logger.info(self.df.glimpse(return_as_string=True))

    def convert_to_null_string_cols(self):
        self.df = self.df.with_columns([
            pl.when(pl.col(pl.String).is_in(["", "N/a"]))
            .then(pl.lit("Unknown"))
            .otherwise(pl.col(pl.String))
            .name.keep()
        ])
        logger.info(self.df.glimpse(return_as_string=True))

    def rename_db_cols(self):
        rename_dict = {
            "typeoftree": "tree_type",
            "speciestype": "tree_species_type",
            "species": "tree_species",
            "age": "tree_age_group",
            "treesurround": "tree_surround",
            "vigour": "tree_vigour",
            "condition": "tree_condition",
            "diameterincentimetres": "diameter_cm",
            "spreadradiusinmetres": "spread_radius_m",
            "treelocationx": "location_x",
            "treelocationy": "location_y",
            "treetag": "tree_tag",
            "treeheightinmetres": "tree_height_m",
            "dataquality": "tree_data_quality"
        }
        self.df = self.df.rename(rename_dict)
        self.df.glimpse()


class DataQualityScorer:
    measurement_cols = ["DIAMETERinCENTIMETRES", "SPREADRADIUSinMETRES", "TREEHEIGHTinMETRES"]
    dq_column_name = "dataquality"

    def __init__(self, df):
        self.df = df

    def score_1_default(self):
        """
        Adds a column with a default ID of good data quality to the dataframe.
        :return:
        """
        self.df = self.df.with_columns(pl.lit("good").alias(self.dq_column_name))
        logger.info(self.df.glimpse(return_as_string=True))

    def score_2_null_in_row(self):
        """
        Adjusting the data quality score for missing data.
        :return:
        """
        null_expressions = ["", "N/A"]
        string_cols = self.df.select(cs.by_dtype(pl.String)).columns
        for string_col in string_cols:
            self.df = self.df.with_columns(
                dataquality=pl.when(pl.col(string_col).is_in(null_expressions))
                .then(pl.lit("ok"))
                .otherwise(pl.col(self.dq_column_name))
            )

    def score_2_zero_measurement(self):
        for m_col in self.measurement_cols:
            self.df = self.df.with_columns(
                dataquality=pl.when(pl.col(m_col) == 0)
                .then(pl.lit("ok"))
                .otherwise(pl.col(self.dq_column_name))
            )

    def score_3_negative_value(self):
        for m_col in self.measurement_cols:
            self.df = self.df.with_columns(
                dataquality=pl.when(pl.col(m_col) < 0)
                .then(pl.lit("poor"))
                .otherwise(pl.col(self.dq_column_name))
            )
        logger.info(self.df.filter(pl.col(self.dq_column_name) == "poor").glimpse(return_as_string=True))

    def score_3_extreme_anomalies(self):
        logger.info(self.dq_column_name)
        for m_col in self.measurement_cols:
            lower_bound, upper_bound = DataInspector.calculate_quartile_bounds(self.df, m_col, iqr_multiple=10)
            logger.info(f"For column {m_col}: {lower_bound=}, {upper_bound=}")
            self.df = self.df.with_columns(
                dataquality=pl.when((pl.col(m_col) < lower_bound) | (pl.col(m_col) > upper_bound))
                .then(pl.lit("poor"))
                .otherwise(pl.col(self.dq_column_name))
            )

    def run_all_data_quality(self):
        self.score_1_default()

        self.score_2_null_in_row()
        self.score_2_zero_measurement()
        logger.info(self.df.filter(pl.col(self.dq_column_name) == "ok").glimpse(return_as_string=True))

        self.score_3_negative_value()
        logger.info(self.df.filter(pl.col(self.dq_column_name) == "poor").glimpse(return_as_string=True))

        self.score_3_extreme_anomalies()
        logger.info(self.df.filter(pl.col(self.dq_column_name) == "poor")
                    .sort(self.measurement_cols[-1], descending=True)
                    .glimpse(return_as_string=True))


class DataTest:

    def __init__(self, df):
        self.df = df

    @staticmethod
    def show_output(test_df, col):
        rows_returned = test_df.shape[0]
        if rows_returned == 0:
            logger.info(f"No '{test_df.columns[0]}' values found in column {col}")
        else:
            logger.error(f"{rows_returned} '{test_df.columns[0]}' values found in column {col}")
            logger.error(test_df)

    def alpha_chars_present(self, col):
        alpha_df = self.df.select((pl.col(col)).filter(pl.col(col).str.contains(r"[a-zA-Z]").not_()).alias("non_alpha"))
        self.show_output(alpha_df, col)

    def ensure_within_range(self, col, lower_bound, upper_bound):
        invalid_vals = self.df.select((pl.col(col))
                                      .filter((pl.col(col) > upper_bound) | (pl.col(col) < lower_bound))
                                      .alias(f"outside_valid_{col}"))

        return invalid_vals

    def valid_lat_and_long(self):
        invalid_latitude = self.ensure_within_range("latitude", -90, 90)
        self.show_output(invalid_latitude, "latitude")

        invalid_long = self.ensure_within_range("longitude", -180, 180)
        self.show_output(invalid_long, "longitude")


class RelationalDataFrameBuilder:
    type_table_list = ["tree_type",
                       "tree_species",
                       "tree_age_group",
                       "tree_surround",
                       "tree_vigour",
                       "tree_condition",
                       "tree_data_quality"]

    def __init__(self, cleansed_df):
        self.df = cleansed_df

        self.type_tables_dict = {}
        self.final_tables_dict = {}

    def create_tree_species_dfs(self):
        # Get the species type table
        species_unique_df = self.type_tables_dict["tree_species"]

        # Clone the desc column so that values can be replaced with IDs
        species_unique_df = species_unique_df.with_columns(pl.col("tree_species").alias("tree_species_type_id"))
        species_unique_df.glimpse()

        # Create species_type type table
        species_type_unique_df = (self.df.select(pl.col("tree_species_type"))
                                  .unique().sort(by="tree_species_type").with_row_index(offset=1))

        # Create dict for species_type
        species_type_desc_to_id = {i[1]: i[0] for i in species_type_unique_df.rows()}

        # Replace cloned desc column with species_type_id
        species_to_species_type_list = self.df.select(pl.col(["tree_species", "tree_species_type"])).unique().rows()
        species_unique_df.select(pl.col("tree_species_type_id")).glimpse()
        for item in sorted(species_to_species_type_list):
            species_unique_df = (species_unique_df.
                                 with_columns(pl.col("tree_species_type_id")
                                              .str.replace(fr"^{item[0]}$", species_type_desc_to_id[item[1]])))

        # Convert ID column to integer
        species_unique_df = species_unique_df.with_columns(pl.col("tree_species_type_id").cast(pl.Int64, strict=False))
        logger.info("species df:")
        logger.info(species_unique_df.glimpse(return_as_string=True))
        logger.info("species type df:")
        logger.info(species_type_unique_df.glimpse(return_as_string=True))

        self.type_tables_dict["tree_species"] = species_unique_df
        self.final_tables_dict["tree_species_type"] = species_type_unique_df

        # Quick test to ensure types match
        # test_items = ["Prunus Cerasifera Nigra", "Tilla Cordata", "Prunus"]
        # self.test_type_table("tree_species",
        #                      "tree_species_type",
        #                      species_unique_df,
        #                      species_type_unique_df,
        #                      *test_items)

    def create_type_tables_dict(self):
        for col in self.type_table_list:
            type_table_df = self.df.select(pl.col(col)).unique().sort(pl.col(col)).with_row_index(offset=1)
            self.type_tables_dict[col] = type_table_df

    def convert_type_cols_to_ids(self, df_with_index):
        rename_dict = {}

        for col, df in self.type_tables_dict.items():
            values_list = df.rows()
            for values_tuple in values_list:
                values_list = values_tuple[:2]
                col_id, desc = values_list
                df_with_index = df_with_index.with_columns(pl.col(col).str.replace(fr"^{desc}$", col_id))

            df_with_index = df_with_index.with_columns(pl.col(col).cast(pl.Int64, strict=False))
            rename_dict[col] = f"{col}_id"
        df_with_index = df_with_index.rename(rename_dict)
        df_with_index.glimpse()
        return df_with_index

    def create_main_tree_table_df(self):
        # Add index to main df
        df_with_index = self.df.with_row_index(offset=1)
        df_with_index = df_with_index.rename({"index": "tree_id"})

        # Drop col not in main table
        df_with_index = df_with_index.drop("tree_species_type")

        # Replace type desc with type_ids
        df_with_index = self.convert_type_cols_to_ids(df_with_index)
        self.final_tables_dict["tree"] = df_with_index

    def create_all_tables(self):
        self.create_type_tables_dict()
        self.create_tree_species_dfs()
        self.create_main_tree_table_df()

        self.final_tables_dict = {**self.final_tables_dict, **self.type_tables_dict}

        logger.info("Final tables:")
        for table_name, df in self.final_tables_dict.items():
            logger.info(table_name)
            logger.info(df.glimpse(return_as_string=True))
        return self.final_tables_dict


class RelationalDBScriptGenerator:
    db_name = "greenfoot"

    type_table_list = RelationalDataFrameBuilder.type_table_list

    def __init__(self, final_tables_dict):
        """
        This class creates a script that when run will create a relational database of the data.
        :param df:
        """
        self.tables_dict = final_tables_dict

        script_start = "-- " + "-" * 100
        script_comment = f"-- Building database {self.db_name}"
        self.sql_script_list = [script_start, script_comment, "START TRANSACTION;"]

    def generate_type_table_script(self, table_name, df, has_fk=False):

        data_list = df.rows()

        fk_col_name, fk_insert, fk_vals = "", "", ""
        if has_fk:
            fk_col_name = f",\n`{table_name}_type_id` int(11) NOT NULL"
            fk_insert = f", `{table_name + '_type_id'}`"

        create_table_sql = f"""
        CREATE TABLE `{table_name}` (
        `{table_name + "_id"}` int(11) NOT NULL,
        `{table_name + "_desc"}` varchar(255) NOT NULL {fk_col_name}
        );
        """

        insert_data = f"""
        INSERT INTO `{table_name}` (`{table_name + "_id"}`, `{table_name + "_desc"}`{fk_insert}) VALUES
        """
        values_sql = [f"({i[0]}, '{i[1]}')," for i in data_list]
        if has_fk:
            values_sql = [f"({i[0]}, '{i[1]}', {i[2]})," for i in data_list]
        joined_values = "\n".join(values_sql)

        insert_stmt = "\n".join([insert_data, joined_values])
        print("=" * 100)
        insert_stmt = insert_stmt[:-1] + ";"
        full_table_stmt = create_table_sql + "\n" + insert_stmt
        self.sql_script_list.append(full_table_stmt)
        logger.info("\n\n".join(self.sql_script_list))

    def generate_all_type_table_script(self):
        all_type_tables = self.type_table_list.copy()
        all_type_tables.append("tree_species_type")
        logger.info(all_type_tables)
        logger.info(self.type_table_list)

        for table in all_type_tables:
            df = self.tables_dict[table]
            fk = False
            if table == "tree_species":
                fk = True
            self.generate_type_table_script(table, df, has_fk=fk)

    @staticmethod
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def write_main_tree_table_script(self):
        main_table_sql_list = []
        table_name = "tree"
        df = self.tables_dict[table_name]

        # Get columns and datatypes
        main_table_df = df.select(["diameter_cm", "spread_radius_m", "tree_height_m", "location_x",
                                   "location_y", "longitude", "latitude", "tree_tag"])
        cols_list = ["tree_id"]
        cols_list.extend(main_table_df.columns)
        cols_list.extend([i + "_id" for i in self.type_table_list])
        cols_list = [(i, "int(11)") for i in cols_list]
        cols_list = [(i[0], "float(8, 6)") if i[0] == "latitude" else i for i in cols_list]
        cols_list = [(i[0], "float(9, 6)") if i[0] == "longitude" else i for i in cols_list]
        cols_list = [(i[0], "float(9, 2)") if "location" in i[0] else i for i in cols_list]

        # Create table statement
        create_table_list = [f"CREATE TABLE `{table_name}` ("]
        sql_col_name_list = []
        for col in cols_list:
            col_name, type = col
            sql_col_name_list.append(col_name)
            insert_stmt = f"`{col_name}` {type}"
            if col_name == "tree_id":
                insert_stmt += " NOT NULL"
            insert_stmt += ","
            create_table_list.append(insert_stmt)
        create_table_sql = "\n".join(create_table_list)
        create_table_sql = create_table_sql[:-1] + "\n);"
        main_table_sql_list.append(create_table_sql)

        # Replace with key values
        chunked_list = list(self.chunks(df.rows(), 500))
        for chunked_rows in chunked_list:
            # Insert values
            insert_vals_list = [f"INSERT INTO `{table_name}` ("]
            for col_name in df.columns:
                insert_vals_list.append(f"`{col_name}`,")
            insert_vals_list[-1] = insert_vals_list[-1].replace(",", "")
            insert_vals_list.append(") VALUES")
            for row in chunked_rows:
                row_str = (str(row) + ",").replace(", None", ", NULL")
                insert_vals_list.append(row_str)
            insert_sql = "\n".join(insert_vals_list)[:-1] + ";"
            main_table_sql_list.append(insert_sql)

        # Joining query
        main_sql_str = "\n\n".join(main_table_sql_list)
        self.sql_script_list.append(main_sql_str)

    def test_type_table(self, orig_val_col, type_val_col, link_table_df, type_table_df, *test_values):
        for orig_val in test_values:
            logger.info(f"Now testing {orig_val_col}'s value in {type_val_col}")

            orig_type_val_tuple = (self.df.select([orig_val_col, type_val_col])
            .filter(pl.col(orig_val_col) == orig_val).rows()[0])
            orig_df_val, orig_df_type_desc = orig_type_val_tuple
            logger.info(
                f"The test value '{orig_df_val}' corresponds to the type desc '{orig_df_type_desc}' in the original df"
            )

            type_tuple = (type_table_df.filter(pl.col(type_val_col) == orig_df_type_desc)
            .rows()[0]
            )
            type_df_id, type_df_desc = type_tuple
            logger.info(
                f"The type desc '{type_df_desc}' corresponds to the type_id '{type_df_id}' in the type table"
            )

            link_table_tuple = link_table_df.filter(pl.col(orig_val_col) == orig_val).rows()[0]
            _, link_df_val_desc, link_df_type_id = link_table_tuple
            logger.info(
                f"The test value {link_df_val_desc} corresponds to the type_id '{link_df_type_id}' in the link table"
            )

            assert (orig_df_val == link_df_val_desc)
            assert (type_df_id == link_df_type_id)
            assert (orig_df_type_desc == type_df_desc)
            logger.info("-" * 100)

    def commit_transaction(self):
        self.sql_script_list.append("COMMIT;")

    def combine_and_log_final_sql(self):
        DataInspector.create_data_quality_log(log_dir="data_exploration/sql_output", prefix="sql")
        sep = "-- " + "-" * 100
        sql_output = f"\n\n{sep}\n\n".join(self.sql_script_list)
        logger.info(sql_output)

    def generate_full_sql_script_for_import(self):
        self.generate_all_type_table_script()
        self.write_main_tree_table_script()
        self.commit_transaction()
        self.combine_and_log_final_sql()


def explore_data(df=None):
    """
    A way to get an overview of the open tree data and examine any data quality issues.
    :return:
    """
    # Set up
    data_explore = DataInspector("data_exploration/odTrees.csv")
    if df is not None:
        data_explore.df = df
    else:
        data_explore.load_data()
        data_explore.create_data_quality_log()

    data_explore.numeric_anomalies()

    # visualisation
    data_explore.visualise_string_data()
    data_explore.visualise_numeric_data()
    data_explore.visualise_boxplots_integers()

    # String exploration
    data_explore.check_string_cols_values()
    data_explore.check_similar_strings()

    # Numeric exploration
    data_explore.check_for_negative_values_int_cols()


def cleanse_data(df=None):
    """
    Making changes to the dataset that make the data clearer and removes errors.
    :return:
    """
    # Set up
    if df is None:
        data_inspector = DataInspector("data_exploration/odTrees.csv")
        data_inspector.load_data()
        data_inspector.create_data_quality_log()
        df = data_inspector.df
    df.glimpse()
    # Add data quality score
    dq = DataQualityScorer(df)
    dq.run_all_data_quality()

    data_cleanser = DataCleanser(dq.df)

    # Rename columns
    data_cleanser.rename_columns()

    # Modifying specific columns
    data_cleanser.convert_string_to_integer("treetag")

    # Cleaning string cols
    data_cleanser.replace_substring("(type)", "species")
    data_cleanser.replace_substring(r"\(", "species")
    data_cleanser.replace_substring(r"\)", "species")
    data_cleanser.replace_substring("'", "species")
    data_cleanser.replace_substring("-", "age", replacement=" ")
    data_cleanser.replace_substring("Tree$", "typeoftree")
    data_cleanser.replace_substring(r"^Not Known$", "speciestype", replacement="Unknown")
    data_cleanser.title_case_string_cols()
    data_cleanser.trim_whitespace_all_string_cols()

    # Changing negatives to positives - consider why and what?
    data_cleanser.reverse_negative_to_positive("spreadradiusinmetres")
    data_cleanser.reverse_negative_to_positive("diameterincentimetres")

    # Remove description column
    data_cleanser.drop_column("description")

    data_cleanser.convert_to_null_string_cols()

    data_cleanser.rename_db_cols()

    return data_cleanser.df


def test_data(df):
    data_test = DataTest(df)

    # Throws error if numeric string is found
    for col in df.select(cs.by_dtype(pl.String)).columns:
        data_test.alpha_chars_present(col)

    data_test.valid_lat_and_long()


explore_data()
quit()
trees_df = modify_data()
# db_gen = RelationalDBScriptGenerator(trees_df)
# db_gen.generate_full_sql_script_for_import()
df_build = RelationalDataFrameBuilder(trees_df)
df_dict = df_build.create_all_tables()
tree_df = df_dict["tree"]
logger.info(tree_df.select(pl.max("tree_height_m")))
quit()
table_list = sorted([k for k in df_dict.keys()])
logger.info(table_list)
logger.info(len(table_list))
df_gen = RelationalDBScriptGenerator(df_dict)
df_gen.generate_full_sql_script_for_import()
quit()
# test_data(trees_df)

# Options for dealing with data issues
# 1) List of questions about what people want out from the data
# 2) Entity relationship diagram
# 3) Project plan

# Next steps:
# 2) Create GH project
# 3) Write project plan
# 4) Begin notes on data decisions taken so far
