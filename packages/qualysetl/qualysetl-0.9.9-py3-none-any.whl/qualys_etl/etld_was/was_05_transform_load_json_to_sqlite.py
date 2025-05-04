#!/usr/bin/env python3
import json
from pathlib import Path
import re
from multiprocessing import Process, Queue
import time

from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_extract_transform_load
from qualys_etl.etld_lib import etld_lib_sqlite_tables


def insert_one_row_into_was_table(data_list_item, sqlite_obj, counter_objects, batch_name, batch_date, batch_number):

    if 'WebApp' in data_list_item:
        insert_one_row_into_table(
            sqlite_obj=sqlite_obj,
            table_name=etld_lib_config.was_webapp_table_name,
            table_fields=etld_lib_config.was_webapp_csv_columns(),
            table_field_types=etld_lib_config.was_webapp_csv_column_types(),
            batch_name=batch_name,
            batch_date=batch_date,
            batch_number=batch_number,
            item_dict=data_list_item['WebApp'],
            counter_obj=counter_objects['counter_obj_was_webapp'],
            counter_obj_duplicates=counter_objects['counter_obj_was_webapp_duplicates']
        )
    elif 'Finding' in data_list_item:
        insert_one_row_into_table(
            sqlite_obj=sqlite_obj,
            table_name=etld_lib_config.was_finding_table_name,
            table_fields=etld_lib_config.was_finding_csv_columns(),
            table_field_types=etld_lib_config.was_finding_csv_column_types(),
            batch_name=batch_name,
            batch_date=batch_date,
            batch_number=batch_number,
            item_dict=data_list_item['Finding'],
            counter_obj=counter_objects['counter_obj_was_finding'],
            counter_obj_duplicates=counter_objects['counter_obj_was_finding_duplicates']
        )
    elif 'Catalog' in data_list_item:
        insert_one_row_into_table(
            sqlite_obj=sqlite_obj,
            table_name=etld_lib_config.was_catalog_table_name,
            table_fields=etld_lib_config.was_catalog_csv_columns(),
            table_field_types=etld_lib_config.was_catalog_csv_column_types(),
            batch_name=batch_name,
            batch_date=batch_date,
            batch_number=batch_number,
            item_dict=data_list_item['Catalog'],
            counter_obj=counter_objects['counter_obj_was_catalog'],
            counter_obj_duplicates=counter_objects['counter_obj_was_catalog_duplicates']
        )


def prepare_was_finding_webapp_fields(item_dict):
    item_dict['webApp_id'] = 0
    item_dict['webApp_name'] = 'NONE'
    item_dict['webApp_url'] = 'NONE'
    item_dict['webApp_tags'] = '{"list": [], "count": 0}}'

    if 'webApp' in item_dict:
        if 'id' in item_dict['webApp']:
            item_dict['webApp_id'] = item_dict['webApp']['id']
        if 'tags' in item_dict['webApp']:
            item_dict['webApp_tags'] = item_dict['webApp']['tags']
        if 'url' in item_dict['webApp']:
            item_dict['webApp_url'] = item_dict['webApp']['url']
        if 'name' in item_dict['webApp']:
            item_dict['webApp_name'] = item_dict['webApp']['name']
        if 'group' in item_dict:
            item_dict['group_0'] = item_dict['group']
        if 'function' in item_dict:
            item_dict['function_0'] = item_dict['function']

    return item_dict


