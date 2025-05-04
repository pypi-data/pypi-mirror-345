#!/usr/bin/env python3
import json
import ijson
from pathlib import Path
import re
import sys
from multiprocessing import Process, Queue
import time

from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_datetime
from qualys_etl.etld_lib import etld_lib_extract_transform_load
from qualys_etl.etld_lib import etld_lib_sqlite_tables
from qualys_etl.etld_lib import etld_lib_csv_distribution


def begin_pcrs_05_transform_load(message=""):
    etld_lib_functions.logger.info(f"start {message}")


def end_pcrs_05_transform_load(message=""):
    etld_lib_functions.logger.info(f"end  {message}")


def drop_and_create_all_tables(sqlite_obj):
    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.pcrs_policy_list_table_name,
        csv_columns=etld_lib_config.pcrs_policy_list_csv_columns(),
        csv_column_types=etld_lib_config.pcrs_policy_list_csv_column_types(),
        key=False
        )

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.pcrs_status_table_name,
        csv_columns=etld_lib_config.status_table_csv_columns(),
        csv_column_types=etld_lib_config.status_table_csv_column_types(),
        key='STATUS_NAME')

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.pcrs_hostids_table_name,
        csv_columns=etld_lib_config.pcrs_hostids_csv_columns(),
        csv_column_types=etld_lib_config.pcrs_hostids_csv_column_types(),
        key=False)

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.pcrs_postureinfo_table_name,
        csv_columns=etld_lib_config.pcrs_postureinfo_csv_columns(),
        csv_column_types=etld_lib_config.pcrs_postureinfo_csv_column_types(),
        key=False)

    if etld_lib_config.pcrs_postureinfo_schema_normalization_flag == True:
        sqlite_obj.drop_and_recreate_table(
            table_name=etld_lib_config.pcrs_postureinfo_controls_table_name,
            csv_columns=etld_lib_config.pcrs_postureinfo_controls_csv_columns(),
            csv_column_types=etld_lib_config.pcrs_postureinfo_controls_csv_column_types(),
            key=False)


def create_counter_objects(database_type='sqlite'):
    counter_obj_pcrs_policy_list = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=50,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to {database_type} "
                                    f"table {etld_lib_config.pcrs_policy_list_table_name}")

    counter_obj_pcrs_hostids = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=1000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to {database_type} "
                                    f"table {etld_lib_config.pcrs_hostids_table_name}")

    counter_obj_pcrs_postureinfo = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=50000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to {database_type} "
                                    f"table {etld_lib_config.pcrs_postureinfo_table_name}")

    counter_obj_pcrs_postureinfo_controls = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=1000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to {database_type} "
                                    f"table {etld_lib_config.pcrs_postureinfo_controls_table_name}")

    counter_objects = {'counter_obj_pcrs_policy_list': counter_obj_pcrs_policy_list,
                       'counter_obj_pcrs_hostids': counter_obj_pcrs_hostids,
                       'counter_obj_pcrs_postureinfo': counter_obj_pcrs_postureinfo,
                       'counter_obj_pcrs_postureinfo_controls': counter_obj_pcrs_postureinfo_controls }

    return counter_objects


