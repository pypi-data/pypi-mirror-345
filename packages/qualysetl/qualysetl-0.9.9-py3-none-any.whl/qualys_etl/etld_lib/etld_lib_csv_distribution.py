#!/usr/bin/env python3
import os
# 2023-05-13 import oschmod
import gzip
import csv
import json
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_sqlite_tables
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_oschmod as oschmod



class CsvDistribution():

    def __init__(self,
                 target_csv_path,
                 target_csv_data_directory
                 ):

        self.csv_writer = None
        self.target_csv_path = target_csv_path
        self.target_csv_data_directory = target_csv_data_directory
        if not target_csv_data_directory.is_dir():
            self.create_directory(target_csv_data_directory)

    def set_csv_writer_with_file_handle(self, file_handle):
        # csv_key = etld_lib_config.get_python_csv_quoting_option_key(
        #     csv_value=etld_lib_config.csv_distribution_python_csv_quoting
        # )
        #etld_lib_functions.logger.info(f"python_csv_options: {csv_key} {etld_lib_config.get_csv_distribution_var_dict()}")
        #etld_lib_functions.logger.info(
        #    f"tested_mysql_load_example: {etld_lib_config.csv_distribution_mysql_load_example} "
        #    f"- note bash requires additional \\")
       #csv_writer = csv.writer(file_handle, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL, doublequote = True)
        # csv_writer = csv.writer(file_handle, delimiter='\x01', escapechar='\\', quoting=csv.QUOTE_ALL)
        # csv_writer = csv.writer(file_handle, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC, doublequote=True, escapechar='\\')
        # DOES NOT WORK csv_writer = csv.writer(file_handle, dialect=csv.excel)

        csv_writer = csv.writer(file_handle,
                               quoting=etld_lib_config.csv_distribution_python_csv_quoting,
                               delimiter=etld_lib_config.csv_distribution_python_csv_dialect_delimiter,
                               doublequote=etld_lib_config.csv_distribution_python_csv_dialect_doublequote,
                               escapechar=etld_lib_config.csv_distribution_python_csv_dialect_escapechar,
                               lineterminator=etld_lib_config.csv_distribution_python_csv_dialect_lineterminator,
                               quotechar=etld_lib_config.csv_distribution_python_csv_dialect_quotechar,
                               skipinitialspace=etld_lib_config.csv_distribution_python_csv_dialect_skipinitialspace,
                               strict=etld_lib_config.csv_distribution_python_csv_dialect_strict
                               )

        etld_lib_functions.logger.info(f"set_csv_writer_with_filehandle - csv_writer_dialect - "
                                       f"delimiter: '{csv_writer.dialect.delimiter}', "
                                       f"doublequote: '{csv_writer.dialect.doublequote}', "
                                       f"escapechar: '{csv_writer.dialect.escapechar}', "
                                       f"lineterminator: '{repr(csv_writer.dialect.lineterminator)}', "
                                       f"quotechar: '{csv_writer.dialect.quotechar}', "
                                       f"quoting: '{csv_writer.dialect.quoting}', "
                                       f"skipinitialspace: '{csv_writer.dialect.skipinitialspace}', "
                                       f"strict: '{csv_writer.dialect.strict}' "
                                       )
        self.csv_writer = csv_writer

    def write_csv_row_to_file_handle(self, row):
        cleaned_row = etld_lib_config.remove_unicode_null_from_row(row)
        self.csv_writer.writerow(cleaned_row)

    @staticmethod
    def create_directory(dir_path=None):
        try:
            if dir_path is not None:
                os.makedirs(dir_path, exist_ok=True)
                # 2023-05-13 oschmod.set_mode(dir_path, "a+rwx,g-rwx,o-rwx")
                oschmod.set_mode(dir_path, "u+rwx,g-rwx,o-rwx")
        except Exception as e:
            raise Exception(f"Could not create directory {dir_path}")

    @staticmethod
    def get_csv_writer(csv_file, csv_open_method=open):
        #delimiter=',',
        #lineterminator='\n',
        #quoting=csv.QUOTE_NONE,
        #escapechar='\\'
        # csv_key = etld_lib_config.get_python_csv_quoting_option_key(
        #     csv_value=etld_lib_config.csv_distribution_python_csv_quoting
        # )
        #etld_lib_functions.logger.info(f"python_csv_options: {csv_key} {etld_lib_config.get_csv_distribution_var_dict()}")
        #etld_lib_functions.logger.info(
        #    f"tested_mysql_load_example: {etld_lib_config.csv_distribution_mysql_load_example} "
        #    f"- note bash requires additional \\")
        # csv_writer = csv.writer(csv_open_method(csv_file, 'wt', newline=''),
        # delimiter = etld_lib_config.csv_distribution_python_csv_dialect_delimiter,
        # csv_writer=csv.writer(csv_open_method(csv_file, 'w', newline='', encoding='utf-8'),
        # NO csv_writer = csv.writer(file_handle, delimiter='\x01', escapechar='\\', quoting=csv.QUOTE_ALL)
        # NOcsv_writer = csv.writer(file_handle, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC, doublequote=True, escapechar='\\')
        # DOES NOT WORK csv_writer = csv.writer(file_handle, dialect=csv.excel)
        # etld_lib_functions.logger.info(f"get_csv_writer - csv_writer_dialect - "
        #                                f"delimiter: '{repr(etld_lib_functions.replace_non_printable_with_hex(csv_writer.dialect.delimiter))}', "
        #                                f"doublequote: '{repr(csv_writer.dialect.doublequote)}', "
        #                                f"escapechar: '{repr(etld_lib_functions.replace_non_printable_with_hex(csv_writer.dialect.escapechar))}', "
        #                                f"lineterminator: '{repr(etld_lib_functions.replace_non_printable_with_hex(csv_writer.dialect.lineterminator))}', "
        #                                f"quotechar: '{repr(csv_writer.dialect.quotechar)}', "
        #                                f"quoting: '{repr(csv_writer.dialect.quoting)}', "
        #                                f"skipinitialspace: '{repr(csv_writer.dialect.skipinitialspace)}', "
        #                                f"strict: '{repr(csv_writer.dialect.strict)}' "
        #                                )

        file_handle = csv_open_method(csv_file, 'wt', newline='', encoding='utf-8')
        csv_writer=csv.writer(file_handle,
                               quoting=etld_lib_config.csv_distribution_python_csv_quoting,
                               escapechar = etld_lib_config.csv_distribution_python_csv_dialect_escapechar,
                               delimiter=etld_lib_config.csv_distribution_python_csv_dialect_delimiter,
                               doublequote=etld_lib_config.csv_distribution_python_csv_dialect_doublequote,
                               lineterminator=etld_lib_config.csv_distribution_python_csv_dialect_lineterminator,
                               quotechar=etld_lib_config.csv_distribution_python_csv_dialect_quotechar,
                               skipinitialspace=etld_lib_config.csv_distribution_python_csv_dialect_skipinitialspace,
                               strict=etld_lib_config.csv_distribution_python_csv_dialect_strict
                               )

        etld_lib_functions.logger.info(f"set_csv_writer_with_filehandle - csv_writer_dialect - "
                                       f"delimiter: '{csv_writer.dialect.delimiter}', "
                                       f"doublequote: '{csv_writer.dialect.doublequote}', "
                                       f"escapechar: '{csv_writer.dialect.escapechar}', "
                                       f"lineterminator: '{repr(csv_writer.dialect.lineterminator)}', "
                                       f"quotechar: '{csv_writer.dialect.quotechar}', "
                                       f"quoting: '{csv_writer.dialect.quoting}', "
                                       f"skipinitialspace: '{csv_writer.dialect.skipinitialspace}', "
                                       f"strict: '{csv_writer.dialect.strict}' "
                                       )
        return csv_writer

    @staticmethod
    def write_csv_row(csv_writer, row):
        cleaned_row = etld_lib_config.remove_unicode_null_from_row(row)
        csv_writer.writerow(cleaned_row)

    @staticmethod
    def prepare_csv_row(headers, row, pragma, csv_max_field_size) -> list:
        row_fields = []
        for idx, fieldname in enumerate(headers):
            field_data = row[idx]
            if pragma[idx][2] == 'INTEGER':
                field_data = str(row[idx]).strip()
                if not str(row[idx]).isnumeric():
                    field_data = '0'
            else:
                #field_data = etld_lib_functions.remove_non_printable_except_tab_and_newline(str(field_data))
                field_data = etld_lib_config.remove_null_soh_cr_and_display_utf8(field_column_type='STRING',field_data=str(field_data),field_name_tmp=fieldname)
                if 'dns' in str(fieldname).lower():
                    field_data = str(field_data).replace('\n', '')
                # DEBUG ROUTINES FOR CHARACTERS
                #non_printable_character_list = etld_lib_functions.find_non_printable_ascii_characters(str(field_data))
                #non_printable_character_list = etld_lib_functions.find_non_printable_utf8_hex(str(field_data))
                unicode_character_list = etld_lib_functions.find_unique_unicode_characters_with_description(str(field_data))
                if len(unicode_character_list) > 0 and etld_lib_config.csv_distribution_display_utf8 is True:
                    etld_lib_functions.logger.info(f"Unicode characters in fieldname: {fieldname} - {unicode_character_list}")

            row_fields.append(f"{str(field_data)[0:int(csv_max_field_size)]}")
        return row_fields