def insert_one_row_into_table(
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        table_name: str,
        table_fields: list,
        table_field_types: list,
        batch_name: str,
        batch_date: str,
        batch_number: str,
        item_dict: dict,
        counter_obj,
        counter_obj_duplicates):

    # def prepare_was_field(field_data, field_name_tmp):
    #     if field_data is None:
    #         field_data = ""
    #     elif 'Date' in field_name_tmp:
    #         field_data = field_data.replace("T", " ").replace("Z", "")
    #         field_data = re.sub("\\..*$", "", field_data)
    #     elif 'lastBoot' in field_name_tmp:
    #         field_data = field_data.replace("T", " ").replace("Z", "")
    #         field_data = re.sub("\\..*$", "", field_data)
    #     elif isinstance(field_data, int):
    #         field_data = str(field_data)
    #     elif not isinstance(field_data, str):
    #         field_data = json.dumps(field_data)
    #
    #     return field_data

    # if Finding.webApp (webApp)
    # flatten webApp data and reinsert into item_dict?
    if 'webApp' in item_dict:
        item_dict = prepare_was_finding_webapp_fields(item_dict)

    row_in_sqlite_form = sqlite_obj.prepare_database_row_was(
        item_dict=item_dict,
        csv_columns=table_fields,
        csv_column_types=table_field_types,
        batch_name=batch_name,
        batch_date=batch_date,
        batch_number=batch_number
    )

    # for field_name in table_fields:  # Iterate through expected columns (contract)
    #     if field_name in item_dict.keys():  # Iterate through columns found in dictionary
    #         item_dict[field_name] = \
    #             prepare_was_field(item_dict[field_name], field_name)
    #         row_in_sqlite_form.append(item_dict[field_name])
    #     else:
    #         row_in_sqlite_form.append("")  # Ensure blank is added to each required empty field

    result = sqlite_obj.insert_unique_row_ignore_duplicates(table_name, row_in_sqlite_form)
    if result is True:
        counter_obj.update_counter_and_display_to_log()
    else:
        counter_obj_duplicates.update_counter_and_display_to_log()


def drop_and_create_all_tables(sqlite_obj):
    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.was_status_table_name,
        csv_columns=etld_lib_config.status_table_csv_columns(),
        csv_column_types=etld_lib_config.status_table_csv_column_types(),
        key='STATUS_NAME')

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.was_webapp_table_name,
        csv_columns=etld_lib_config.was_webapp_csv_columns(),
        csv_column_types=etld_lib_config.was_webapp_csv_column_types(),
        key='id')

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.was_catalog_table_name,
        csv_columns=etld_lib_config.was_catalog_csv_columns(),
        csv_column_types=etld_lib_config.was_catalog_csv_column_types(),
        key='id')

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.was_finding_table_name,
        csv_columns=etld_lib_config.was_finding_csv_columns(),
        csv_column_types=etld_lib_config.was_finding_csv_column_types(),
        key='id')

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.was_q_knowledgebase_in_was_finding_table,
        csv_columns=etld_lib_config.kb_csv_columns(),
        csv_column_types=etld_lib_config.kb_csv_column_types(),
        key='QID')


def create_counter_objects(database_type='sqlite'):

    counter_obj_was_webapp = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=100,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to {database_type} "
                                    f"table {etld_lib_config.was_webapp_table_name}")

    counter_obj_was_catalog = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=100,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to {database_type} "
                                    f"table {etld_lib_config.was_catalog_table_name}")

    counter_obj_was_finding = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to {database_type} "
                                    f"table {etld_lib_config.was_finding_table_name}")

    counter_obj_was_webapp_duplicates = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=100,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"duplicate rows bypassed, not written to {database_type} "
                                    f"table {etld_lib_config.was_webapp_table_name}")

    counter_obj_was_catalog_duplicates = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=100,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"duplicate rows bypassed, not written to {database_type} "
                                    f"table {etld_lib_config.was_catalog_table_name}")

    counter_obj_was_finding_duplicates = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"duplicate rows bypassed, not written to {database_type} "
                                    f"table {etld_lib_config.was_finding_table_name}")

    counter_objects = {'counter_obj_was_webapp': counter_obj_was_webapp,
                       'counter_obj_was_finding': counter_obj_was_finding,
                       'counter_obj_was_catalog': counter_obj_was_catalog,
                       'counter_obj_was_webapp_duplicates': counter_obj_was_webapp_duplicates,
                       'counter_obj_was_catalog_duplicates': counter_obj_was_catalog_duplicates,
                       'counter_obj_was_finding_duplicates': counter_obj_was_finding_duplicates}

    return counter_objects