def load_one_pcrs_policy_list_file_into_sqlite(
        json_file, pcrs_data, sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        counter_objects, table_fields, table_field_types,
):
    with etld_lib_config.pcrs_open_file_compression_method(str(json_file), "rt", encoding='utf-8') \
            as read_file:
        pcrs_data = json.load(read_file)

    etld_lib_functions.logger.info(f"load_one_pcrs_policy_list_file_into_sqlite: {str(pcrs_data)[0:50]}")
    batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(json_file)
    batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(json_file)
    counter_objects.set_batch_date(batch_date)

    if 'subscriptionId' in pcrs_data.keys() and 'policyList' in pcrs_data.keys():
        subscription_id = pcrs_data['subscriptionId']
        sqlite_obj.update_status_table(
            batch_date=batch_date, batch_number=batch_number,
            total_rows_added_to_database=counter_objects.get_counter(),
            status_table_name=etld_lib_config.pcrs_status_table_name,
            status_table_columns=etld_lib_config.status_table_csv_columns(),
            status_table_column_types=etld_lib_config.status_table_csv_column_types(),
            status_name_column=etld_lib_config.pcrs_policy_list_table_name, status_column='begin')

        for policy in pcrs_data['policyList']:
            row_dict = policy
            row_dict['subscriptionId'] = subscription_id
            row_in_sqlite_form = sqlite_obj.prepare_database_row_pcrs(
                item_dict=row_dict,
                csv_columns=table_fields,
                csv_column_types=table_field_types,
                batch_name="",
                batch_date=batch_date,
                batch_number=batch_number)

            result = sqlite_obj.insert_unique_row_ignore_duplicates(
                etld_lib_config.pcrs_policy_list_table_name,
                row_in_sqlite_form)

            if result == True:
                counter_objects.update_counter_and_display_to_log()
            if result ==  'duplicate':
                pass
                # TODO add some logic to deal with edge case

        sqlite_obj.commit_changes(message=f"{etld_lib_config.pcrs_policy_list_table_name} - ")

        sqlite_obj.update_status_table(
        batch_date=batch_date, batch_number=batch_number,
        total_rows_added_to_database=counter_objects.get_counter(),
        status_table_name=etld_lib_config.pcrs_status_table_name,
        status_table_columns=etld_lib_config.status_table_csv_columns(),
        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
        status_name_column=etld_lib_config.pcrs_policy_list_table_name, status_column='end')

        counter_objects.display_counter_to_log()

    else:
        etld_lib_functions.logger.error(f"Error finding policy in json file: {json_file}")
        etld_lib_functions.logger.error(f"Please review json file for data structure issues: {json_file}")
        exit(1)


def load_one_pcrs_hostids_file_into_sqlite(
        json_file, pcrs_data_dict, sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        counter_objects, table_fields, table_field_types,
):

    with etld_lib_config.pcrs_open_file_compression_method(str(json_file), "rt", encoding='utf-8') \
            as read_file:
        pcrs_data_dict = json.load(read_file)



    # etld_lib_functions.logger.info(f"load_one_pcrs_hostids_file_into_sqlite: {str(pcrs_data)[0:80]}")
    etld_lib_functions.logger.info(f"load_one_pcrs_hostids_file_into_sqlite: {json_file}")
    batch_number = etld_lib_extract_transform_load.get_batch_number_str_from_filename(json_file)
    batch_number = re.sub("batch_", "", batch_number)
    batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(json_file)
    counter_objects.set_batch_date(batch_date)

    subscription_id = ""
    pcrs_data = pcrs_data_dict[0]
    if 'subscriptionId' in pcrs_data.keys() and \
            'policyId' in pcrs_data.keys() and \
            'hostIds' in pcrs_data.keys():
        subscription_id = pcrs_data['subscriptionId']
        policy_id = pcrs_data['policyId']
        batch_number_policy_id = f"{batch_number}_policyId_{policy_id}"
        sqlite_obj.update_status_table(
            batch_date=batch_date,
            batch_number=batch_number_policy_id,
            total_rows_added_to_database=counter_objects.get_counter(),
            status_table_name=etld_lib_config.pcrs_status_table_name,
            status_table_columns=etld_lib_config.status_table_csv_columns(),
            status_table_column_types=etld_lib_config.status_table_csv_column_types(),
            status_name_column=etld_lib_config.pcrs_hostids_table_name,
            status_column='begin'
        )

        for host_id in pcrs_data['hostIds']:
            row_dict = {}
            row_dict['hostId'] = host_id
            row_dict['subscriptionId'] = subscription_id
            row_dict['policyId'] = policy_id
            row_in_sqlite_form = sqlite_obj.prepare_database_row_pcrs(
                item_dict=row_dict,
                csv_columns=table_fields,
                csv_column_types=table_field_types,
                batch_name="",
                batch_date=batch_date,
                batch_number=batch_number)

            result = sqlite_obj.insert_unique_row_ignore_duplicates(
                etld_lib_config.pcrs_hostids_table_name,
                row_in_sqlite_form)

            if result == True:
                counter_objects.update_counter_and_display_to_log()
            if result == 'duplicate':
                pass
                # TODO add some logic to deal with edge case

        sqlite_obj.commit_changes(message=f"{etld_lib_config.pcrs_hostids_table_name} - ")

        sqlite_obj.update_status_table(
            batch_date=batch_date,
            batch_number=batch_number_policy_id,
            total_rows_added_to_database=counter_objects.get_counter(),
            status_table_name=etld_lib_config.pcrs_status_table_name,
            status_table_columns=etld_lib_config.status_table_csv_columns(),
            status_table_column_types=etld_lib_config.status_table_csv_column_types(),
            status_name_column=etld_lib_config.pcrs_hostids_table_name,
            status_column='end'
        )
        counter_objects.display_counter_to_log()
    else:
        etld_lib_functions.logger.error(f"Error finding hostids in json file: {json_file}")
        etld_lib_functions.logger.error(f"Please review json file for data structure issues: {json_file}")
        exit(1)


