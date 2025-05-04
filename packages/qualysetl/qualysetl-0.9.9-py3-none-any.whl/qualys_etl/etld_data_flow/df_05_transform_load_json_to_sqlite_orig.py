#!/usr/bin/env python3
import json
from pathlib import Path
import re
from multiprocessing import Process, Queue
import time

from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_datetime
from qualys_etl.etld_lib import etld_lib_extract_transform_load
from qualys_etl.etld_lib import etld_lib_sqlite_tables
from qualys_etl.etld_lib import etld_lib_csv_distribution


def transform_epoch_dates(item):
    item['sensor_lastVMScanDate'] = ""
    item['sensor_lastComplianceScanDate'] = ""
    item['sensor_lastFullScanDate'] = ""
    item['agent_lastActivityDate'] = ""
    item['agent_lastCheckedInDate'] = ""
    item['agent_lastInventoryDate'] = ""
    item['inventory_createdDate'] = ""
    item['inventory_lastUpdatedDate'] = ""
    # Added 2022-12-16
    item['sensor_lastPcScanDateAgent'] = ""
    item['sensor_lastPcScanDateScanner'] = ""
    item['sensor_lastVmScanDateAgent'] = ""
    item['sensor_lastVmScanDateScanner'] = ""

    if 'sensor' in item.keys() and item['sensor'] is not None:
        if 'lastVMScan' in item['sensor']:
            item['sensor_lastVMScanDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastVMScan'])
        if 'lastComplianceScan' in item['sensor']:
            item['sensor_lastComplianceScanDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastComplianceScan'])
        if 'lastFullScan' in item['sensor']:
            item['sensor_lastFullScanDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastFullScan'])
        if 'lastPcScanDateAgent' in item['sensor']:
            item['sensor_lastPcScanDateAgent'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastPcScanDateAgent'])
        if 'lastPcScanDateScanner' in item['sensor']:
            item['sensor_lastPcScanDateScanner'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastPcScanDateScanner'])
        if 'lastVmScanDateAgent' in item['sensor']:
            item['sensor_lastVmScanDateAgent'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastVmScanDateAgent'])
        if 'lastVmScanDateScanner' in item['sensor']:
            item['sensor_lastVmScanDateScanner'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['sensor']['lastVmScanDateScanner'])

    if 'agent' in item.keys() and item['agent'] is not None:
        if 'lastActivity' in item['agent']:
            item['agent_lastActivityDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['agent']['lastActivity'])
        if 'lastCheckedIn' in item['agent']:
            item['agent_lastCheckedInDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['agent']['lastCheckedIn'])
        if 'lastInventory' in item['agent']:
            item['agent_lastInventoryDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['agent']['lastInventory'])

    if 'inventory' in item.keys() and item['inventory'] is not None:
        if 'created' in item['inventory']:
            item['inventory_createdDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['inventory']['created'])
        if 'lastUpdated' in item['inventory']:
            item['inventory_lastUpdatedDate'] = \
                etld_lib_datetime.get_datetime_str_from_epoch_milli_sec(item['inventory']['lastUpdated'])
    return item


def insert_one_row_into_table_q_pcrs(
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        table_name: str,
        table_fields: list,
        table_field_types: list,
        asset_item_dict: dict,
        counter_obj,
        counter_obj_duplicates,
        batch_date: str,
        batch_number: str,
        batch_name: str,
        csv_distribution_dict=None
):

    # def prepare_pcrs_field(field_data, field_name_tmp):
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
    #
    # row_in_sqlite_form = []
    # for field_name in table_fields:  # Iterate through expected columns (contract)
    #     if field_name in asset_item_dict.keys():  # Iterate through columns found in dictionary
    #         asset_item_dict[field_name] = \
    #             sqlite_obj.prepare_database_field_pcrs(asset_item_dict[field_name],
    #                                                               field_name,
    #                                                               csv_column_types=table_field_types)
    #         row_in_sqlite_form.append(asset_item_dict[field_name])
    #     else:
    #         row_in_sqlite_form.append("")  # Ensure blank is added to each required empty field

    row_in_sqlite_form = sqlite_obj.prepare_database_row_pcrs(
        item_dict=asset_item_dict,
        csv_columns=table_fields,
        csv_column_types=table_field_types,
        batch_name=batch_name,
        batch_date=batch_date,
        batch_number=batch_number)

    result = sqlite_obj.insert_unique_row_ignore_duplicates(table_name, row_in_sqlite_form)
    if result is True:
        counter_obj.update_counter_and_display_to_log()
        # WRITE CSV ROW
        if etld_lib_config.pcrs_distribution_csv_flag and csv_distribution_dict is not None:
            #
            # Write one row to Q_Asset_Inventory CSV File
            #
            qids_csv_obj: etld_lib_csv_distribution.CsvDistribution = \
                csv_distribution_dict['q_pcrs_csv_obj']
            qids_csv_obj.write_csv_row_to_file_handle(row_in_sqlite_form)
    else:
        counter_obj_duplicates.update_counter_and_display_to_log()


def insert_one_row_into_table_q_pcrs_software_assetid(
        asset_item_dict: dict,
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        counter_obj,
        batch_date: str,
        batch_number: str,
        batch_name: str
):

    if asset_item_dict['softwareListData'] is not None:
        for software_item in asset_item_dict['softwareListData']['software']:
            if 'fullName' in software_item:
                assetid = str(asset_item_dict['assetId'])
                fullname = software_item['fullName']
                row = {'assetId': assetid, 'fullName': fullname}
                sqlite_row = []
                for field in etld_lib_config.pcrs_software_assetid_csv_columns():
                    if field in row.keys():
                        sqlite_row.append(row[field])
                    else:
                        sqlite_row.append("")

                result = sqlite_obj.insert_unique_row_ignore_duplicates(
                    etld_lib_config.pcrs_table_name_software_assetid,
                    sqlite_row)
                if result is True:
                    counter_obj.update_counter_and_display_to_log()
                    # WRITE CSV ROW
                else:
                    pass
                    #etld_lib_functions.logger.info("found dups in software assetid")


def insert_one_row_into_table_q_pcrs_software_os_unique(
        asset_item_dict: dict,
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        counter_obj,
        batch_date: str,
        batch_number: str,
        batch_name: str,
):

    if asset_item_dict['softwareListData'] is not None:
        for software_item in asset_item_dict['softwareListData']['software']:
            if 'fullName' in software_item:
                fullname = str(software_item['fullName'])
                osname = ""
                isignored = ""
                ignoredreason = ""
                category = ""
                if 'operatingSystem' in asset_item_dict:
                    if 'osName' in asset_item_dict['operatingSystem']:
                        osname = str(asset_item_dict['operatingSystem']['osName'])
                if 'lifecycle' in software_item:
                    lifecycle = software_item['lifecycle']
                    if lifecycle is None:
                        lifecycle = {}
                else:
                    lifecycle = {}
                if 'isIgnored' in software_item:
                    isignored = str(software_item['isIgnored'])
                if 'ignoredReason' in software_item:
                    ignoredreason = str(software_item['ignoredReason'])
                if 'category' in software_item:
                    category = \
                        f"{software_item['category']} | {software_item['category']} | {software_item['category']}"

                row = {'fullName': fullname, 'osName': osname,
                       'isIgnored': isignored, 'ignoredReason': ignoredreason, 'category': category,
                       }
                row.update(lifecycle)
                sqlite_row = []
                for field in etld_lib_config.pcrs_software_os_unique_csv_columns():
                    if field in row.keys():
                        sqlite_row.append(row[field])
                    else:
                        sqlite_row.append("")

                result = sqlite_obj.insert_unique_row_ignore_duplicates(
                    etld_lib_config.pcrs_table_name_software_os_unique,
                    sqlite_row)
                if result is True:
                    counter_obj.update_counter_and_display_to_log()
                    # WRITE CSV ROW


def drop_and_create_all_tables(sqlite_obj):
    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.pcrs_table_name,
        csv_columns=etld_lib_config.pcrs_csv_columns(),
        csv_column_types=etld_lib_config.pcrs_csv_column_types(),
        key='assetId')

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.pcrs_status_table_name,
        csv_columns=etld_lib_config.status_table_csv_columns(),
        csv_column_types=etld_lib_config.status_table_csv_column_types(),
        key='STATUS_NAME')

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.pcrs_table_name_software_os_unique,
        csv_columns=etld_lib_config.pcrs_software_os_unique_csv_columns(),
        csv_column_types=etld_lib_config.pcrs_software_os_unique_csv_column_types(),
        key=['fullName', 'osName'])

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.pcrs_table_name_software_assetid,
        csv_columns=etld_lib_config.pcrs_software_assetid_csv_columns(),
        csv_column_types=etld_lib_config.pcrs_software_assetid_csv_column_types(),
        key=['assetId', 'fullName'])


def create_counter_objects(database_type='sqlite'):
    counter_obj_pcrs = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=25000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to {database_type} "
                                    f"table {etld_lib_config.pcrs_table_name}")
    counter_obj_pcrs_duplicates = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"duplicate rows bypassed, not written to {database_type} "
                                    f"table {etld_lib_config.pcrs_table_name}")
    counter_obj_software_os = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=25000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to {database_type} "
                                    f"table {etld_lib_config.pcrs_table_name_software_os_unique}")
    counter_obj_software_assetid = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=25000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to {database_type} "
                                    f"table {etld_lib_config.pcrs_table_name_software_assetid}")
    counter_objects = {'counter_obj_pcrs': counter_obj_pcrs,
                       'counter_obj_pcrs_duplicates': counter_obj_pcrs_duplicates,
                       'counter_obj_software_os': counter_obj_software_os,
                       'counter_obj_software_assetid': counter_obj_software_assetid}

    return counter_objects