def get_target_temp_csv_file_name(batch_date, batch_number, table_name, csv_file_open_method=open):
    batch_date = str(batch_date).replace(' ', 'T') + 'Z'
    table_name_utc_run_datetime = f"_utc_run_datetime_{batch_date}"
    table_name_batch_number = '_batch_000000'
    if '_batch_' in batch_number:
        table_name_batch_number = f'{batch_number}'
    elif batch_number.startswith('batch_'):
        table_name_batch_number = f'_{batch_number}'
    elif 'batch' not in batch_number:
        table_name_batch_number = f'_batch_{batch_number}'

    # 'Q_Host_List_Detection_HOSTS_utc_run_datetime_2022-11-16T17:31:11Z_batch_000001'
    target_csv_file_name = f"{table_name}{table_name_utc_run_datetime}{table_name_batch_number}"
    if csv_file_open_method == open:
        target_csv_file_name = f"{target_csv_file_name}.csv.tmp"
    elif csv_file_open_method == gzip.open:
        target_csv_file_name = f"{target_csv_file_name}.csv.gz.tmp"
    else:
        etld_lib_functions.logger.error(f"ERROR: Unknown csv_file_open_method: {csv_file_open_method}")
        etld_lib_functions.logger.error(f"ERROR: table_name: {table_name}, batch_date: {batch_date}, batch_number: {batch_number}")
        exit(1)

    return target_csv_file_name, table_name_utc_run_datetime, table_name_batch_number