# def transform_and_load_queue_of_json_files_into_sqlite(queue_of_json_files,
#                                                        table_name,
#                                                        table_columns,
#                                                        table_column_types,
#                                                        table_primary_keys):
#     file_path = "EXCEPTION"
#     try:
#         sqlite_was = etld_lib_sqlite_tables.SqliteObj(etld_lib_config.was_sqlite_file)
#         drop_and_create_all_tables(sqlite_was)
#         counter_objects = create_counter_objects()
#         while True:
#             time.sleep(2)
#             file_path = queue_of_json_files.get()
#             if file_path == 'BEGIN':
#                 etld_lib_functions.logger.info(f"Found BEGIN of Queue.")
#                 break
#
#         while True:
#             time.sleep(2)
#             file_path = queue_of_json_files.get()
#             if file_path == 'END':
#                 etld_lib_functions.logger.info(f"Found END of Queue.")
#                 break
#
#             with etld_lib_config.was_open_file_compression_method(str(file_path), "rt", encoding='utf-8') \
#                     as read_file:
#                 batch_name = etld_lib_extract_transform_load.get_batch_name_from_filename(file_name=file_path)
#                 batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(file_name=file_path)
#                 batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(file_name=file_path)
#                 etld_lib_functions.logger.info(f"Received batch file from multiprocessing Queue: {batch_name}")
#
#                 status_name, status_detail_dict, status_count = \
#                     sqlite_was.update_status_table(
#                         batch_date=batch_date, batch_number=batch_number,
#                         total_rows_added_to_database=counter_objects['counter_obj_was'].get_counter(),
#                         etl_workflow_status_table_name=etld_lib_config.was_status_table_name,
#                         status_table_columns=etld_lib_config.status_table_csv_columns(),
#                         status_table_column_types=etld_lib_config.status_table_csv_column_types(),
#                         status_name_column='ASSET_INVENTORY_LOAD_STATUS', status_column='begin')
#
#                 all_items = json.load(read_file)
#                 for item in all_items['assetListData']['asset']:
#                     insert_one_asset_into_multiple_tables(item, sqlite_was, counter_objects)
#                 sqlite_was.commit_changes()
#
#
#                 status_name, status_detail_dict, status_count = \
#                     sqlite_was.update_status_table(
#                         batch_date=batch_date, batch_number=batch_number,
#                         total_rows_added_to_database=counter_objects['counter_obj_was'].get_counter(),
#                         etl_workflow_status_table_name=etld_lib_config.was_status_table_name,
#                         status_table_columns=etld_lib_config.status_table_csv_columns(),
#                         status_table_column_types=etld_lib_config.status_table_csv_column_types(),
#                         status_name_column='ASSET_INVENTORY_LOAD_STATUS', status_column='end')
#
#                 etld_lib_functions.logger.info(
#                     f"Committed batch file from multiprocessing Queue into Database: {batch_name}")
#
#         etld_lib_functions.logger.info(f"Completed processing Queue of files")
#
#         status_name, status_detail_dict, status_count = \
#             sqlite_was.update_status_table(
#                 batch_date=batch_date, batch_number=batch_number,
#                 total_rows_added_to_database=counter_objects['counter_obj_was'].get_counter(),
#                 etl_workflow_status_table_name=etld_lib_config.was_status_table_name,
#                 status_table_columns=etld_lib_config.status_table_csv_columns(),
#                 status_table_column_types=etld_lib_config.status_table_csv_column_types(),
#                 status_name_column='ASSET_INVENTORY_LOAD_STATUS', status_column='final')
#
#         sqlite_was.commit_changes()
#         sqlite_was.close_connection()
#         counter_objects['counter_obj_was_duplicates'].display_final_counter_to_log()
#         counter_objects['counter_obj_was'].display_final_counter_to_log()
#         counter_objects['counter_obj_software_os'].display_final_counter_to_log()
#         counter_objects['counter_obj_software_assetid'].display_final_counter_to_log()
#         end_msg_was_to_sqlite()
#
#     except Exception as e:
#         etld_lib_functions.logger.error(f"Exception: {e}")
#         etld_lib_functions.logger.error(f"Potential JSON File corruption detected: {file_path}")
#         exit(1)
#