def insert_one_asset_into_multiple_tables(asset_item, sqlite_obj, counter_objects, csv_distribution_dict=None,
                                          batch_date="", batch_number="", batch_name=""):
    item = transform_epoch_dates(asset_item)
    insert_one_row_into_table_q_pcrs_software_os_unique(
        asset_item_dict=item,
        sqlite_obj=sqlite_obj,
        counter_obj=counter_objects['counter_obj_software_os'],
        batch_date=batch_date,
        batch_number=batch_number,
        batch_name=batch_name
    )
    insert_one_row_into_table_q_pcrs_software_assetid(
        asset_item_dict=item,
        sqlite_obj=sqlite_obj,
        counter_obj=counter_objects['counter_obj_software_assetid'],
        batch_date=batch_date,
        batch_number=batch_number,
        batch_name=batch_name
    )
    insert_one_row_into_table_q_pcrs(
        sqlite_obj=sqlite_obj,
        table_name=etld_lib_config.pcrs_table_name,
        table_fields=etld_lib_config.pcrs_csv_columns(),
        table_field_types=etld_lib_config.pcrs_csv_column_types(),
        asset_item_dict=item,
        counter_obj=counter_objects['counter_obj_pcrs'],
        counter_obj_duplicates=counter_objects['counter_obj_pcrs_duplicates'],
        csv_distribution_dict=csv_distribution_dict,
        batch_date=batch_date,
        batch_number=batch_number,
        batch_name=batch_name
    )


