#!/usr/bin/env python3
import json
import time
import multiprocessing
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_authentication_objects
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_datetime
from qualys_etl.etld_lib import etld_lib_extract_transform_load
from qualys_etl.etld_was import was_04_extract_from_qualys
import traceback


def begin_was_03_extract_controller():
    etld_lib_functions.logger.info(f"start")


def end_was_03_extract_controller():
    etld_lib_functions.logger.info(f"end")


def get_next_batch(json_file=None):
    try:
        was_batch_status = {}
        with etld_lib_config.was_open_file_compression_method(json_file, "rt", encoding='utf-8') as read_file:
            was_dict = json.load(read_file)
            was_sr_dict = {}

            if 'ServiceResponse' in was_dict.keys():
                was_sr_dict = was_dict['ServiceResponse']
            else:
                raise Exception(f"Cannot find ServiceResponse in json file: {json_file}")

            if 'SUCCESS' not in was_sr_dict['responseCode']:
                raise Exception(f"Failed Response Code in json file: {json_file}")

            if 'hasMoreRecords' not in was_sr_dict.keys():
                was_sr_dict['hasMoreRecords'] = 'false'

            if 'hasMoreRecords' in was_sr_dict.keys():
                if was_sr_dict['hasMoreRecords'] != 'true':
                    was_sr_dict['lastId'] = ""

            was_batch_status = {
                'responseCode': was_sr_dict['responseCode'],
                'count': was_sr_dict['count'],
                'hasMoreRecords': was_sr_dict['hasMoreRecords'],
                'lastId': was_sr_dict['lastId'],
            }

    except Exception as e:
        etld_lib_functions.logger.error(f"Error downloading records Exception: {e}")
        etld_lib_functions.logger.error(f"batch_status: {was_batch_status}")
        etld_lib_functions.logger.error(f"dict: {was_sr_dict}")
        etld_lib_functions.logger.error(f"file: {str(json_file)}")
        exit(1)

    return was_batch_status


def get_was_count(_: dict):
    api_call_name = _['api_call_name']
    was_extract_function_reference = _['was_extract_function_reference']
    utc_datetime = _['utc_datetime']
    cred_dict = _['cred_dict']
    dir_search_glob = _['dir_search_glob']
    # if 'last_id' in _.keys():
    #     last_id = _['last_id']
    # else:
    #     last_id = 0

    etld_lib_functions.logger.info(f"Begin {api_call_name}")
    qualys_headers_dict = {}

    etld_lib_config.remove_old_files(
        dir_path=etld_lib_config.was_extract_dir,
        dir_search_glob=dir_search_glob
    )

    file_info_dict = \
        etld_lib_config.prepare_extract_batch_file_name(
            next_batch_number_str='batch_000000',
            next_batch_date=utc_datetime,
            extract_dir=etld_lib_config.was_extract_dir,
            file_name_type=f"{api_call_name}",
            file_name_option="last_scan_date",
            file_name_option_date=etld_lib_config.was_webapp_last_scan_date,
            file_extension="json",
            compression_method=etld_lib_config.was_open_file_compression_method)

    was_extract_function_reference(
        batch_number_str=file_info_dict['next_batch_number_str'],
        qualys_headers_dict=qualys_headers_dict,
        cred_dict=cred_dict,
        file_info_dict=file_info_dict)

    etld_lib_functions.logger.info(f"End   {api_call_name}")


def get_was_data(_: dict):

    api_call_name = _['api_call_name']
    was_extract_function_reference = _['was_extract_function_reference']
    utc_datetime = _['utc_datetime']
    cred_dict = _['cred_dict']
    page_size = _['page_size']
    dir_search_glob = _['dir_search_glob']
    if 'last_id' in _.keys():
        last_id = _['last_id']
    else:
        last_id = 0

    etld_lib_config.remove_old_files(
        dir_path=etld_lib_config.was_extract_dir,
        dir_search_glob=dir_search_glob
    )

    batch_info = {'hasMoreRecords': 'true', 'lastId': last_id}
    has_more_records = 'true'
    batch_number = 0
    qualys_headers_dict = {}

    while has_more_records == 'true':
        batch_number = batch_number + 1
        batch_number_str = f'batch_{batch_number:06d}'

        # TODO currently was_webapp_last_scan_date is ignored, all apps are pulled.
        # TODO see etld_lib_config for details

        file_info_dict = \
            etld_lib_config.prepare_extract_batch_file_name(
                next_batch_number_str=batch_number_str,
                next_batch_date=utc_datetime,
                extract_dir=etld_lib_config.was_extract_dir,
                file_name_type=f"{api_call_name}",
                file_name_option="last_scan_date",
                file_name_option_date=etld_lib_config.was_webapp_last_scan_date,
                file_extension="json",
                compression_method=etld_lib_config.was_open_file_compression_method)

        was_extract_function_reference(
            last_id=str(batch_info['lastId']),
            batch_number_str=file_info_dict['next_batch_number_str'],
            qualys_headers_dict=qualys_headers_dict,
            cred_dict=cred_dict,
            file_info_dict=file_info_dict,
            page_size=page_size
        )

        batch_info = get_next_batch(json_file=file_info_dict['next_file_path'])
        has_more_records = str(batch_info['hasMoreRecords'])
        etld_lib_functions.logger.info(f"{batch_number_str} info: {batch_info}")

        has_more_records = test_system_option(
            file_path=file_info_dict['next_file_path'],
            has_more_records=has_more_records,
            number_of_files_to_extract=etld_lib_config.was_test_number_of_files_to_extract,
            test_system_flag=etld_lib_config.was_test_system_flag
        )