def load_one_pcrs_postureinfo_file_into_sqlite(
        json_file, pcrs_data_dict, sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        counter_objects, counter_objects_controls,
        table_fields, table_field_types,
        table_fields_two, table_field_types_two,
):
    #etld_lib_functions.logger.info(f"load_one_pcrs_postureinfo_file_into_sqlite: {str(pcrs_data_dict)[0:80]}")
    etld_lib_functions.logger.info(f"load_one_pcrs_postureinfo_file_into_sqlite: {json_file}")
    batch_number = etld_lib_extract_transform_load.get_batch_number_str_from_filename(json_file)
    batch_slice = etld_lib_extract_transform_load.get_slice_from_filename(json_file)
    batch_number = re.sub("batch_", "", batch_number)
    batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(json_file)
    counter_objects.set_batch_date(batch_date)
    counter_objects_controls.set_batch_date(batch_date)

    batch_number_slice_number = f"{batch_number}_{batch_slice}"
    sqlite_obj.update_status_table(
        batch_date=batch_date,
        batch_number=batch_number_slice_number,
        total_rows_added_to_database=counter_objects.get_counter(),
        status_table_name=etld_lib_config.pcrs_status_table_name,
        status_table_columns=etld_lib_config.status_table_csv_columns(),
        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
        status_name_column=etld_lib_config.pcrs_postureinfo_table_name,
        status_column='begin'
    )

    if etld_lib_config.pcrs_postureinfo_schema_normalization_flag == True:
        sqlite_obj.update_status_table(
            batch_date=batch_date,
            batch_number=batch_number_slice_number,
            total_rows_added_to_database=counter_objects_controls.get_counter(),
            status_table_name=etld_lib_config.pcrs_status_table_name,
            status_table_columns=etld_lib_config.status_table_csv_columns(),
            status_table_column_types=etld_lib_config.status_table_csv_column_types(),
            status_name_column=etld_lib_config.pcrs_postureinfo_controls_table_name,
            status_column='begin'
        )

    total_records_committed = 0
    with etld_lib_config.pcrs_open_file_compression_method(str(json_file), "rt", encoding='utf-8') \
            as read_file:

        #for pcrs_data in json.load(read_file):
        records_ready_to_commit = 0
        for pcrs_data in ijson.items(read_file, 'item'):

            if etld_lib_config.pcrs_postureinfo_schema_normalization_flag == True:
                # Add table for policy, id, control information
                row_in_sqlite_form = sqlite_obj.prepare_database_row_pcrs(
                    item_dict=pcrs_data,
                    csv_columns=table_fields_two,
                    csv_column_types=table_field_types_two,
                    batch_name="",
                    batch_date=batch_date,
                    batch_number=batch_number_slice_number)

                key_exists = sqlite_obj.pcrs_check_if_key_exists_in_postureinfo_policy_control_technology(
                    policyid=row_in_sqlite_form[etld_lib_config.pcrs_postureinfo_controls_csv_columns_dict['policyId']],
                    controlid=row_in_sqlite_form[etld_lib_config.pcrs_postureinfo_controls_csv_columns_dict['controlId']],
                    technologyid=row_in_sqlite_form[etld_lib_config.pcrs_postureinfo_controls_csv_columns_dict['technologyId']],
                )
                if key_exists:
                    pass
                else:
                    result = sqlite_obj.insert_unique_row_ignore_duplicates(
                        etld_lib_config.pcrs_postureinfo_controls_table_name,
                        row_in_sqlite_form)
                    if result == True:
                        counter_objects_controls.update_counter_and_display_to_log()
                    # sqlite_obj.commit_changes(message=f"{etld_lib_config.pcrs_postureinfo_controls_table_name} - ")

            row_in_sqlite_form = sqlite_obj.prepare_database_row_pcrs(
                item_dict=pcrs_data,
                csv_columns=table_fields,
                csv_column_types=table_field_types,
                batch_name="",
                batch_date=batch_date,
                batch_number=batch_number_slice_number)

            result = sqlite_obj.insert_unique_row_ignore_duplicates(
                etld_lib_config.pcrs_postureinfo_table_name,
                row_in_sqlite_form)
            records_ready_to_commit = records_ready_to_commit + 1
            total_records_committed = total_records_committed + 1
            if records_ready_to_commit >= 5000:
                sqlite_obj.commit_changes(f"{etld_lib_config.pcrs_postureinfo_table_name} - {total_records_committed} records updated - ")
                records_ready_to_commit = 0

            if result == True:
                counter_objects.update_counter_and_display_to_log()
            if result == 'duplicate':
                pass
                # TODO add some logic to deal with edge case

    sqlite_obj.commit_changes(f"{etld_lib_config.pcrs_postureinfo_table_name} - {total_records_committed} records updated - ")

    sqlite_obj.update_status_table(
        batch_date=batch_date,
        batch_number=batch_number_slice_number,
        total_rows_added_to_database=counter_objects.get_counter(),
        status_table_name=etld_lib_config.pcrs_status_table_name,
        status_table_columns=etld_lib_config.status_table_csv_columns(),
        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
        status_name_column=etld_lib_config.pcrs_postureinfo_table_name,
        status_column='end'
    )

    if etld_lib_config.pcrs_postureinfo_schema_normalization_flag == True:
        sqlite_obj.update_status_table(
            batch_date=batch_date,
            batch_number=batch_number_slice_number,
            total_rows_added_to_database=counter_objects_controls.get_counter(),
            status_table_name=etld_lib_config.pcrs_status_table_name,
            status_table_columns=etld_lib_config.status_table_csv_columns(),
            status_table_column_types=etld_lib_config.status_table_csv_column_types(),
            status_name_column=etld_lib_config.pcrs_postureinfo_controls_table_name,
            status_column='end'
        )
    sqlite_obj.commit_changes(message=f"Completed {json_file} - ")
    counter_objects.display_counter_to_log()
    counter_objects_controls.display_counter_to_log()