def transform_and_load_queue_of_json_files_into_sqlite(queue_of_json_files,):
    begin_pcrs_05_transform_load(message="queue_of_json_files_through_multiprocesssing")
    file_path = "EXCEPTION"
    try:
        sqlite_pcrs = etld_lib_sqlite_tables.SqliteObj(etld_lib_config.pcrs_sqlite_file)
        drop_and_create_all_tables(sqlite_pcrs)
        counter_objects = create_counter_objects()
        while True:
            time.sleep(2)
            file_path = queue_of_json_files.get()
            if file_path == 'BEGIN':
                etld_lib_functions.logger.info(f"Found BEGIN of Queue.")
                break

        while True:
            time.sleep(2)
            file_path = queue_of_json_files.get()
            if file_path == 'END':
                etld_lib_functions.logger.info(f"Found END of Queue.")
                break

            with etld_lib_config.pcrs_open_file_compression_method(str(file_path), "rt", encoding='utf-8') \
                    as read_file:
                batch_name = etld_lib_extract_transform_load.get_batch_name_from_filename(file_name=file_path)
                batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(file_name=file_path)
                batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(file_name=file_path)
                etld_lib_functions.logger.info(f"Received batch file from multiprocessing Queue: {Path(file_path).name}")

                sqlite_pcrs.update_status_table(
                        batch_date=batch_date, batch_number=batch_number,
                        total_rows_added_to_database=counter_objects['counter_obj_pcrs'].get_counter(),
                        status_table_name=etld_lib_config.pcrs_status_table_name,
                        status_table_columns=etld_lib_config.status_table_csv_columns(),
                        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                        status_name_column=etld_lib_config.pcrs_table_name, status_column='begin')

                all_items = json.load(read_file)
                csv_distribution_dict = {}
                if etld_lib_config.host_list_detection_distribution_csv_flag:
                    q_pcrs_csv_info =  etld_lib_csv_distribution.get_csv_info_dict(
                        batch_date=batch_date,
                        batch_number=batch_number,
                        table_name=etld_lib_config.pcrs_table_name,
                        csv_file_open_method=etld_lib_config.pcrs_open_file_compression_method,
                        distribution_dir=etld_lib_config.pcrs_distribution_dir
                    )
                    with q_pcrs_csv_info['compression_method'](
                            q_pcrs_csv_info['target_tmp_csv_file_path'], 'wt', newline='') as \
                            q_pcrs_target_tmp_csv_file_handle:
                        q_pcrs_csv_info['csv_obj'].set_csv_writer_with_file_handle(
                            q_pcrs_target_tmp_csv_file_handle)
                        csv_distribution_dict['q_pcrs_csv_obj'] = q_pcrs_csv_info['csv_obj']
                        for item in all_items['assetListData']['asset']:
                            insert_one_asset_into_multiple_tables(
                                item, sqlite_pcrs, counter_objects,
                                csv_distribution_dict=csv_distribution_dict,
                                batch_date=batch_date, batch_number=batch_number, batch_name=batch_name
                            )
                    Path(q_pcrs_csv_info['target_tmp_csv_file_path']).\
                            rename(q_pcrs_csv_info['target_csv_file_path'])
                else:
                    for item in all_items['assetListData']['asset']:
                        insert_one_asset_into_multiple_tables(
                            item, sqlite_pcrs, counter_objects, csv_distribution_dict=None,
                            batch_date=batch_date, batch_number=batch_number, batch_name=batch_name
                        )

                sqlite_pcrs.commit_changes()

                sqlite_pcrs.update_status_table(
                        batch_date=batch_date, batch_number=batch_number,
                        total_rows_added_to_database=counter_objects['counter_obj_pcrs'].get_counter(),
                        status_table_name=etld_lib_config.pcrs_status_table_name,
                        status_table_columns=etld_lib_config.status_table_csv_columns(),
                        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                        status_name_column=etld_lib_config.pcrs_table_name, status_column='end')

                etld_lib_functions.logger.info(
                    f"Committed batch file from multiprocessing Queue into Database: {batch_name}")

        etld_lib_functions.logger.info(f"Completed processing Queue of files")

        sqlite_pcrs.update_status_table(
                batch_date=batch_date, batch_number=batch_number,
                total_rows_added_to_database=counter_objects['counter_obj_pcrs'].get_counter(),
                status_table_name=etld_lib_config.pcrs_status_table_name,
                status_table_columns=etld_lib_config.status_table_csv_columns(),
                status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                status_name_column=etld_lib_config.pcrs_table_name, status_column='final')

        sqlite_pcrs.update_status_table(
            batch_date=batch_date,
            batch_number=0,
            total_rows_added_to_database=0,
            status_table_name=etld_lib_config.pcrs_status_table_name,
            status_table_columns=etld_lib_config.status_table_csv_columns(),
            status_table_column_types=etld_lib_config.status_table_csv_column_types(),
            status_name_column='ALL_TABLES_LOADED_SUCCESSFULLY',
            status_column='final')

        sqlite_pcrs.commit_changes()
        sqlite_pcrs.close_connection()
        counter_objects['counter_obj_pcrs_duplicates'].display_final_counter_to_log()
        counter_objects['counter_obj_pcrs'].display_final_counter_to_log()
        counter_objects['counter_obj_software_os'].display_final_counter_to_log()
        counter_objects['counter_obj_software_assetid'].display_final_counter_to_log()

    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Potential JSON File corruption detected: {file_path}")
        exit(1)
    end_pcrs_05_transform_load(message="queue_of_json_files_through_multiprocesssing")