def get_target_csv_file_name(batch_date, batch_number, table_name, csv_file_open_method=open):
    batch_date = str(batch_date).replace(' ', 'T') + 'Z'
    table_name_utc_run_datetime = f"_utc_run_datetime_{batch_date}"
    table_name_batch_number = '_batch_000000'
    if '_batch_' in batch_number:
        table_name_batch_number = f'{batch_number}'
    elif batch_number.startswith('batch_'):
        table_name_batch_number = f'_{batch_number}'
    elif 'batch' not in batch_number:
        table_name_batch_number = f'_batch_{batch_number}'

    # 'Q_Host_List_Detection_HOSTS_utc_run_datetime_2022-11-16T17:31:11Z_batch_000001'
    target_csv_file_name = f"{table_name}{table_name_utc_run_datetime}{table_name_batch_number}"
    if csv_file_open_method == open:
        target_csv_file_name = f"{target_csv_file_name}.csv"
    elif csv_file_open_method == gzip.open:
        target_csv_file_name = f"{target_csv_file_name}.csv.gz"
    else:
        etld_lib_functions.logger.error(f"ERROR: Unknown csv_file_open_method: {csv_file_open_method}")
        etld_lib_functions.logger.error(f"ERROR: table_name: {table_name}, batch_date: {batch_date}, batch_number: {batch_number}")
        exit(1)

    target_tmp_csv_file_name = target_csv_file_name + ".tmp"
    return target_csv_file_name, table_name_utc_run_datetime, table_name_batch_number, target_tmp_csv_file_name