def end_was_05_transform_load():
    etld_lib_functions.logger.info(f"end")


def begin_was_05_transform_load():
    etld_lib_functions.logger.info("start")


def attach_database(
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj, table_name, database_as_name, database_file):
    sqlite_obj.attach_database_to_connection(database_as_name=database_as_name,
                                             database_sqlite_file=database_file)
    table_name = f"{database_as_name}.{table_name}"
    table_columns = sqlite_obj.get_table_columns(table_name=table_name)
    etld_lib_functions.logger.info(f"Found Table {table_name} columns: {table_columns}")
    return table_name, table_columns


def copy_database_table(
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj, table_name, new_table_name, where_clause=""):
    try:
        etld_lib_functions.logger.info(f"Begin creating {new_table_name} from {table_name}")
        #        etl_workflow_sqlite_obj.cursor.execute(f"DROP TABLE IF EXISTS {new_table_name}")
        #        etl_workflow_sqlite_obj.cursor.execute(f"CREATE TABLE {new_table_name} AS SELECT * FROM {table_name} where 1=0")
        sqlite_obj.cursor.execute(f"INSERT INTO {new_table_name} SELECT * FROM {table_name} {where_clause}")
        etld_lib_functions.logger.info(f"End   creating {new_table_name} from {table_name}")
    except Exception as e:
        etld_lib_functions.logger.error(f"Error creating table {new_table_name} from {table_name}")
        etld_lib_functions.logger.error(f"Exception is: {e}")
        exit(1)


def create_kb_table_in_was_database(sqlite_obj: etld_lib_sqlite_tables.SqliteObj):
    etld_lib_functions.logger.info(f"Attaching database: {etld_lib_config.kb_table_name}")
    kb_table_name, kb_table_columns = \
        attach_database(sqlite_obj=sqlite_obj,
                        table_name="Q_KnowledgeBase",
                        database_as_name="K1",
                        database_file=etld_lib_config.kb_sqlite_file)

    etld_lib_functions.logger.info(f"Copying table: {kb_table_name}")
    where_clause = f"where {kb_table_name}.QID in (select distinct(qid) from Q_Was_Finding)"

    copy_database_table(sqlite_obj=sqlite_obj, table_name=kb_table_name,
                        new_table_name=etld_lib_config.was_q_knowledgebase_in_was_finding_table,
                        where_clause=where_clause)
    etld_lib_functions.logger.info(f"Commit copy of table: {kb_table_name}")
    sqlite_obj.commit_changes()