def begin_pcrs_05_transform_load(message=""):
    etld_lib_functions.logger.info(f"start {message}")


def end_pcrs_05_transform_load(message=""):
    etld_lib_functions.logger.info(f"end  {message}")


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
            with etld_lib_config.pcrs_open_file_compression_method(str(json_file), "rt", encoding='utf-8') \
                    as read_file:

                batch_name = etld_lib_extract_transform_load.get_batch_name_from_filename(file_name=json_file)
                batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(file_name=json_file)
                batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(file_name=json_file)
                etld_lib_functions.logger.info(f"Received batch file from directory: {batch_name}")

                sqlite_pcrs.update_status_table(
                        batch_date=batch_date, batch_number=batch_number,
                        total_rows_added_to_database=counter_objects['counter_obj_pcrs'].get_counter(),
                        status_table_name=etld_lib_config.pcrs_status_table_name,
                        status_table_columns=etld_lib_config.status_table_csv_columns(),
                        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                        status_name_column=etld_lib_config.pcrs_table_name, status_column='begin')

                all_items = json.load(read_file)
                # Open CSV File
                for item in all_items['assetListData']['asset']:
                    insert_one_asset_into_multiple_tables(
                        item,
                        sqlite_pcrs,
                        counter_objects,
                        csv_distribution_dict=None,
                        batch_date=batch_date,
                        batch_number=batch_number,
                        batch_name=batch_name
                    )

                etld_lib_functions.logger.info(
                    f"Added batch file from directory into Database: {batch_name}")

                sqlite_pcrs.update_status_table(
                        batch_date=batch_date, batch_number=batch_number,
                        total_rows_added_to_database=counter_objects['counter_obj_pcrs'].get_counter(),
                        status_table_name=etld_lib_config.pcrs_status_table_name,
                        status_table_columns=etld_lib_config.status_table_csv_columns(),
                        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                        status_name_column=etld_lib_config.pcrs_table_name, status_column='end')

        sqlite_pcrs.update_status_table(
                batch_date=batch_date, batch_number=batch_number,
                total_rows_added_to_database=counter_objects['counter_obj_pcrs'].get_counter(),
                status_table_name=etld_lib_config.pcrs_status_table_name,
                status_table_columns=etld_lib_config.status_table_csv_columns(),
                status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                status_name_column=etld_lib_config.pcrs_table_name, status_column='final')

        sqlite_pcrs.update_status_table(
            batch_date=batch_date,
            batch_number=0,
            total_rows_added_to_database=0,
            status_table_name=etld_lib_config.pcrs_status_table_name,
            status_table_columns=etld_lib_config.status_table_csv_columns(),
            status_table_column_types=etld_lib_config.status_table_csv_column_types(),
            status_name_column='ALL_TABLES_LOADED_SUCCESSFULLY',
            status_column='final')

        etld_lib_functions.logger.info(f"Completed processing directory of files")
        sqlite_pcrs.commit_changes()
        sqlite_pcrs.close_connection()
        counter_objects['counter_obj_pcrs_duplicates'].display_final_counter_to_log()
        counter_objects['counter_obj_pcrs'].display_final_counter_to_log()
        counter_objects['counter_obj_software_os'].display_final_counter_to_log()
        counter_objects['counter_obj_software_assetid'].display_final_counter_to_log()

    except Exception as e:
        etld_lib_functions.logger.error(f"JSON File Issue: {json_file}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)
    end_pcrs_05_transform_load(message="directory_listing_of_json_files")


def spawn_multiprocessing_queue_to_transform_and_load_json_files_into_sqlite():
    queue_of_file_paths = Queue()
    queue_process = \
        Process(target=transform_and_load_queue_of_json_files_into_sqlite, args=(queue_of_file_paths,))
    queue_process.daemon = True
    queue_process.start()
    batch_queue_of_file_paths = queue_of_file_paths
    batch_queue_process = queue_process

    return batch_queue_of_file_paths, batch_queue_process


def main():
    transform_and_load_all_json_files_into_sqlite()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='pcrs_05_transform_load_json_to_sqlite')
    etld_lib_config.main()
    etld_lib_config.pcrs_json_to_sqlite_via_multiprocessing = False
    main()