def final_message(sqlite_obj, counter_objects):

    sqlite_obj.update_status_table(
        batch_date=counter_objects['counter_obj_pcrs_policy_list'].get_batch_date(),
        batch_number=0,
        total_rows_added_to_database=counter_objects['counter_obj_pcrs_policy_list'].get_counter(),
        status_table_name=etld_lib_config.pcrs_status_table_name,
        status_table_columns=etld_lib_config.status_table_csv_columns(),
        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
        status_name_column=etld_lib_config.pcrs_policy_list_table_name,
        status_column='final'
    )
    sqlite_obj.update_status_table(
        batch_date=counter_objects['counter_obj_pcrs_hostids'].get_batch_date(),
        batch_number=0,
        total_rows_added_to_database=counter_objects['counter_obj_pcrs_hostids'].get_counter(),
        status_table_name=etld_lib_config.pcrs_status_table_name,
        status_table_columns=etld_lib_config.status_table_csv_columns(),
        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
        status_name_column=etld_lib_config.pcrs_hostids_table_name,
        status_column='final'
    )
    sqlite_obj.update_status_table(
        batch_date=counter_objects['counter_obj_pcrs_postureinfo'].get_batch_date(),
        batch_number=0,
        total_rows_added_to_database=counter_objects['counter_obj_pcrs_postureinfo'].get_counter(),
        status_table_name=etld_lib_config.pcrs_status_table_name,
        status_table_columns=etld_lib_config.status_table_csv_columns(),
        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
        status_name_column=etld_lib_config.pcrs_postureinfo_table_name,
        status_column='final'
    )
    if etld_lib_config.pcrs_postureinfo_schema_normalization_flag == True:
        sqlite_obj.update_status_table(
            batch_date=counter_objects['counter_obj_pcrs_postureinfo_controls'].get_batch_date(),
            batch_number=0,
            total_rows_added_to_database=counter_objects['counter_obj_pcrs_postureinfo_controls'].get_counter(),
            status_table_name=etld_lib_config.pcrs_status_table_name,
            status_table_columns=etld_lib_config.status_table_csv_columns(),
            status_table_column_types=etld_lib_config.status_table_csv_column_types(),
            status_name_column=etld_lib_config.pcrs_postureinfo_controls_table_name,
            status_column='final'
        )

    sqlite_obj.update_status_table(
        batch_date=counter_objects['counter_obj_pcrs_policy_list'].get_batch_date(),
        batch_number=0,
        total_rows_added_to_database=0,
        status_table_name=etld_lib_config.pcrs_status_table_name,
        status_table_columns=etld_lib_config.status_table_csv_columns(),
        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
        status_name_column='ALL_TABLES_LOADED_SUCCESSFULLY',
        status_column='final')

    sqlite_obj.commit_changes(message="Final Commit")
    sqlite_obj.validate_all_tables_loaded_successfully()
    sqlite_obj.close_connection()
    counter_objects['counter_obj_pcrs_policy_list'].display_final_counter_to_log()
    counter_objects['counter_obj_pcrs_hostids'].display_final_counter_to_log()
    counter_objects['counter_obj_pcrs_postureinfo'].display_final_counter_to_log()
    if etld_lib_config.pcrs_postureinfo_schema_normalization_flag == True:
        counter_objects['counter_obj_pcrs_postureinfo_controls'].display_final_counter_to_log()