def test_system_option(file_path: Path, has_more_records, number_of_files_to_extract, test_system_flag):
    if test_system_flag is True:
        test_batch_number = \
            etld_lib_extract_transform_load.get_batch_number_from_filename(file_path)
        if int(test_batch_number) >= number_of_files_to_extract:
            has_more_records = '0'
    return has_more_records


def extract_was_api_data():
    begin_was_03_extract_controller()
    utc_datetime = etld_lib_datetime.get_utc_datetime_qualys_format()
    cred_dict = etld_lib_authentication_objects.qualys_authentication_obj.get_credentials_dict()
    etld_lib_config.remove_old_files(
        dir_path=etld_lib_config.was_extract_dir,
        dir_search_glob=etld_lib_config.was_extract_dir_file_search_blob,
        other_files_list=etld_lib_config.was_data_files
    )
    etld_lib_config.remove_old_files(
        dir_path=etld_lib_config.was_distribution_dir,
        dir_search_glob=etld_lib_config.was_distribution_dir_file_search_blob
    )

    was_count_webapp_arg_dict = {
        'api_call_name': 'was_count_webapp',
        'was_extract_function_reference': was_04_extract_from_qualys.was_webapp_extract_count,
        'utc_datetime': utc_datetime, 'cred_dict': cred_dict,
        'dir_search_glob': etld_lib_config.was_extract_dir_file_search_blob_webapp_count
    }
    was_count_webapp_proc = multiprocessing.Process(
        target=get_was_count,
        name='was_count_webapp',
        args=(was_count_webapp_arg_dict,)
    )
    was_count_catalog_arg_dict = {
        'api_call_name': 'was_count_catalog',
        'was_extract_function_reference': was_04_extract_from_qualys.was_catalog_extract_count,
        'utc_datetime': utc_datetime, 'cred_dict': cred_dict,
        'last_id': etld_lib_config.was_catalog_start_greater_than_last_id,
        'dir_search_glob': etld_lib_config.was_extract_dir_file_search_blob_catalog_count
    }
    was_count_catalog_proc = multiprocessing.Process(
        target=get_was_count,
        name='was_count_catalog',
        args=(was_count_catalog_arg_dict,)
    )

# TODO Multiprocess 2 web apps
    was_webapp_arg_dict = {
        'api_call_name': 'was_webapp',
        'was_extract_function_reference': was_04_extract_from_qualys.was_webapp_extract,
        'utc_datetime': utc_datetime, 'cred_dict': cred_dict, 'page_size': 300,
        'dir_search_glob': etld_lib_config.was_extract_dir_file_search_blob_webapp
    }
    was_webapp_proc = multiprocessing.Process(
        target=get_was_data,
        name='was_webapp',
        args=(was_webapp_arg_dict,)
    )

    was_catalog_arg_dict = {
        'api_call_name': 'was_catalog',
        'was_extract_function_reference': was_04_extract_from_qualys.was_catalog_extract,
        'utc_datetime': utc_datetime, 'cred_dict': cred_dict, 'page_size': 300,
        'last_id': etld_lib_config.was_catalog_start_greater_than_last_id,
        'dir_search_glob': etld_lib_config.was_extract_dir_file_search_blob_catalog
    }
    was_catalog_proc = multiprocessing.Process(
        target=get_was_data,
        name='was_catalog',
        args=(was_catalog_arg_dict,)
    )

    proc_list = [
        was_count_webapp_proc,
        was_count_catalog_proc,
        was_webapp_proc,
        was_catalog_proc
    ]

    for proc_item in proc_list:
        proc_item.daemon = True
        proc_item.start()

    time.sleep(15)
    proc_timeout = 36000  # 10 hour catch all
    for proc_item in proc_list:
        proc_item.join(timeout=proc_timeout)

    for proc_item in proc_list:
        if proc_item.exitcode == 0:
            etld_lib_functions.logger.info(f"{proc_item.name} exited successfully, exit code: {proc_item.exitcode}")
        else:
            etld_lib_functions.logger.error(f"{proc_item.name} exited after .join timeout of {proc_timeout} seconds "
                                            f"with error code: {proc_item.exitcode}")
            etld_lib_functions.logger.error(f"{proc_item.name} failed, please investigate why job ran so long and rerun.")
            for proc_item_to_kill in proc_list:
                proc_item_to_kill.kill()
            exit(1)

    end_was_03_extract_controller()


def main():
    try:
        extract_was_api_data()
    except Exception as e:
        etld_lib_functions.logger.error(f"ERROR: extract_was_api_data function failed.")
        etld_lib_functions.logger.error(f"ERROR: {e}")
        formatted_lines = traceback.format_exc().splitlines()
        etld_lib_functions.logger.error(f"ERROR: {formatted_lines}")


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='was_03_extract_controller')
    etld_lib_config.main()
    etld_lib_credentials.main()
    etld_lib_authentication_objects.main()
    main()
