import sqlite3
import traceback
import re
import time
import csv
import sys
import json
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_datetime
from qualys_etl.etld_lib import etld_lib_config
global count_rows_added_to_table


class SqliteObj:
    def __init__(self, sqlite_file, read_only=False):
        self.sqlite_file = str(sqlite_file)
        self.read_only = read_only
        self.connection = None
        self.cursor = None
        self.isolation_level = None
        self.count_rows_added_to_table = 0
        self.status_table_recreated = False
        self.pcrs_postureinfo_policy_control_technlogy_dict = {}
        self.open_connection_and_cursor(read_only=read_only)
        self.pragma_set = False

    def get_pragma(self, cursor, table_name):
        # pragma[0]['name'] - field 0 name 'field name in table'
        # pragma[0]['type'] - field 0 type 'INTEGER'
        sqlPragma = f'PRAGMA table_info({table_name})'
        try:
            cursor.execute(sqlPragma)
            result = cursor.fetchall()
        except sqlite3.DatabaseError as e:
            raise Exception(f"Exception: {e} - Could not obtain pragma for table: {table_name}.")
        return result

    def get_all_table_names_from_database(self) -> list:
        database_table_names = []
        try:
            self.cursor.execute("select tbl_name from sqlite_master where type == 'table'")
            for create_table_list in self.cursor.fetchall():
                create_table_statement = str(create_table_list[0])
                database_table_names.append(create_table_statement)
        except sqlite3.DatabaseError as e:
            raise Exception(f"Exception: {e} - Could not obtain table names for {self.sqlite_file}.")
        return database_table_names

    # def get_create_table_statement_from_database(self, table_name) -> str:
    #     create_table_statement = ""
    #     try:
    #         select_statement = "select sql from sqlite_master " \
    #                            "where type == 'table' and " \
    #                            f"tbl_name == '{table_name}'"
    #         self.cursor.execute(select_statement)
    #         create_table_statement = self.cursor.fetchone()
    #         create_table_statement = str(create_table_statement[0])
    #     except sqlite3.DatabaseError as e:
    #         raise Exception(f"Exception: {e} - Could not obtain table names for {self.sqlite_file}.")
    #     return create_table_statement

    def reopen_connection_and_cursor_as_sqlite3_row_factory(self):
        try:
           self.close_connection()
        except Exception as e:
            pass # Ignore errors

        try:
            self.connection = sqlite3.connect(database=self.sqlite_file, timeout=300)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            self.log_pragma_settings(message="DEFAULT FOR reopen_connection_and_cursor_as_sqlite3_row_factory")
            self.optimize_database_performance()
            self.log_pragma_settings(message="UPDATED FOR reopen_connection_and_cursor_as_sqlite3_row_factory")
        except Exception as e:
            etld_lib_functions.logger.error(f"Error getting row factory connnection cursor obj: {self.sqlite_file}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    def open_connection_and_cursor(self, read_only=False, open_cursor=True, enable_row_factory=True):
        try:
            if read_only is True and Path(self.sqlite_file).exists:
                self.connection = sqlite3.connect(f'file:{str(self.sqlite_file)}?mode=ro', uri=True, timeout=300)
            else:
                if Path(self.sqlite_file).exists():
                    self.connection = sqlite3.connect(database=self.sqlite_file, timeout=300)
                else:
                    self.connection = sqlite3.connect(database=self.sqlite_file, timeout=300)
                    self.initialize_database_pragma_page_size() # 2025-04-07 pragma page_size can only be added on new databasse.
            if enable_row_factory is True:
                self.connection.row_factory = sqlite3.Row
            if open_cursor is True:
                self.cursor = self.connection.cursor()

        except Exception as e:
            etld_lib_functions.logger.error(f"Error getting cursor obj: {self.sqlite_file}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

        if read_only is False:
            self.log_pragma_settings("DEFAULT FOR open_connection_and_cursor")
            self.optimize_database_performance()
            self.log_pragma_settings(message="UPDATED FOR open_connection_and_cursor")

    def optimize_database_performance(self):
        """
        Optimize database settings for large datasets and operations.
        Uses the database connection provided during class initialization.
        """
        cursor = self.cursor

        try:
            # Adjust cache size (in pages). Example: 80,000 pages -80000
            cursor.execute(f"PRAGMA cache_size = {etld_lib_config.sqlite_pragma_cache_size};")

            # Change journal mode to Write-Ahead Logging for better concurrency
            cursor.execute(f"PRAGMA journal_mode = {etld_lib_config.sqlite_pragma_journal};")

            # Set synchronous to NORMAL (1) for a balance between performance and durability
            cursor.execute(f"PRAGMA synchronous = {etld_lib_config.sqlite_pragma_synchronous};")

            # Use memory for temporary storage to speed up operations requiring temp tables or indices
            cursor.execute(f"PRAGMA temp_store = {etld_lib_config.sqlite_pragma_temp_store};")

            # Keep auto_vacuum as NONE during bulk operations for performance
            cursor.execute("PRAGMA auto_vacuum = NONE;")

            # Optionally, execute ANALYZE to update statistics for the query planner
            # cursor.execute("ANALYZE;")
        except sqlite3.DatabaseError as e:
            # Handle the database error, e.g., log it or print an error message
            etld_lib_functions.logger.warning(f"Database error occurred setting pragmas: {e}")
        except Exception as e:
            # Handle other possible exceptions
            etld_lib_functions.logger.warning(f"Unexpected error occurred setting pragmas: {e}")

    def log_pragma_settings(self, message="DEFAULT"):
        """
        Logs the current PRAGMA settings using the etld_lib_functions.logger, with descriptive names.
        """
        pragma_settings = [
            "cache_size",
            "journal_mode",
            "synchronous",
            "temp_store",
            "auto_vacuum"
        ]

        # Maps for converting PRAGMA values to descriptive names
        synchronous_names = {
            0: "OFF",
            1: "NORMAL",
            2: "FULL"
        }
        temp_store_names = {
            0: "DEFAULT",
            1: "FILE",
            2: "MEMORY"
        }
        auto_vacuum_names = {
            0: "NONE",
            1: "FULL",
            2: "INCREMENTAL"
        }

        cursor = self.cursor
        try:
            pragma_dict = {}
            for setting in pragma_settings:
                cursor.execute(f"PRAGMA {setting};")
                value = cursor.fetchone()
                if value:
                    value_str = str(value[0])
                    # Convert specific PRAGMA values to descriptive names
                    if setting == "synchronous":
                        value_str = synchronous_names.get(value[0], value_str)
                    elif setting == "temp_store":
                        value_str = temp_store_names.get(value[0], value_str)
                    elif setting == "auto_vacuum":
                        value_str = auto_vacuum_names.get(value[0], value_str)
                    if setting == "cache_size":
                        memory_usage = self.calculate_cache_memory_usage(abs(int(value[0])))
                        value_str += f" (Approx. {memory_usage:.2f} MB used by cache)"
                    pragma_dict[setting] = value_str
                else:
                    etld_lib_functions.logger.info(f"Failed to fetch PRAGMA {setting}")
            etld_lib_functions.logger.info(f"{message} PRAGMA {Path(self.sqlite_file).name} - {pragma_dict}")

        except sqlite3.DatabaseError as e:
            etld_lib_functions.logger.warning(f"Database error occurred while fetching PRAGMA settings: {e}")
        except Exception as e:
            etld_lib_functions.logger.warning(f"An unexpected error occurred while fetching PRAGMA settings: {e}")

    def calculate_cache_memory_usage(self, cache_size):
        """
        Calculates the memory used by the cache based on the cache size in pages.

        :param cache_size: The cache size in pages.
        :return: Memory usage in megabytes.
        """
        page_size_bytes = 4096  # Default page size in SQLite is 4096 bytes
        memory_usage_bytes = cache_size * page_size_bytes
        memory_usage_megabytes = memory_usage_bytes / (1024 * 1024)
        return memory_usage_megabytes


    def attach_database_to_connection(self, database_as_name, database_sqlite_file: str, mode='ro'):
        attach_database_sql = f'ATTACH DATABASE ? AS {database_as_name}'
        # unsupported on redhat 8.4 self.connection.execute(attach_database_sql, (f'file:{str(database_sqlite_file)}?mode={mode}',))
        try:
            etld_lib_functions.logger.info(f"{attach_database_sql}, ({database_sqlite_file})")
            self.connection.execute(attach_database_sql, (str(database_sqlite_file),))
        except sqlite3.Error as err:
            etld_lib_functions.logger.error(f"sqlite3.Error attaching database: {self.sqlite_file}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {err}")
            exit(1)
        except Exception as e:
            etld_lib_functions.logger.error(f"Error attaching database: {self.sqlite_file}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    def detach_database_to_connection(self, database_as_name, database_sqlite_file: str, mode='ro'):
        detach_database_sql = f'DETACH DATABASE {database_as_name}'
        # unsupported on redhat 8.4 self.connection.execute(attach_database_sql, (f'file:{str(database_sqlite_file)}?mode={mode}',))
        try:
            self.connection.execute(detach_database_sql,)
        except sqlite3.Error as err:
            etld_lib_functions.logger.error(f"sqlite3.Error detaching database {database_as_name} from {self.sqlite_file}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {err}")
            exit(1)
        except Exception as e:
            etld_lib_functions.logger.error(f"Error outside of sqlite3 detaching database {database_as_name}, {self.sqlite_file}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    # def get_table_columns(self, table_name) -> list:
    #     try:
    #         sql = f"select * from {table_name} where 1=0;"
    #         self.cursor.execute(sql)
    #         return [d[0] for d in self.cursor.description]
    #     except Exception as e:
    #         etld_lib_functions.logger.info(f"Table not found: {table_name}")
    #         etld_lib_functions.logger.info(f"Exception: {e}")
    #         return []

    def get_table_columns(self, table_name) -> list:
        max_attempts = 30
        attempt = 0
        sleep_time = 60
        success_flag = False
        while attempt < max_attempts:
            try:
                sql = f"SELECT * FROM {table_name} WHERE 1=0;"
                self.cursor.execute(sql)
                etld_lib_functions.logger.info(f"success get_table_columns for {table_name}")
                success_flag = True
                return [d[0] for d in self.cursor.description]
            except sqlite3.OperationalError as e:
                etld_lib_functions.logger.info(f"Operational error Retrying {table_name}. Attempt {attempt + 1}/{max_attempts}")
                etld_lib_functions.logger.info(f"Exception: {e}")
            except sqlite3.Error as e:  # Catch other sqlite3 errors
                etld_lib_functions.logger.info(f"SQLite error Retrying {table_name}. Attempt {attempt + 1}/{max_attempts}")
                etld_lib_functions.logger.info(f"Exception: {e}")
            except Exception as e:  # Catch any other exceptions
                etld_lib_functions.logger.info(f"Unexpected error Retrying {table_name}. Attempt {attempt + 1}/{max_attempts}")
                etld_lib_functions.logger.info(f"Exception: {e}")
            if not success_flag:
                attempt += 1
                time.sleep(sleep_time)
                continue

        if not success_flag:
            etld_lib_functions.logger.error(
                f"Failed to access table {table_name} after {max_attempts} attempts.")
            exit(1)
        else:
            return []

    def get_min_max_dates_from_table_column(self, table_name, column_name):
        select_statement = f'select min({column_name}) MIN_DATE, ' \
                           f'max({column_name}) MAX_DATE ' \
                           f'from {table_name};'
        self.cursor.execute(select_statement)
        records = self.cursor.fetchall()
        min_date=""
        max_date=""
        if len(records) == 1:
            min_date = records[0][0]
            max_date = records[0][1]
        return {'min_date': min_date, 'max_date': max_date}

    def get_distinct_batch_numbers_from_table_column(self, table_name, column_name='BATCH_NUMBER') -> list:
        select_statement = f'select distinct({column_name}) ' \
                           f'from {table_name};'
        self.cursor.execute(select_statement)
        records = self.cursor.fetchall()
        record_list = []
        for record in records:
            record_list.append(record)

        return record_list

    def select_rows_from_status_table(self, table_name):
        select_statement = f'select * from {table_name} limit 100;'
        self.cursor.execute(select_statement)
        records = self.cursor.fetchall()
        return records

    def execute_statement(self, statement):
        self.cursor.execute(f"{statement};")


    # def create_table(self,
    #                  table_name=None, csv_columns=[],
    #                  key=False, csv_column_types={}):
    #     try:
    #         if key is False:
    #             table_statement = self.create_table_statement_no_primary_key(table_name, csv_columns)
    #         else:
    #             table_statement = self.create_table_statement(key, table_name, csv_columns, csv_column_types)
    #
    #         self.cursor.execute(table_statement)
    #         table_statement_one_line = table_statement.replace("\n", " ")
    #         etld_lib_functions.logger.info(f"sqlite create table statement: {table_statement_one_line}")
    #         self.connection.commit()
    #     except Exception as e:
    #         etld_lib_functions.logger.error(f"Error creating table: {table_name}, please retry after fixing error")
    #         etld_lib_functions.logger.error(f"Exception: {e}")
    #         exit(1)

    def initialize_database_pragma_page_size(self, page_size="4096"):
        page_size_before = self.connection.execute(f"PRAGMA page_size;").fetchone()[0]
        self.connection.execute(f"PRAGMA page_size = {page_size};")
        page_size_after = self.connection.execute(f"PRAGMA page_size;").fetchone()[0]
        etld_lib_functions.logger.info(f"PRAGMA page_size before: {page_size_before}, page_size after: {page_size_after}: sqlite file: {self.sqlite_file}")

    def drop_and_recreate_table(self, table_name: str, csv_columns: list, csv_column_types: dict, key=False):
        try:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            if key is False:
                table_statement = \
                    self.create_table_statement_no_primary_key_and_column_types(
                        table_name=table_name,
                        csv_columns=csv_columns,
                        csv_column_types=csv_column_types)
            else:
                table_statement = self.create_table_statement(
                    primary_key=key,
                    table_name=table_name,
                    csv_columns=csv_columns,
                    csv_column_types=csv_column_types)

            self.cursor.execute(table_statement)
            table_statement_one_line = table_statement.replace("\n", " ")
            etld_lib_functions.logger.info(f"sqlite create table statement: {table_statement_one_line}")
            self.connection.commit()
        except Exception as e:
            etld_lib_functions.logger.error(f"Error creating table: {table_name}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    @staticmethod
    def create_table_statement(primary_key, table_name, csv_columns, csv_column_types={}):
        table_statement = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        primary_keys = ""
        if isinstance(primary_key, list):
            pass
        elif primary_key in csv_column_types.keys():
            table_statement = f"{table_statement}{primary_key} {csv_column_types[primary_key]} PRIMARY KEY NOT NULL,\n"
        else:
            table_statement = f"{table_statement}{primary_key} CHAR PRIMARY KEY NOT NULL,\n"

        for column in csv_columns:
            if isinstance(primary_key, list) or primary_key != column:
                if column in csv_column_types.keys():
                    column_type = csv_column_types[column]
                    table_statement = f"{table_statement}{column} {column_type},\n"
                else:
                    table_statement = f"{table_statement}{column} TEXT,\n"

        # table_statement = f"{table_statement}Row_Last_Updated TEXT,\n"

        table_statement = re.sub(",\n$", "", table_statement)

        if isinstance(primary_key, list):
            primary_keys = ", ".join(primary_key)
            table_statement = f"{table_statement},\nPRIMARY KEY ({primary_keys})\n"

        table_statement = table_statement + ");"
        return table_statement

    @staticmethod
    def create_table_statement_no_primary_key_and_column_types(table_name: str, csv_columns: list, csv_column_types: dict):
        table_statement = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        for column in csv_columns:
            if column in csv_column_types.keys():
                column_type = csv_column_types[column]
                table_statement = f"{table_statement}{column} {column_type},\n"
            else:
                table_statement = f"{table_statement}{column} TEXT,\n"

        # table_statement = f"{table_statement}Row_Last_Updated TEXT,\n"

        table_statement = re.sub(",\n$", "", table_statement)

        table_statement = table_statement + ");"
        return table_statement

    # @staticmethod
    # def create_table_statement_no_primary_key(table_name, csv_columns):
    #     table_statement_list = []
    #     table_statement_list.append(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
    #     for column in csv_columns:
    #         table_statement_list.append(f"{column} TEXT,\n")
    #
    #     table_statement_list[-1] = re.sub(",\n$", "", table_statement_list[-1])
    #     # table_statement_list.append(f"Row_Last_Updated TEXT")
    #
    #     table_statement_list.append(");")
    #     table_statement = "".join(table_statement_list)
    #     return table_statement

    # def get_csv_column_type(self, field_name: str, csv_column_types):
    #     if field_name in csv_column_types:
    #         column_type = csv_column_types()[field_name]
    #     else:
    #         column_type = ''
    #     return column_type

    def prepare_database_row_vmpc(self, item_dict: dict, csv_columns: list,
                                  csv_column_types: list, batch_date: str, batch_number: str):
        row_in_sqlite_form = []
        for field_name in csv_columns:  # Iterate through expected columns (contract)
            if field_name in item_dict.keys():  # Iterate through columns found in dictionary
                item_dict[field_name] = \
                    self.prepare_database_field_vmpc(item_dict[field_name], field_name, csv_column_types)
                row_in_sqlite_form.append(item_dict[field_name])
            else:
                if field_name == 'Row_Last_Updated':
                    row_in_sqlite_form.append(etld_lib_datetime.get_utc_datetime_sqlite_database_format())
                elif field_name == 'BATCH_DATE':
                    row_in_sqlite_form.append(batch_date)
                elif field_name == 'BATCH_NUMBER':
                    row_in_sqlite_form.append(batch_number)
                else:
                    row_in_sqlite_form.append("")  # Ensure blank is added to each required empty field

        return row_in_sqlite_form

    def prepare_database_field_vmpc(self, field_data: dict, field_name_tmp, csv_column_types: list):
        if field_name_tmp in csv_column_types:
            field_column_type = csv_column_types[field_name_tmp]
        else:
            field_column_type = ''

        if field_column_type == 'INTEGER':
            field_data = str(field_data).strip()
            if str(field_data).isnumeric():
                field_data = str(field_data)
            else:
                field_data = '0'
        elif field_data is None:
            field_data = ""
        elif 'DATE' in field_name_tmp:
            field_data = str(field_data).replace("T", " ").replace("Z", "")
            field_data = re.sub("\\..*$", "", field_data)
        elif isinstance(field_data, int):
            field_data = str(field_data)
        elif 'CVE_LIST' in field_name_tmp:
            if 'CVE' in field_data.keys():
                if isinstance(field_data['CVE'], dict):
                    one_item_dict = [field_data['CVE']]
                    field_data['CVE'] = one_item_dict
                    field_data = json.dumps(field_data)
                else:
                    field_data = json.dumps(field_data)
        elif not isinstance(field_data, str):
            field_data = json.dumps(field_data)

        field_data = etld_lib_config.remove_null_soh_cr_and_display_utf8(field_column_type, field_name_tmp, field_data)

        return field_data




    def prepare_database_row_was(self, item_dict: dict, csv_columns: list, csv_column_types: list,
                                 batch_name: str, batch_date: str, batch_number: str):
        row_in_sqlite_form = []
        for field_name in csv_columns:  # Iterate through expected columns (contract)
            if field_name in item_dict.keys():  # Iterate through columns found in dictionary
                item_dict[field_name] = \
                    self.prepare_database_field_was(item_dict[field_name], field_name, csv_column_types)
                row_in_sqlite_form.append(item_dict[field_name])
            else:
                if field_name == 'Row_Last_Updated':
                    row_in_sqlite_form.append(etld_lib_datetime.get_utc_datetime_sqlite_database_format())
                elif field_name == 'BATCH_DATE':
                    row_in_sqlite_form.append(batch_date)
                elif field_name == 'BATCH_NUMBER':
                    row_in_sqlite_form.append(batch_number)
                else:
                    row_in_sqlite_form.append("")  # Ensure blank is added to each required empty field

        return row_in_sqlite_form


    def prepare_database_field_was(self, field_data: dict, field_name_tmp, csv_column_types: list):
        if field_name_tmp in csv_column_types:
            field_column_type = csv_column_types[field_name_tmp]
        else:
            field_column_type = ''
        if field_column_type == 'INTEGER':
            field_data = str(field_data).strip()
            if str(field_data).isnumeric():
                field_data = str(field_data)
            else:
                field_data = '0'
        elif field_data is None:
            field_data = ""
        elif 'lastBoot' in field_name_tmp:
            field_data = str(field_data).replace("T", " ").replace("Z", "")
            field_data = re.sub("\\..*$", "", field_data)
        elif 'Date' in field_name_tmp:
            field_data = str(field_data).replace("T", " ").replace("Z", "")
            field_data = re.sub("\\..*$", "", field_data)
        elif isinstance(field_data, int):
            field_data = str(field_data)
        elif not isinstance(field_data, str):
            field_data = json.dumps(field_data)

        field_data = etld_lib_config.remove_null_soh_cr_and_display_utf8(field_column_type, field_name_tmp, field_data)

        return field_data

    # ADDED PCRS PREPARE ROW AND FIELD.

    # TODO ADD LOGIN FOR pcrs_postureinfo_controls_row.
    # Take results of prepare_database_row_pcrs and create another function that returns
    # both rows.  1. postureinfo row normalized ( columns blanked out )
    def prepare_database_row_pcrs(self, item_dict: dict, csv_columns: list, csv_column_types: list,
                                 batch_name: str, batch_date: str, batch_number: str):
        row_in_sqlite_form = []
        for field_name in csv_columns:  # Iterate through expected columns (contract)
            if field_name in item_dict.keys():  # Iterate through columns found in dictionary
                item_dict[field_name] = \
                    self.prepare_database_field_pcrs(item_dict[field_name], field_name, csv_column_types)
                row_in_sqlite_form.append(item_dict[field_name])
            else:
                if field_name == 'Row_Last_Updated':
                    row_in_sqlite_form.append(etld_lib_datetime.get_utc_datetime_sqlite_database_format())
                elif field_name == 'BATCH_DATE':
                    row_in_sqlite_form.append(batch_date)
                elif field_name == 'BATCH_NUMBER':
                    row_in_sqlite_form.append(batch_number)
                else:
                    row_in_sqlite_form.append("")  # Ensure blank is added to each required empty field

        return row_in_sqlite_form


    def prepare_database_field_pcrs(self, field_data: dict, field_name_tmp, csv_column_types: list):
        if field_name_tmp in csv_column_types:
            field_column_type = csv_column_types[field_name_tmp]
        else:
            field_column_type = ''
        if field_column_type == 'INTEGER':
            field_data = str(field_data).strip()
            if str(field_data).isnumeric():
                field_data = str(field_data)
            else:
                field_data = '0'
        elif field_data is None:
            field_data = ""
        elif 'lastBoot' in field_name_tmp:
            field_data = str(field_data).replace("T", " ").replace("Z", "")
            field_data = re.sub("\\..*$", "", field_data)
        elif 'Date' in field_name_tmp:
            field_data = str(field_data).replace("T", " ").replace("Z", "")
            field_data = re.sub("\\..*$", "", field_data)
        elif 'created' in field_name_tmp:
            field_data = str(field_data).replace("T", " ").replace("Z", "")
            field_data = re.sub("\\..*$", "", field_data)
        elif isinstance(field_data, int):
            field_data = str(field_data)
        elif not isinstance(field_data, str):
            field_data = json.dumps(field_data)

        field_data = etld_lib_config.remove_null_soh_cr_and_display_utf8(field_column_type, field_name_tmp, field_data)

        return field_data

    def pcrs_check_if_key_exists_in_postureinfo_policy_control_technology(self, policyid, controlid, technologyid) -> bool:
        key = f"{policyid}_{controlid}_{technologyid}"
        if key in self.pcrs_postureinfo_policy_control_technlogy_dict:
            key_value = self.pcrs_postureinfo_policy_control_technlogy_dict[key] + 1
            self.pcrs_postureinfo_policy_control_technlogy_dict[key] = key_value
            return True
        else:
            self.pcrs_postureinfo_policy_control_technlogy_dict[key] = 1
            return False

    def prepare_database_row_asset_inventory(self, item_dict: dict, csv_columns: list, csv_column_types: list,
                                             batch_name: str, batch_date: str, batch_number: str):
        row_in_sqlite_form = []
        for field_name in csv_columns:  # Iterate through expected columns (contract)
            if field_name in item_dict.keys():  # Iterate through columns found in dictionary
                item_dict[field_name] = \
                    self.prepare_database_field_asset_inventory(item_dict[field_name], field_name, csv_column_types)
                row_in_sqlite_form.append(item_dict[field_name])
            else:
                if field_name == 'Row_Last_Updated':
                    row_in_sqlite_form.append(etld_lib_datetime.get_utc_datetime_sqlite_database_format())
                elif field_name == 'BATCH_DATE':
                    row_in_sqlite_form.append(batch_date)
                elif field_name == 'BATCH_NUMBER':
                    row_in_sqlite_form.append(batch_number)
                else:
                    row_in_sqlite_form.append("")  # Ensure blank is added to each required empty field

        return row_in_sqlite_form

    def prepare_database_field_asset_inventory(self, field_data: dict, field_name_tmp, csv_column_types: list):

        if field_name_tmp in csv_column_types:
            field_column_type = csv_column_types[field_name_tmp]
        else:
            field_column_type = ''

        if field_column_type == 'INTEGER':
            field_data = str(field_data).strip()
            if str(field_data).isnumeric():
                field_data = str(field_data)
            else:
                field_data = '0'
        elif field_data is None:
            field_data = ""
        elif 'lastBoot' in field_name_tmp:
            field_data = str(field_data).replace("T", " ").replace("Z", "")
            field_data = re.sub("\\..*$", "", field_data)
        elif 'Date' in field_name_tmp:
            field_data = str(field_data).replace("T", " ").replace("Z", "")
            field_data = re.sub("\\..*$", "", field_data)
        elif 'dns' in str(field_name_tmp).lower():
            field_data = str(field_data).replace('\n', '')
        elif isinstance(field_data, int):
            field_data = str(field_data)
        elif not isinstance(field_data, str):
            field_data = json.dumps(field_data)

        field_data = etld_lib_config.remove_null_soh_cr_and_display_utf8(field_column_type, field_name_tmp, field_data)

        return field_data

    # def prepare_database_field(self, field_data, field_name_tmp, field_column_type) -> dict:
    #     if field_column_type == 'INTEGER':
    #         field_data = str(field_data).strip()
    #         if str(field_data).isnumeric():
    #             field_data = str(field_data)
    #         else:
    #             field_data = '0'
    #     elif field_data is None:
    #         field_data = ""
    #     elif isinstance(field_data, str):
    #         if 'date' in str(field_name_tmp).lower():
    #             field_data = field_data.replace("T", " ").replace("Z", "")
    #             field_data = re.sub("\\..*$", "", field_data)
    #         elif 'dns' in str(field_name_tmp).lower():
    #             field_data = field_data.replace('\n', '')
    #     elif isinstance(field_data, int):
    #         field_data = str(field_data)
    #     elif not isinstance(field_data, str):
    #         field_data = json.dumps(field_data)
    #
    #     return field_data

    # def prepare_database_row_integer_fields(self, item: dict, database_columns: list, database_column_types: dict) -> list:
    #     for field_name in database_columns:
    #         if field_name in item.keys():
    #             field_column_type = ""
    #             if field_name in database_column_types:
    #                 if database_column_types[field_name] == 'INTEGER':
    #                     if item[field_name] =
    #                     item[field_name]
    #                 field_column_type = database_column_types[field_name]
    #
    #             item[field_name] = \
    #                 self.prepare_database_field(item[field_name], field_name, field_column_type)
    #             row_in_sqlite_form.append(item[field_name])
    #         else:
    #             row_in_sqlite_form.append("")  # Ensure blank is added to each required empty field
    #

    # def prepare_database_row(self, item: dict, database_columns: list, database_column_types: dict) -> list:
    #     row_in_sqlite_form = []
    #     for field_name in database_columns:
    #         if field_name in item.keys():
    #             field_column_type = ""
    #             if field_name in database_column_types:
    #                 field_column_type = database_column_types[field_name]
    #             item[field_name] = \
    #                 self.prepare_database_field(item[field_name], field_name, field_column_type)
    #             row_in_sqlite_form.append(item[field_name])
    #         else:
    #             row_in_sqlite_form.append("")  # Ensure blank is added to each required empty field
    #     return row_in_sqlite_form

    # def prepare_integer_columns_for_database(self, table_name: str, row: list):
    #     if table_name in self.pragma_dict:
    #         pragma = self.pragma_dict['table_name']
    #     else:
    #         pragma = self.get_pragma(self.cursor, table_name)
    #         self.pragma_dict[table_name] = pragma
    #
    #     row_fields = []
    #     for idx, fieldname in pragma:
    #         field_data = row[idx]
    #         if pragma[idx][2] == 'INTEGER':
    #             field_data = str(row[idx]).strip()
    #             if not str(row[idx]).isnumeric():
    #                 field_data = '0'
    #         row_fields.append(field_data)
    #     return row_fields

    # def insert_or_replace_row(self, table_name: str, row: list):
    #     result = True
    #     try:
    #         self.cursor.execute(f"INSERT OR REPLACE INTO {table_name} "
    #                             f"VALUES({self.get_values_var(row)},datetime('now'))",
    #                             row)
    #     except Exception as e:
    #         etld_lib_functions.logger.error(
    #             f"Error inserting or replacing row into table: {table_name}, please retry after fixing error")
    #         etld_lib_functions.logger.error(f"Exception: {e}")
    #         result = False
    #
    #     return result

    # def insert_or_replace_row_pristine(self, table_name: str, row: list):
    #     result = True
    #     try:
    #         # Added 2025-03-24 to clean up \U0000
    #         cleaned_row = etld_lib_config.remove_unicode_null_from_row(row)
    #         self.cursor.execute(f"INSERT OR REPLACE INTO {table_name} "
    #                             f"VALUES({self.get_values_var(row)})",
    #                             cleaned_row)
    #     except Exception as e:
    #         etld_lib_functions.logger.error(
    #             f"Error inserting or replacing pristine row into table: {table_name}, please retry after fixing error")
    #         etld_lib_functions.logger.error(f"Exception: {e}")
    #         result = False
    #
    #     return result


    def insert_or_replace_row_pristine(self, table_name: str, row: list):
        max_attempts = 15
        attempt = 1

        # Added retry loop 2025-04-01
        while attempt <= max_attempts:
            try:
                # Added 2025-03-24 to clean up \U0000
                cleaned_row = etld_lib_config.remove_unicode_null_from_row(row)
                self.cursor.execute(f"INSERT OR REPLACE INTO {table_name} "
                                    f"VALUES({self.get_values_var(row)})",
                                    cleaned_row)
                return True  # If successful, return immediately

            except Exception as e:
                if attempt == max_attempts:
                    etld_lib_functions.logger.error(
                        f"Attempt {attempt} failed - Error inserting or replacing pristine row into table: {table_name}")
                    etld_lib_functions.logger.error(f"All {max_attempts} attempts failed. Giving up.")
                    etld_lib_functions.logger.error(f"Exception: {e}")
                    return False
                else:
                    etld_lib_functions.logger.warning(
                        f"Attempt {attempt} failed - retry inserting or replacing pristine row into table: {table_name}")
                    etld_lib_functions.logger.warning(f"Exception: {e}")

                # Sleep for 5 minutes (300 seconds) before next attempt
                time.sleep(300)
                attempt += 1

    # def insert_or_replace_row_including_datetime(self, table_name: str, row: list, datetime: str):
    #     result = True
    #     try:
    #         row.append(datetime)
    #         self.cursor.execute(f"INSERT OR REPLACE INTO {table_name} "
    #                             f"VALUES({self.get_values_var(row)})",
    #                             row)
    #     except Exception as e:
    #         etld_lib_functions.logger.error(
    #             f"Error inserting or replacing row into table: {table_name}, please retry after fixing error")
    #         etld_lib_functions.logger.error(f"Exception: {e}")
    #         result = False
    #
    #     return result

    # def insert_row_into_csv(self, table_name: str, row: list, csv_obj: etld_lib_sqlite_to_csv.SqliteTabletoCsvFile):
    #     result = True
    #     try:
    #         csv_obj.write_row(row)
    #     except Exception as e:
    #         etld_lib_functions.logger.error(
    #             f"Error writing csv record from {table_name}, please retry after fixing error")
    #         etld_lib_functions.logger.error(f"Exception: {e}")
    #         exit(1)
    #     return result

    def insert_unique_row_ignore_duplicates(self, table_name: str, row: list):
        result = True
        try:
            #self.cursor.execute(f"INSERT INTO {table_name} VALUES({self.get_values_var(row)},datetime('now'))", row)
            # Added 2025-03-24 - remove unicode null from data.
            cleaned_row = etld_lib_config.remove_unicode_null_from_row(row)
            self.cursor.execute(f"INSERT INTO {table_name} VALUES({self.get_values_var(row)})", cleaned_row)
        except sqlite3.IntegrityError as err:
            if 'unique constraint failed' in str(err).lower():
                result = "duplicate"
                #etld_lib_functions.logger.warning(
                #    f"Duplicate Key, inserting into: {table_name}, ignore, first field: {row[0]}")
                #etld_lib_functions.logger.error(f"Exception: {err}")
                pass
            else:
                etld_lib_functions.logger.error(
                    f"Integrity Error inserting into: {table_name}, please retry after fixing error")
                etld_lib_functions.logger.error(f"Exception: {err}")
                exit(1)

        except sqlite3.Error as err:
            etld_lib_functions.logger.error(
                f"Error inserting row into table: {table_name}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {err}")
            exit(1)
        except Exception as e:
            etld_lib_functions.logger.error(
                f"Error inserting row into table: {table_name}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)
        return result

    # def insert_unique_row(self, table_name: str, values_var: list, row: list, conflict: str):
    #     try:
    #         self.cursor.execute(f"INSERT INTO {table_name} VALUES({values_var},datetime('now'))", row)
    #     except sqlite3.Error as err:
    #         etld_lib_functions.logger.error(
    #             f"Error inserting row into table: {table_name}, please retry after fixing error")
    #         etld_lib_functions.logger.error(f"Exception: {err}")
    #         exit(1)
    #     except Exception as e:
    #         etld_lib_functions.logger.error(
    #             f"Error inserting row into table: {table_name}, please retry after fixing error")
    #         etld_lib_functions.logger.error(f"Exception: {e}")
    #         exit(1)

    def commit_changes(self, message=""):
        try:
            self.connection.commit()
            etld_lib_functions.logger.info(f"{message}commit to database {self.sqlite_file}")
        except Exception as e:
            etld_lib_functions.logger.error(
                f"Error committing to: {self.sqlite_file}, please retry after fixing error: message={message}")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    def close_connection(self):
        try:
            self.connection.close()
        except Exception as e:
            etld_lib_functions.logger.error(
                f"Error closing: {self.sqlite_file}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)
        finally:
            etld_lib_functions.logger.info(f"sqlite3 connection closed for {self.sqlite_file}")

    def vacuum_database(self):
        try:
            self.isolation_level = self.connection.isolation_level
            self.connection.isolation_level = None
            self.connection.execute("VACUUM")
            self.connection.isolation_level = self.isolation_level
        except Exception as e:
            etld_lib_functions.logger.error(
                f"Error vacuuming database: {self.sqlite_file}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    def select_all_from_table(self, table_name):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        return self.cursor.fetchall()

    def select_all_from_table_where_table_column_equals_value(
            self, table_name, table_column, where_table_column_equals_value):
        self.cursor.execute(f"SELECT * FROM {table_name} WHERE {table_column} LIKE '{where_table_column_equals_value}'")
        return self.cursor.fetchall()

    def select_from_table(self, select_statement):
        self.cursor.execute(f"{select_statement}")
        return self.cursor.fetchall()

    def select_all_from_status_table_where_status_name_equals_table_name(
            self, status_table_name, table_name):
        self.cursor.execute(f"SELECT * FROM {status_table_name}")
        return self.cursor.fetchall()

    @staticmethod
    def get_values_var(csv_columns: list):
        values_var = ""
        for column in csv_columns:
            values_var = f"{values_var}?, "
        values_var = re.sub("\?, $", "?", values_var)
        return values_var

    @staticmethod
    def status_table_prepare_fields_for_update(status_name='HOST_LIST_LOAD_STATUS', batch_date="", batch_number="0",
                                               status='COMPLETED', total_rows_added=0):
        status_name = status_name
        try:
            logfile_run_datetime = etld_lib_functions.logger_datetime
            logfile_workflow_name = etld_lib_functions.my_logger_program_name_for_database_routine
            status_detail_dict = {'BATCH_DATE': batch_date,
                                  'BATCH_NUMBER': batch_number,
                                  'STATUS': status,
                                  'TOTAL_ROWS_ADDED': total_rows_added,
                                  'LOG_WORKFLOW_DATE': logfile_run_datetime,
                                  'LOG_WORKFLOW_NAME': logfile_workflow_name
                                  }
        except AttributeError:
            status_detail_dict = {'BATCH_DATE': batch_date,
                                  'BATCH_NUMBER': batch_number,
                                  'STATUS': status,
                                  'TOTAL_ROWS_ADDED': total_rows_added,
                                  'LOG_WORKFLOW_DATE': "",
                                  'LOG_WORKFLOW_NAME': ""
                                  }

        # change to support text field of batch name - status_count (last_batch_processed) = int(batch_number)
        last_batch_processed = batch_number
        return status_name, status_detail_dict, last_batch_processed


    @staticmethod
    def status_table_prepare_general_data_for_update(
            status_name='LOG_DATA', status_detail_dict={}, last_batch_processed="FALSE"):
            # LOG_DATA - status_detail_dict will be all logging relevant for job.
            #          - last_batch_prcoessed will be set to FALSE, ERROR, TRUE
            #          - If last_batch_processed is set to FALSE or ERROR, do not move forward with ETL.

        return status_name, status_detail_dict, last_batch_processed

    def update_status_table_general_data_update(self, status_table_name,
                                                status_name, status_detail_dict, last_batch_processed):

        self.status_table_insert_or_replace_row_in_sqlite(
            table_name=status_table_name,
            status_name=status_name,
            status_detail_dict=status_detail_dict,
            last_batch_processed=last_batch_processed
        )
        self.status_table_select_status_row_from_sqlite(
            table_name=status_table_name,
            table_column='STATUS_NAME',
            where_table_column_equals_value=status_name)

        etld_lib_functions.logger.info(f"Updated {status_table_name} - "
                                       f"status_name={status_name} - "
                                       f"last_batch_processed={last_batch_processed}")

    # def get_database_status_detail(self, status_name='ALL_TABLES_LOADED_SUCCESSFULLY'):
    #     database_table_names_list = self.get_all_table_names_from_database()
    #     status_detail = {}
    #     for database_table_name in database_table_names_list:
    #         if str(database_table_name).endswith("_Status"):
    #             self.cursor.execute(f"select * from {database_table_name} where STATUS_NAME == '{status_name}'")
    #             row = self.cursor.fetchall()
    #             if row is None:
    #                 etld_lib_functions.logger.info(f"TABLE: {database_table_name} "
    #                                                f"did not contain STATUS_NAME:{status_name} "
    #                                                f"required to retrieve STATUS_DETAIL")
    #                 status_detail = {}
    #             if 'STATUS_DETAIL' in row['STATUS_DETAIL']
    #                 json_string = row['STATUS_DETAIL']
    #                 status_detail = json.loads(json_string)
    #     return status_detail

    def get_database_status_detail(self, status_name='ALL_TABLES_LOADED_SUCCESSFULLY'):
        database_table_names_list = self.get_all_table_names_from_database()
        status_detail = {}
        for database_table_name in database_table_names_list:
            if str(database_table_name).endswith("_Status"):
                self.cursor.execute(
                    f"SELECT STATUS_DETAIL FROM {database_table_name} WHERE STATUS_NAME = '{status_name}'")
                row = self.cursor.fetchone()  # Fetch the first row
                if row is None:
                    etld_lib_functions.logger.info(f"TABLE: {database_table_name} "
                                                   f"did not contain STATUS_NAME: {status_name} "
                                                   f"required to retrieve STATUS_DETAIL.")
                else:
                    # Assuming STATUS_DETAIL is in the first column of the row
                    json_string = row[0]
                    try:
                        status_detail[database_table_name] = json.loads(json_string)
                        return status_detail[database_table_name]
                    except json.JSONDecodeError:
                        etld_lib_functions.logger.error(
                            f"Failed to decode JSON from {database_table_name}: {json_string}")

    def validate_all_tables_loaded_successfully(self):
        try:
            self.commit_changes()
            status_detail = self.get_database_status_detail()

            if not status_detail:
                time.sleep(10)
                etld_lib_functions.logger.error(f"FAIL ALL_TABLES_LOADED_SUCCESSFULLY: {self.sqlite_file}")
                exit(1)
            if 'STATUS' in status_detail and status_detail['STATUS'] == 'FINAL BATCH LOADED':
                etld_lib_functions.logger.info(f"PASS ALL_TABLES_LOADED_SUCCESSFULLY - {self.sqlite_file} - STATUS: {status_detail}")
                return True
            else:
                time.sleep(10)
                etld_lib_functions.logger.error(f"FAIL ALL_TABLES_LOADED_SUCCESSFULLY - {self.sqlite_file} - STATUS: {status_detail}")
                exit(1)
        except Exception as e:
            time.sleep(10)
            etld_lib_functions.logger.error(f"validate_all_tables_loaded_successfully error: {self.sqlite_file}, "
                                            f"please investigate {sys.argv}")
            etld_lib_functions.logger.error(f"Exception: {e}")
            formatted_lines = traceback.format_exc().splitlines()
            etld_lib_functions.logger.error(f"TRACEBACK: {formatted_lines}")
            exit(1)
        except KeyboardInterrupt:
            time.sleep(10)
            etld_lib_functions.logger.error(f"validate_all_tables_loaded_successfully error: {self.sqlite_file}, "
                                            f"please investigate {sys.argv}")
            etld_lib_functions.logger.error("Caught a KeyboardInterrupt, performing cleanup...")
            formatted_lines = traceback.format_exc().splitlines()
            etld_lib_functions.logger.error(f"TRACEBACK: {formatted_lines}")
            exit(1)
        except SystemExit:
            time.sleep(10)
            etld_lib_functions.logger.error(f"validate_all_tables_loaded_successfully error: {self.sqlite_file}, "
                                            f"please investigate {sys.argv}")
            etld_lib_functions.logger.error("Caught a SystemExit, performing cleanup...")
            formatted_lines = traceback.format_exc().splitlines()
            etld_lib_functions.logger.error(f"TRACEBACK: {formatted_lines}")
            exit(1)

    def status_table_insert_or_replace_row_in_sqlite(self,
                                                     table_name: str, status_name: str, status_detail_dict: dict,
                                                     last_batch_processed: str, commit_changes: bool = True):
        status_detail_json = json.dumps(status_detail_dict)
        row_last_updated_datetime = etld_lib_datetime.get_utc_datetime_sqlite_database_format()
        row_to_insert = [status_name,
                         status_detail_json,
                         last_batch_processed,
                         row_last_updated_datetime
                         ]
        result = self.insert_or_replace_row_pristine(
            table_name=table_name,
            row=row_to_insert
        )
        if commit_changes is True:
            self.commit_changes(message=f"{table_name} updated - ")

    def status_table_select_status_row_from_sqlite(self,
                                                   table_name: str, table_column: str,
                                                   where_table_column_equals_value: str):
        result = self.select_all_from_table_where_table_column_equals_value(
            table_name=table_name,
            table_column=table_column,
            where_table_column_equals_value=where_table_column_equals_value
        )
        status_name = result[0]['STATUS_NAME']
        status_detail_dict = json.loads(result[0]['STATUS_DETAIL'])
        last_batch_processed = result[0]['LAST_BATCH_PROCESSED']
        return status_name, status_detail_dict, last_batch_processed

    def update_status_table(self,
                            batch_date: str,
                            batch_number: str,
                            total_rows_added_to_database: int,
                            status_table_name: str,
                            status_table_columns: list,
                            status_table_column_types: list,
                            status_name_column: str = 'TABLE_LOAD_STATUS',
                            status_column: str = 'begin'):

        status_column_dict = {'begin': 'BEGIN LOADING BATCH',
                              'end': 'END LOADING BATCH',
                              'final': 'FINAL BATCH LOADED',
                              }

        if status_column in status_column_dict.keys():
            status_column_display = status_column_dict[status_column]
        else:
            status_column_display = status_column

        status_name, status_detail_dict, last_batch_processed = \
            self.status_table_prepare_fields_for_update(
                status_name=status_name_column,
                batch_date=batch_date,
                batch_number=batch_number,
                status=status_column_display,
                total_rows_added=total_rows_added_to_database)

        self.status_table_insert_or_replace_row_in_sqlite(
            table_name=status_table_name,
            status_name=status_name,
            status_detail_dict=status_detail_dict,
            last_batch_processed=str(last_batch_processed)
        )

        status_name, status_detail_dict, last_batch_processed = \
            self.status_table_select_status_row_from_sqlite(
                table_name=status_table_name,
                table_column='STATUS_NAME',
                where_table_column_equals_value=status_name)
        etld_lib_functions.logger.info(f"Updated {status_table_name} - "
                                       f"status_name={status_name} - status_detail_dict={status_detail_dict}")

        return status_name, status_detail_dict, last_batch_processed

    def bulk_insert_csv_file(self, table_name, csv_file_name, csv_columns, message="",
                             display_progress_counter_at_this_number=10000,
                             delimiter=',', header_present=True,
                             key_column_index="", key_to_look_for_in_data=""):
        csv.field_size_limit(sys.maxsize)
        sqlite_rows_written = \
            etld_lib_functions.DisplayCounterToLog(
                display_counter_at=display_progress_counter_at_this_number,
                logger_func=etld_lib_functions.logger.info,
                display_counter_log_message=f"count {table_name} sqlite rows written")
        # etld_lib_functions.logger.info(f"csv.field_size_limit(sys.maxsize): {str(sys.maxsize)}")
        try:
            values_var = ""
            for column in csv_columns:
                values_var = f"{values_var}?, "
            values_var = re.sub("\?, $", "?", values_var)
            csv_headers = ""
            csv_row_list = []
            bulk_insert_count = 100000
            with open(csv_file_name, "rt", encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=delimiter)
                self.count_rows_added_to_table = 0
                if header_present is True:
                    csv_headers = next(csv_reader)  # Skip Header
                for row in csv_reader:
                    if isinstance(key_column_index, int):
                        if key_column_index <= len(row):
                            if key_to_look_for_in_data in row[key_column_index]:
                                pass  # Insert row with key.  Ex. 'etl_was 20220122180000'
                            else:
                                continue
                    self.cursor.execute(
                        f"INSERT OR REPLACE INTO {table_name} VALUES({values_var},datetime('now'))", row)
                    sqlite_rows_written.update_counter_and_display_to_log()
                    self.count_rows_added_to_table += 1
                self.commit_changes()
                sqlite_rows_written.display_final_counter_to_log()

        except sqlite3.Error as err:
            etld_lib_functions.logger.error(
                f"Error inserting row into table: {table_name}, please retry after fixing error")
            etld_lib_functions.logger.error(f"Exception: {err}")
            exit(1)
        except Exception as e:
            etld_lib_functions.logger.error(f"Error creating table from: {csv_file_name}, retry after fixing error")
            etld_lib_functions.logger.error(f"Row Number: {self.count_rows_added_to_table}")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

    import sqlite3
    import time

    def count_select_statement(self, cursor, sql_statement):
        try:
            cursor.execute(sql_statement)
            result = cursor.fetchone()
            if result:
                return f"{result[0]}"
            else:
                # It's unusual for COUNT() to return None, as it should return 0 if no rows match.
                # Returning None as the count, along with an explanation.
                return "Unexpected result: COUNT() returned no rows."
        except Exception as e:
            # Return None as the count and the error message
            fun_error = str(e)
            return f"Exception query:{sql_statement}: {fun_error}"

    def create_q_knowledgebase_in_host_list_detection(self, max_retries=5, backoff_factor=2):
        create_index_sql = "CREATE INDEX IF NOT EXISTS temp_idx_qid ON Q_Host_List_Detection_QIDS(QID);"
        create_table_sql = "CREATE TABLE Q_QIDS AS SELECT DISTINCT(QID) FROM Q_Host_List_Detection_QIDS; "
        insert_sql = ("INSERT OR IGNORE INTO Q_KnowledgeBase_In_Host_List_Detection "
                      "SELECT * FROM K1.Q_KnowledgeBase WHERE K1.Q_KnowledgeBase.QID IN (SELECT QID FROM Q_QIDS); ")
        drop_table_sql = "DROP TABLE IF EXISTS Q_QIDS;"

        drop_index_sql = "DROP INDEX IF EXISTS temp_idx_qid;"
        index_name = 'temp_idx_qids'
        select_count_qids = "SELECT COUNT(QID) FROM Q_KnowledgeBase_In_Host_List_Detection;"

        # Original query that had trouble running on large tables with low AWS IOPS.
        original_query = ("INSERT INTO Q_KnowledgeBase_In_Host_List_Detection SELECT * FROM K1.Q_KnowledgeBase "
                          "where K1.Q_KnowledgeBase.QID in (select distinct(QID) from Q_Host_List_Detection_QIDS)")
        retries = 0
        success_flag = False
        sql_statement = ""
        while retries < max_retries:
            try:
                cursor = self.cursor
                step_number = 0

                # Drop Table
                sql_statement = drop_table_sql
                step_number += 1
                etld_lib_functions.logger.info(f"{step_number}) Attempt {retries + 1} Try: {sql_statement}")
                cursor.execute(sql_statement)
                time.sleep(5)

                # Explain Query Plan BEFORE
                step_number += 1
                sql_statement = f"EXPLAIN QUERY PLAN {create_table_sql}"
                etld_lib_functions.logger.info(f"{step_number}) Attempt {retries + 1} Try: {sql_statement}")
                cursor.execute(sql_statement)
                results = cursor.fetchall()
                formatted_results = [' '.join(map(str, row)) for row in results]
                one_line_plan = '; '.join(formatted_results).replace('|', '[pipe to]')
                step_number += 1
                etld_lib_functions.logger.info(f"{step_number}) Attempt {retries + 1} NO IDX QUERY_PLAN: {one_line_plan}")

                # Create QID Index
                step_number += 1
                sql_statement = create_index_sql
                etld_lib_functions.logger.info(f"{step_number}) Attempt {retries + 1} Try: {sql_statement}")
                cursor.execute(sql_statement)
                time.sleep(5)

                # Explain Query Plan AFTER
                step_number += 1
                sql_statement = f"EXPLAIN QUERY PLAN {create_table_sql}"
                etld_lib_functions.logger.info(f"{step_number}) Attempt {retries + 1} Try: {sql_statement}")
                cursor.execute(sql_statement)
                results = cursor.fetchall()
                formatted_results = [' '.join(map(str, row)) for row in results]
                one_line_plan = '; '.join(formatted_results).replace('|', '[pipe to]')
                step_number += 1
                etld_lib_functions.logger.info(f"{step_number}) Attempt {retries + 1} IDX QUERY_PLAN: {one_line_plan}")

                # Create Q_QIDS Temp Table
                step_number += 1
                sql_statement = create_table_sql
                etld_lib_functions.logger.info(f"{step_number}) Attempt {retries + 1} Try: {sql_statement}")
                cursor.execute(sql_statement)
                time.sleep(5)

                # Create Q_KnowledgeBase_In_Host_List_Detection
                step_number += 1
                sql_statement = insert_sql
                etld_lib_functions.logger.info(f"{step_number}) Attempt {retries + 1} Try: {sql_statement}")
                cursor.execute(sql_statement)
                time.sleep(5)

                # Drop Table
                step_number += 1
                sql_statement = drop_table_sql
                etld_lib_functions.logger.info(f"{step_number}) Attempt {retries + 1} Try: {sql_statement}")
                cursor.execute(sql_statement)
                time.sleep(5)

                # Drop Temp Index
                step_number += 1
                sql_statement = drop_index_sql
                etld_lib_functions.logger.info(f"{step_number}) Attempt {retries + 1} Try: {sql_statement}")
                cursor.execute(sql_statement)
                time.sleep(5)

                # COUNT KNOWLEDGEBASE RECORDS FOUND.
                step_number += 1
                sql_statement = select_count_qids
                etld_lib_functions.logger.info(f"{step_number}) Attempt {retries + 1} Try: {sql_statement}")
                qids_found = self.count_select_statement(cursor, sql_statement)
                time.sleep(5)
                step_number += 1
                etld_lib_functions.logger.info(f"{step_number}) Attempt {retries + 1} Try: QIDS FOUND: {qids_found}")

                # REPORT SUCCESS
                step_number += 1
                self.commit_changes()
                time.sleep(5)
                etld_lib_functions.logger.info(f"{step_number}) Attempt {retries + 1} Success creating Q_KnowledgeBase_In_Host_List_Detection")
                success_flag = True
                break
            except sqlite3.Error as e:
                time.sleep(5)
                etld_lib_functions.logger.warning(f"Attempt {retries + 1} failed: {sql_statement} - sqlite3.Error: {e}")
                retries += 1
                time.sleep(backoff_factor ** retries)  # Exponential backoff
            except Exception as e:
                time.sleep(5)
                etld_lib_functions.logger.warning(f"Attempt {retries + 1} failed: {sql_statement} - Other Exception: {e}")
                retries += 1
                time.sleep(backoff_factor ** retries)  # Exponential backoff

        if retries == max_retries:
            time.sleep(5)
            etld_lib_functions.logger.error(f"Attempt {retries + 1} Failed: {sql_statement}")
            etld_lib_functions.logger.error("Failed to create Q_QIDS table after maximum retries. Please check the database.")
        if success_flag == False:
            time.sleep(5)
            etld_lib_functions.logger.error(f"Attempt {retries + 1} Failed, success flag: {success_flag}")
            print("Failed to create Q_QIDS table after maximum retries. Please check the database.")

    # Example usage:
    # create_q_qids_table('your_database_file_path_here.db')