def get_table_name_utc_run_datetime(sqlite_obj, etl_workflow_location_dict):
    sqlite_obj.reopen_connection_and_cursor_as_sqlite3_row_factory()
    database_table_names_list = sqlite_obj.get_all_table_names_from_database()
    table_name_utc_run_datetime = f"_utc_run_datetime_1970-01-01T00:00:00Z"
    table_name_batch_number = '_batch_000000'
    # CREATE FILENAME Q_TABLENAME_utc_run_datetime_2022-11-17T16:45:37Z_batch_000001.csv.gz
    for database_table_name in database_table_names_list:
        if str(database_table_name).endswith("_Status"):
            sqlite_obj.reopen_connection_and_cursor_as_sqlite3_row_factory()
            sqlite_obj.cursor.execute(f"select * from {database_table_name}")
            row = sqlite_obj.cursor.fetchone()
            if row is None:
                etld_lib_functions.logger.error(f"No Status Rows Found in Database: {etl_workflow_location_dict['sqlite_file']}")
                etld_lib_functions.logger.error(f"Please rerun to rebuild database: {etl_workflow_location_dict['sqlite_file']}")
                exit(1)
            if 'STATUS_DETAIL' in row.keys():
                json_string = row['STATUS_DETAIL']
                status_detail = json.loads(json_string)
                batch_date = str(status_detail['BATCH_DATE']).replace(' ', 'T') + 'Z'
                batch_number = 'batch_000000'
                dummy_value, \
                table_name_utc_run_datetime, \
                table_name_batch_number, tmp_csv_file_name = \
                    get_target_csv_file_name(batch_date=batch_date,
                                             batch_number=batch_number,
                                             table_name='Q_DUMMY',
                                             )
    return table_name_utc_run_datetime, table_name_batch_number


def get_csv_info_dict(batch_date, batch_number, table_name, csv_file_open_method=open, distribution_dir=None):
    csv_info_dict = {}
    batch_date = str(batch_date).replace(' ', 'T') + 'Z'
    table_name_utc_run_datetime = f"_utc_run_datetime_{batch_date}"
    table_name_batch_number = '_batch_000000'
    if '_batch_' in batch_number:
        table_name_batch_number = f'{batch_number}'
    elif batch_number.startswith('batch_'):
        table_name_batch_number = f'_{batch_number}'
    elif 'batch' not in batch_number:
        table_name_batch_number = f'_batch_{batch_number}'

    # 'Q_Host_List_Detection_HOSTS_utc_run_datetime_2022-11-16T17:31:11Z_batch_000001'
    target_csv_file_name = f"{table_name}{table_name_utc_run_datetime}{table_name_batch_number}"
    target_tmp_csv_file_name = ""
    if csv_file_open_method == open:
        target_csv_file_name = f"{target_csv_file_name}.csv"
        target_tmp_csv_file_name = target_csv_file_name + ".tmp"
    elif csv_file_open_method == gzip.open:
        target_csv_file_name = f"{target_csv_file_name}.csv.gz"
        target_tmp_csv_file_name = target_csv_file_name + ".tmp"
    else:
        etld_lib_functions.logger.error(f"ERROR: Unknown csv_file_open_method: {csv_file_open_method}")
        etld_lib_functions.logger.error(
            f"ERROR: table_name: {table_name}, batch_date: {batch_date}, batch_number: {batch_number}")
        exit(1)

    csv_info_dict['compression_method'] = csv_file_open_method
    csv_info_dict['target_csv_file_name'] = target_csv_file_name
    csv_info_dict['table_name_utc_run_datetime'] = table_name_utc_run_datetime
    csv_info_dict['table_name_batch_number'] = table_name_batch_number
    csv_info_dict['target_tmp_csv_file_name'] = target_tmp_csv_file_name
    csv_info_dict['distribution_dir'] = distribution_dir
    # FINAL CSV FILENAME Target
    csv_info_dict['target_csv_file_path'] = Path(distribution_dir, target_csv_file_name)
    csv_info_dict['target_tmp_csv_file_path'] = Path(distribution_dir, target_tmp_csv_file_name)

    csv_info_dict['csv_obj'] = \
        CsvDistribution(target_csv_path=csv_info_dict['target_tmp_csv_file_path'],
                        target_csv_data_directory=Path(csv_info_dict['distribution_dir']))

    return csv_info_dict


