#!/usr/bin/env python3
import os
from pathlib import Path
#from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_authentication_objects
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_extract_transform_load
from qualys_etl.etld_lib import etld_lib_datetime


def host_list_detection_extract(
        xml_file: str, batch_of_host_ids: str, batch_number_str: str,
        qualys_headers_multiprocessing_dict, cred_dict: dict):

    begin_host_list_detection_04_extract(message=batch_number_str)
    authorization = cred_dict['authorization']  # Base64 user:password
    #url = f"https://{cred_dict['api_fqdn_server']}/api/2.0/fo/asset/host/vm/detection/"
    url = f"https://{cred_dict['api_fqdn_server']}{etld_lib_config.host_list_detection_api_endpoint}"

    payload = etld_lib_config.host_list_detection_api_payload
    payload_id_list = ",".join(str(x) for x in batch_of_host_ids)
    payload.update({'truncation_limit': '0', 'ids': payload_id_list})
    if isinstance(etld_lib_config.host_list_detection_payload_option, dict):
        payload.update(etld_lib_config.host_list_detection_payload_option)

    headers = {'X-Requested-With': 'qualysetl', 'Authorization': authorization}

    print_payload = payload.copy()
    print_payload['ids'] = "TRUNCATED FOR LOG"
    etld_lib_functions.logger.info(f"api call     - {url}")
    etld_lib_functions.logger.info(f"api options  - {print_payload}")

    chunk_size_calc = etld_lib_config.host_list_detection_chunk_size_calc
    try_extract_max_count = etld_lib_config.host_list_detection_try_extract_max_count
    http_conn_timeout = etld_lib_config.host_list_detection_http_conn_timeout
    etld_lib_extract_transform_load.extract_qualys(
        try_extract_max_count=try_extract_max_count,
        url=url,
        headers=headers,
        payload=payload,
        http_conn_timeout=http_conn_timeout,
        chunk_size_calc=chunk_size_calc,
        output_file=xml_file,
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers_multiprocessing_dict,
        batch_number_formatted=batch_number_str,
        compression_method=etld_lib_config.host_list_detection_open_file_compression_method)

    end_host_list_detection_04_extract(message=batch_number_str)


def get_qualys_limits_from_host_list_detection(qualys_headers_multiprocessing_dict, cred_dict):

    authorization = cred_dict['authorization']  # Base64 user:password
    #url = f"https://{cred_dict['api_fqdn_server']}/api/2.0/fo/asset/host/vm/detection/"
    url = f"https://{cred_dict['api_fqdn_server']}{etld_lib_config.host_list_detection_api_endpoint}"

    payload = {'action': 'list',
               'truncation_limit': '1',
               }

    headers = {'X-Requested-With': 'qualysetl', 'Authorization': authorization}

    xml_file = Path(os.devnull)
    chunk_size_calc = etld_lib_config.host_list_detection_chunk_size_calc
    try_extract_max_count = etld_lib_config.host_list_detection_try_extract_max_count
    http_conn_timeout = etld_lib_config.asset_inventory_http_conn_timeout
    batch_number_str = "check_headers"
    etld_lib_extract_transform_load.extract_qualys(
        try_extract_max_count=try_extract_max_count,
        url=url,
        headers=headers,
        payload=payload,
        http_conn_timeout=http_conn_timeout,
        chunk_size_calc=chunk_size_calc,
        output_file=xml_file,
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers_multiprocessing_dict,
        batch_number_formatted=batch_number_str)


def end_message_info(url, xml_file_utc_run_datetime, xml_file):
    etld_lib_functions.log_file_info(url, 'url')
    etld_lib_functions.logger.info(f"Run Date: {xml_file_utc_run_datetime}")
    etld_lib_functions.log_file_info(xml_file)


def begin_host_list_detection_04_extract(message=""):
    etld_lib_functions.logger.info(f"start {message}")


#def end_host_list_detection_04_extract(url, xml_file_utc_run_datetime, xml_file, message=""):
#    end_message_info(url, xml_file_utc_run_datetime, xml_file)
#    etld_lib_functions.logger.info(f"end   {message}")

def end_host_list_detection_04_extract(message=""):
    etld_lib_functions.logger.info(f"end   {message}")


def main(args=None):
    test_one_batch()


def test_one_batch():
    # TODO get list of batch id's for testing.
    xml_file_utc_run_datetime = etld_lib_datetime.get_utc_datetime_qualys_format()
    file_info_dict = \
        etld_lib_config.prepare_extract_batch_file_name(
            next_batch_number_str="batch_000001",
            next_batch_date=xml_file_utc_run_datetime,
            extract_dir=etld_lib_config.host_list_detection_extract_dir,
            file_name_type="host_list_detection",
            file_name_option="vm_processed_after",
            file_name_option_date=etld_lib_config.host_list_detection_vm_processed_after,
            compression_method=etld_lib_config.host_list_detection_open_file_compression_method
        )

    #cred_dict=etld_lib_credentials.get_cred(cred_dict={})
    credentials_dict = etld_lib_authentication_objects.qualys_authentication_obj.get_credentials_dict()
    host_list_detection_extract(
        xml_file=file_info_dict['next_file_path'],
        batch_of_host_ids="",
        batch_number_str=file_info_dict['next_batch_number_str'],
        qualys_headers_multiprocessing_dict=None,
        cred_dict=credentials_dict
    )


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_detection_04_extract')
    etld_lib_config.main()
    #etld_lib_credentials.main()
    etld_lib_authentication_objects.main()
    main()