def insert_json_file_into_sqlite(json_file, pcrs_data, sqlite_pcrs, counter_objects):
    if Path(json_file).name.startswith('pcrs_policy_list'):
        table_fields = etld_lib_config.pcrs_policy_list_csv_columns()
        table_field_types = etld_lib_config.pcrs_policy_list_csv_column_types()
        load_one_pcrs_policy_list_file_into_sqlite(json_file,
                                                   pcrs_data,
                                                   sqlite_pcrs,
                                                   counter_objects['counter_obj_pcrs_policy_list'],
                                                   table_fields,
                                                   table_field_types)

    elif Path(json_file).name.startswith('pcrs_hostids'):
        table_fields = etld_lib_config.pcrs_hostids_csv_columns()
        table_field_types = etld_lib_config.pcrs_hostids_csv_column_types()
        load_one_pcrs_hostids_file_into_sqlite(json_file,
                                               pcrs_data,
                                               sqlite_pcrs,
                                               counter_objects['counter_obj_pcrs_hostids'],
                                               table_fields,
                                               table_field_types)

    elif Path(json_file).name.startswith('pcrs_postureinfo'):
        table_fields = etld_lib_config.pcrs_postureinfo_csv_columns()
        table_field_types = etld_lib_config.pcrs_postureinfo_csv_column_types()
        table_fields_two = etld_lib_config.pcrs_postureinfo_controls_csv_columns()
        table_field_types_two = etld_lib_config.pcrs_postureinfo_controls_csv_column_types()
        load_one_pcrs_postureinfo_file_into_sqlite(json_file,
                                                   pcrs_data,
                                                   sqlite_pcrs,
                                                   counter_objects['counter_obj_pcrs_postureinfo'],
                                                   counter_objects['counter_obj_pcrs_postureinfo_controls'],
                                                   table_fields,
                                                   table_field_types,
                                                   table_fields_two,
                                                   table_field_types_two)