def get_one_etl_workflow_csv_data(etl_workflow, counter_obj_dict, exclude_table_names=None):

    if exclude_table_names is None:
        exclude_table_names = []

    final_exit_status = False
    target_csv_path_list = []
    #passed_all_tests = True
    #if etld_lib_config.test_system_do_not_test_intermediary_extracts_flag:
    #    passed_all_tests = True  # Skip during etl_test_system
    #else:
    #    passed_all_tests = \
    #        etld_lib_log_validation.validate_log_has_no_errors_prior_to_distribution(etl_workflow)

    etl_workflow_location_dict = \
        etld_lib_config.get_etl_workflow_data_location_dict(etl_workflow)

    #if passed_all_tests and len(etl_workflow_location_dict) > 0:
    if len(etl_workflow_location_dict) > 0:
        sqlite_obj = etld_lib_sqlite_tables.SqliteObj(sqlite_file=etl_workflow_location_dict['sqlite_file'])
        sqlite_obj.open_connection_and_cursor()

        all_database_table_names_list = sqlite_obj.get_all_table_names_from_database()
        database_table_names_list = []
        for database_table_name in all_database_table_names_list:
            if database_table_name in exclude_table_names:
                pass
            else:
                database_table_names_list.append(database_table_name)

        table_name_utc_run_datetime, table_name_batch_number = \
            get_table_name_utc_run_datetime(sqlite_obj, etl_workflow_location_dict)

        for database_table_name in database_table_names_list:
            target_csv_file_name = f"{database_table_name}{table_name_utc_run_datetime}{table_name_batch_number}"
            target_csv_path = Path(etl_workflow_location_dict['distribution_dir'], f"{target_csv_file_name}.csv")
            if etl_workflow_location_dict['open_file_compression_method'] == open:
                pass
            elif etl_workflow_location_dict['open_file_compression_method'] == gzip.open:
                target_csv_path = Path(f"{str(target_csv_path)}.gz.tmp")
            target_csv_path_list.append(target_csv_path)

            sqlite_obj.reopen_connection_and_cursor_as_sqlite3_row_factory()
            pragma = sqlite_obj.get_pragma(sqlite_obj.cursor, database_table_name)
            sqlite_obj.reopen_connection_and_cursor_as_sqlite3_row_factory()
            sqlite_obj.cursor.execute(f"select * from {database_table_name}")
            headers = prepare_headers_from_sqlite(cursor=sqlite_obj.cursor)


            csv_obj = CsvDistribution(
                target_csv_path=target_csv_path,
                target_csv_data_directory=etl_workflow_location_dict['distribution_dir']
            )
            csv_writer = csv_obj.get_csv_writer(
                csv_file=target_csv_path,
                csv_open_method=etl_workflow_location_dict['open_file_compression_method']
            )


            counter_obj_dict[database_table_name] = \
                etld_lib_functions.DisplayCounterToLog(
                    display_counter_at=etl_workflow_location_dict['csv_distribution_display_counter_at'],
                    logger_func=etld_lib_functions.logger.info,
                    display_counter_log_message=f"rows added to csv file from "
                                                f"table {database_table_name}")

            while True:
                row = sqlite_obj.cursor.fetchone()
                if row is None:
                    target_path = str(target_csv_path).replace('.tmp', '')
                    target_csv_path.rename(target_path)
                    break
                new_row = []
                for field in row:
                    new_row.append(field)
                row = csv_obj.prepare_csv_row(headers=headers,
                                              row=new_row,
                                              pragma=pragma,
                                              csv_max_field_size=etl_workflow_location_dict['csv_max_field_size'])
                csv_obj.write_csv_row(csv_writer, row)
                counter_obj_dict[database_table_name].update_counter_and_display_to_log()

        final_exit_status = True

        for database_table_name in database_table_names_list:
            counter_obj_dict[database_table_name].display_final_counter_to_log()

        log_csv_location_information(target_csv_path_list)

    return final_exit_status