def transform_and_load_all_json_files_into_sqlite(dir_file_search_blob=None):
    json_file = "EXCEPTION"
    begin_was_05_transform_load()
    try:
        sqlite_was = etld_lib_sqlite_tables.SqliteObj(etld_lib_config.was_sqlite_file)
        drop_and_create_all_tables(sqlite_was)
        counter_objects = create_counter_objects()
        json_file_list = sorted(Path(etld_lib_config.was_extract_dir).
                                glob(etld_lib_config.was_extract_dir_file_search_blob_webapp_detail))
        json_file_list = json_file_list + sorted(Path(etld_lib_config.was_extract_dir).
                                                 glob(etld_lib_config.was_extract_dir_file_search_blob_finding_detail))
        json_file_list = json_file_list + sorted(Path(etld_lib_config.was_extract_dir).
                                                 glob(etld_lib_config.was_extract_dir_file_search_blob_catalog))

        for json_file in json_file_list:
            with etld_lib_config.was_open_file_compression_method(str(json_file), "rt", encoding='utf-8') \
                    as read_file:

                batch_name = etld_lib_extract_transform_load.get_batch_name_from_filename(file_name=json_file)
                batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(file_name=json_file)
                batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(file_name=json_file)
                etld_lib_functions.logger.info(f"Received batch file from directory: {batch_name}")
                status_table_columns = etld_lib_config.status_table_csv_columns()
                status_table_column_types = etld_lib_config.status_table_csv_column_types()

                if json_file.name.__contains__("was_webapp_detail_utc"):
                    total_rows_added_to_database = counter_objects['counter_obj_was_webapp'].get_counter()
                    status_name_column = etld_lib_config.was_webapp_table_name
                    counter_objects['counter_obj_was_webapp'].update_batch_info(
                        batch_name=batch_name,
                        batch_number=batch_number,
                        batch_date=batch_date,
                        status_table_name=etld_lib_config.was_status_table_name,
                        status_name_column=status_name_column)
                elif json_file.name.__contains__("was_finding_detail_utc"):
                    total_rows_added_to_database = counter_objects['counter_obj_was_finding'].get_counter()
                    status_name_column = etld_lib_config.was_finding_table_name
                    counter_objects['counter_obj_was_finding'].update_batch_info(
                        batch_name=batch_name,
                        batch_number=batch_number,
                        batch_date=batch_date,
                        status_table_name=etld_lib_config.was_status_table_name,
                        status_name_column=status_name_column)
                elif json_file.name.__contains__("was_catalog_utc"):
                    total_rows_added_to_database = counter_objects['counter_obj_was_catalog'].get_counter()
                    status_name_column = etld_lib_config.was_catalog_table_name
                    counter_objects['counter_obj_was_catalog'].update_batch_info(
                        batch_name=batch_name,
                        batch_number=batch_number,
                        batch_date=batch_date,
                        status_table_name=etld_lib_config.was_status_table_name,
                        status_name_column=status_name_column)
                else:
                    # skip all other files
                    continue

                sqlite_was.update_status_table(
                        batch_date=batch_date,
                        batch_number=batch_number,
                        total_rows_added_to_database=total_rows_added_to_database,
                        status_table_name=etld_lib_config.was_status_table_name,
                        status_table_columns=etld_lib_config.status_table_csv_columns(),
                        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                        status_name_column=status_name_column,
                        status_column='begin')

                json_data = json.load(read_file)

                json_success_found = False
                if 'ServiceResponse' in json_data:
                    if 'responseCode' in json_data['ServiceResponse']:
                        responseCode = json_data['ServiceResponse']['responseCode']
                        if 'success' == str(responseCode).lower():
                            json_success_found = True

                if json_success_found:
                    pass
                else:
                    etld_lib_functions.logger.error(
                        f"C1 - Found invalid batch json with no responseCode SUCCESS: {status_name_column} - {batch_name}")
                    json_data_string = str(json.dumps(json_data)).replace('\n', ' ').replace('\r', ' ')
                    etld_lib_functions.logger.error(f"JSON DATA: {json_data_string}")
                    etld_lib_functions.logger.error(f"json_file: {json_file}")
                    exit(1)

                if 'data' in json_data['ServiceResponse']:
                    for data_list_item in json_data['ServiceResponse']['data']:
                        insert_one_row_into_was_table(data_list_item, sqlite_was, counter_objects, batch_name, batch_date, batch_number)
                    sqlite_was.commit_changes()
                    etld_lib_functions.logger.info(
                        f"Added batch file from directory into Database: {status_name_column} - {batch_name}")

                    sqlite_was.update_status_table(
                            batch_date=batch_date,
                            batch_number=batch_number,
                            total_rows_added_to_database=total_rows_added_to_database,
                            status_table_name=etld_lib_config.was_status_table_name,
                            status_table_columns=etld_lib_config.status_table_csv_columns(),
                            status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                            status_name_column=status_name_column,
                            status_column='end')
                elif 'success' in str(json_data['ServiceResponse']['responseCode']).lower():
                    etld_lib_functions.logger.info(
                        f"Skipping, No Data in batch file from directory into "
                        f"Database: {status_name_column} - {batch_name}")
                else:
                    etld_lib_functions.logger.error(
                        f"C2 - Found invalid batch json with no responseCode SUCCESS: {status_name_column} - {batch_name}")
                    json_data_string = str(json.dumps(json_data)).replace('\n', ' ').replace('\r', ' ')
                    etld_lib_functions.logger.error(f"JSON DATA: {json_data_string}")
                    etld_lib_functions.logger.error(f"json_file: {json_file}")
                    exit(1)

        create_kb_table_in_was_database(sqlite_obj=sqlite_was)
        sqlite_was.update_status_table(
                batch_date=counter_objects['counter_obj_was_webapp'].get_batch_date(),
                batch_number=counter_objects['counter_obj_was_webapp'].get_batch_number(),
                total_rows_added_to_database=counter_objects['counter_obj_was_webapp'].get_counter(),
                status_table_name=etld_lib_config.was_status_table_name,
                status_table_columns=etld_lib_config.status_table_csv_columns(),
                status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                status_name_column=counter_objects['counter_obj_was_webapp'].get_status_name_column(),
                status_column='final')
        sqlite_was.update_status_table(
                batch_date=counter_objects['counter_obj_was_finding'].get_batch_date(),
                batch_number=counter_objects['counter_obj_was_finding'].get_batch_number(),
                total_rows_added_to_database=counter_objects['counter_obj_was_finding'].get_counter(),
                status_table_name=etld_lib_config.was_status_table_name,
                status_table_columns=etld_lib_config.status_table_csv_columns(),
                status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                status_name_column=counter_objects['counter_obj_was_finding'].get_status_name_column(),
                status_column='final')
        sqlite_was.update_status_table(
            batch_date=counter_objects['counter_obj_was_catalog'].get_batch_date(),
            batch_number=counter_objects['counter_obj_was_catalog'].get_batch_number(),
            total_rows_added_to_database=counter_objects['counter_obj_was_catalog'].get_counter(),
            status_table_name=etld_lib_config.was_status_table_name,
            status_table_columns=etld_lib_config.status_table_csv_columns(),
            status_table_column_types=etld_lib_config.status_table_csv_column_types(),
            status_name_column=counter_objects['counter_obj_was_catalog'].get_status_name_column(),
            status_column='final')

        sqlite_was.update_status_table(
            batch_date=counter_objects['counter_obj_was_webapp'].get_batch_date(),
            batch_number=0,
            total_rows_added_to_database=0,
            status_table_name=etld_lib_config.was_status_table_name,
            status_table_columns=etld_lib_config.status_table_csv_columns(),
            status_table_column_types=etld_lib_config.status_table_csv_column_types(),
            status_name_column='ALL_TABLES_LOADED_SUCCESSFULLY',
            status_column='final')

        etld_lib_functions.logger.info(f"Completed processing directory of files")
        sqlite_was.commit_changes()
        sqlite_was.validate_all_tables_loaded_successfully()
        sqlite_was.close_connection()
        counter_objects['counter_obj_was_webapp'].display_final_counter_to_log()
        counter_objects['counter_obj_was_catalog'].display_final_counter_to_log()
        counter_objects['counter_obj_was_finding'].display_final_counter_to_log()

    except Exception as e:
        etld_lib_functions.logger.error(f"JSON File Issue: {json_file}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)
    end_was_05_transform_load()


# def spawn_multiprocessing_queue_to_transform_and_load_json_files_into_sqlite(file_type='was_webapp'):
#     queue_of_file_paths = Queue()
#     queue_process = \
#         Process(target=transform_and_load_queue_of_json_files_into_sqlite, args=(queue_of_file_paths,))
#     queue_process.daemon = True
#     queue_process.start()
#     batch_queue_of_file_paths = queue_of_file_paths
#     batch_queue_process = queue_process
#
#     return batch_queue_of_file_paths, batch_queue_process


def main():
    transform_and_load_all_json_files_into_sqlite()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='was_05_transform_load_json_to_sqlite')
    etld_lib_config.main()
    etld_lib_config.was_json_to_sqlite_via_multiprocessing = False
    main()