def spawn_multiprocessing_queue_to_transform_and_load_json_files_into_sqlite():
    queue_of_file_paths = Queue()
    queue_process = \
        Process(target=transform_and_load_queue_of_json_files_into_sqlite, args=(queue_of_file_paths,))
    queue_process.daemon = True
    queue_process.start()
    batch_queue_of_file_paths = queue_of_file_paths
    batch_queue_process = queue_process

    return batch_queue_of_file_paths, batch_queue_process


def transform_and_load_queue_of_json_files_into_sqlite(queue_of_json_files,):
    begin_pcrs_05_transform_load(message="queue_of_json_files_through_multiprocesssing")
    json_file = "EXCEPTION"
    try:
        sqlite_pcrs = etld_lib_sqlite_tables.SqliteObj(etld_lib_config.pcrs_sqlite_file)
        drop_and_create_all_tables(sqlite_pcrs)
        counter_objects = create_counter_objects()
        while True:
            time.sleep(2)
            json_file = queue_of_json_files.get()
            if json_file == 'BEGIN':
                etld_lib_functions.logger.info(f"Found BEGIN of Queue.")
                break

        while True:
            time.sleep(2)
            json_file = queue_of_json_files.get()
            if json_file == 'END':
                etld_lib_functions.logger.info(f"Found END of Queue.")
                break

            batch_name = etld_lib_extract_transform_load.get_batch_number_str_from_filename_excluding_extension(
                file_name=json_file)
            etld_lib_functions.logger.info(f"Received batch file from multiprocessing Queue: {batch_name}")
            # with etld_lib_config.pcrs_open_file_compression_method(str(json_file), "rt", encoding='utf-8') \
            #         as read_file:
            #     pcrs_data = json.load(read_file)
            #     insert_json_file_into_sqlite(json_file, pcrs_data, sqlite_pcrs, counter_objects)
            pcrs_data = {}
            insert_json_file_into_sqlite(json_file, pcrs_data, sqlite_pcrs, counter_objects)

        time.sleep(5)
        final_message(sqlite_pcrs, counter_objects)
        etld_lib_functions.logger.info(f"Completed processing Queue of files")

    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Potential JSON File corruption detected: {json_file}")
        exit(1)
    end_pcrs_05_transform_load(message="queue_of_json_files_through_multiprocesssing")


def transform_and_load_all_json_files_into_sqlite():
    begin_pcrs_05_transform_load(message="directory_listing_of_json_files")
    json_file = "EXCEPTION"
    try:
        sqlite_pcrs = etld_lib_sqlite_tables.SqliteObj(etld_lib_config.pcrs_sqlite_file)
        drop_and_create_all_tables(sqlite_pcrs)
        counter_objects = create_counter_objects()

        json_file_list = \
            sorted(Path(etld_lib_config.pcrs_extract_dir).glob(
                etld_lib_config.pcrs_extract_dir_file_search_blob))
        for json_file in json_file_list:

            # with etld_lib_config.pcrs_open_file_compression_method(str(json_file), "rt", encoding='utf-8') \
            #         as read_file:
            #     pcrs_data = json.load(read_file)
            #     insert_json_file_into_sqlite(json_file, pcrs_data, sqlite_pcrs, counter_objects)
            pcrs_data = {}
            insert_json_file_into_sqlite(json_file, pcrs_data, sqlite_pcrs, counter_objects)

        final_message(sqlite_pcrs, counter_objects)
        etld_lib_functions.logger.info(f"Completed loading directory of files")


    except Exception as e:
        etld_lib_functions.logger.error(f"JSON File Issue: {json_file}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)
    end_pcrs_05_transform_load(message="directory_listing_of_json_files")


def main():
    transform_and_load_all_json_files_into_sqlite()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='pcrs_05_transform_load_json_to_sqlite')
    etld_lib_config.main()
    etld_lib_config.pcrs_json_to_sqlite_via_multiprocessing = False
    main()