def log_csv_location_information(target_csv_path_list: list):
    for target_csv_path in target_csv_path_list:
        etld_lib_functions.logger.info(f"File ready for distribution: {str(target_csv_path).replace('.tmp','')}")


def distribute_csv_data_for_one_workflow(distribution_csv_flag=False,
                                         etl_workflow='knowledgebase_etl_workflow',
                                         distribution_csv_flag_name='kb_distribution_csv_flag',
                                         exclude_table_names=None
                                         ):
    if exclude_table_names == None:
        exclude_table_names = []


    counter_obj_dict = {}
    if distribution_csv_flag:
        try:
            etl_workflow_location_dict = \
                etld_lib_config.get_etl_workflow_data_location_dict(etl_workflow)
            if len(etl_workflow_location_dict) > 0:
                get_one_etl_workflow_csv_data(
                    etl_workflow=etl_workflow,
                    counter_obj_dict=counter_obj_dict,
                    exclude_table_names=exclude_table_names)
            else:
                raise Exception(f"Could not retrieve etl_workflow csv data for: {etl_workflow}")
        except Exception as e:
            etld_lib_functions.logger.error(f"Distribution Program aborted, Exception: {e}")
            exit(1)
    else:
        etld_lib_functions.logger.info(f"No distribute_csv_data_for_one_workflow. {distribution_csv_flag_name} set to: {distribution_csv_flag} ")


def prepare_headers_from_sqlite(cursor):
    headers = [i[0] for i in cursor.description]
    return headers


def get_all_etl_workflow_csv_data():
    csv_obj_list = []
    counter_obj_dict = {}
    final_exit_status = 0
    for etl_workflow in etld_lib_config.etl_workflow_list:
        if get_one_etl_workflow_csv_data(
                etl_workflow=etl_workflow,
                counter_obj_dict=counter_obj_dict,
                exclude_table_names=None
        ):
            pass
        else:
            final_exit_status = 2

        if final_exit_status == 0:
            pass
        else:
            etld_lib_functions.logger.error(f"ERROR found in csv creation, exit status is {final_exit_status}")

    for table_name in counter_obj_dict:
        counter_obj_dict[table_name].display_final_counter_to_log()

    exit(final_exit_status)


def test_one_etl_workflow_csv_data(etl_workflow):
    csv_obj_list = []
    counter_obj_dict = {}
    final_exit_status = 0
    if etl_workflow in etld_lib_config.etl_workflow_list:
        if get_one_etl_workflow_csv_data(
                etl_workflow=etl_workflow,
                counter_obj_dict=counter_obj_dict,
                exclude_table_names=None
        ):
            pass
        else:
            final_exit_status = 2

        if final_exit_status == 0:
            pass
        else:
            etld_lib_functions.logger.error(f"ERROR found in csv creation, exit status is {final_exit_status}")
    else:
        etld_lib_functions.logger.error(f"Invalid workflow: {etl_workflow}")
        etld_lib_functions.logger.error(f"Valid Workflows are: {etld_lib_config.etl_workflow_list}")
        final_exit_status = 3

    for table_name in counter_obj_dict:
        counter_obj_dict[table_name].display_final_counter_to_log()

    exit(final_exit_status)


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='etld_lib_prepare_distribution')
    etld_lib_config.main()
    #get_all_etl_workflow_csv_data()
    if 'etl_workflow' in os.environ.keys():
        etl_workflow = os.environ.get('etl_workflow')
    else:
        etl_workflow = 'asset_inventory_etl_workflow' # Default

    test_one_etl_workflow_csv_data(etl_workflow)
