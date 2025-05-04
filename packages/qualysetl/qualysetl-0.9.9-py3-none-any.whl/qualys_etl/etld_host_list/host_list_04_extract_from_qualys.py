#!/usr/bin/env python3
#from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_authentication_objects
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_extract_transform_load
from qualys_etl.etld_lib import etld_lib_datetime


def host_list_extract_batch(host_xml_file=None, id_min=0,
                            batch_number=None, cred_dict={}, qualys_headers_multiprocessing_dict={}):

    begin_host_list_04_extract_from_qualys(message=batch_number)
    authorization = cred_dict['authorization']  # Base64 user:password
    # url = f"https://{cred_dict['api_fqdn_server']}/api/2.0/fo/asset/host/"  # Qualys Endpoint
    url = f"https://{cred_dict['api_fqdn_server']}{etld_lib_config.host_list_api_endpoint}"  # Qualys Endpoint

    payload = etld_lib_config.host_list_api_payload
    payload.update({'id_min': id_min})
    if isinstance(etld_lib_config.host_list_payload_option, dict):
        payload.update(etld_lib_config.host_list_payload_option)

    headers = {'X-Requested-With': 'qualysetl', 'Authorization': authorization}

    etld_lib_functions.logger.info(f"api call     - {url}")
    etld_lib_functions.logger.info(f"api options  - {payload}")

    etld_lib_extract_transform_load.extract_qualys(
        try_extract_max_count=etld_lib_config.host_list_try_extract_max_count,
        url=url,
        headers=headers,
        payload=payload,
        http_conn_timeout=etld_lib_config.host_list_http_conn_timeout,
        chunk_size_calc=etld_lib_config.host_list_chunk_size_calc,
        output_file=host_xml_file,
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers_multiprocessing_dict,
        batch_number_formatted=batch_number,
        compression_method=etld_lib_config.host_list_open_file_compression_method)
    end_host_list_04_extract_from_qualys(message=batch_number)


def host_list_extract(cred_dict: dict):

    begin_host_list_04_extract_from_qualys()
    authorization = cred_dict['authorization']  # Base64 user:password
    # url = f"https://{cred_dict['api_fqdn_server']}/api/2.0/fo/asset/host/"  # Qualys Endpoint
    url = f"https://{cred_dict['api_fqdn_server']}{etld_lib_config.host_list_api_endpoint}"  # Qualys Endpoint
    payload = etld_lib_config.host_list_api_payload
    payload.update({'truncation_limit': '0'})
    if isinstance(etld_lib_config.host_list_payload_option, dict):
        payload.update(etld_lib_config.host_list_payload_option)
    etld_lib_functions.logger.info(f"api call     - {url}")
    etld_lib_functions.logger.info(f"api options  - {payload}")

    chunk_size_calc = etld_lib_config.host_list_chunk_size_calc
    try_extract_max_count = etld_lib_config.host_list_try_extract_max_count
    http_conn_timeout = etld_lib_config.host_list_http_conn_timeout
    qualys_headers = {}
    multi_proc_batch_number = None
    headers = {'X-Requested-With': 'qualysetl', 'Authorization': authorization}

    batch_date = etld_lib_datetime.get_utc_datetime_qualys_format()
    batch_number = 1
    batch_number_str = f'batch_{batch_number:06d}'
    file_info_dict = \
        etld_lib_config.prepare_extract_batch_file_name(
            next_batch_number_str=batch_number_str,
            next_batch_date=batch_date,
            extract_dir=etld_lib_config.host_list_extract_dir,
            file_name_type="host_list",
            file_name_option="vm_processed_after",
            file_name_option_date=etld_lib_config.host_list_vm_processed_after,
            compression_method=etld_lib_config.host_list_open_file_compression_method
        )

    etld_lib_extract_transform_load.extract_qualys(
        try_extract_max_count=try_extract_max_count,
        url=url,
        headers=headers,
        payload=payload,
        http_conn_timeout=http_conn_timeout,
        chunk_size_calc=chunk_size_calc,
        output_file=file_info_dict['next_file_path'],
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers,
        batch_number_formatted=multi_proc_batch_number,
        compression_method=etld_lib_config.host_list_open_file_compression_method)
    end_host_list_04_extract_from_qualys()
    return qualys_headers


def begin_host_list_04_extract_from_qualys(message=""):
    etld_lib_functions.logger.info(f"start {message}")


def end_host_list_04_extract_from_qualys(message=""):
    etld_lib_functions.logger.info(f"end   {message}")


def main():
    credentials_dict = etld_lib_authentication_objects.qualys_authentication_obj.get_credentials_dict()
    host_list_extract(cred_dict=credentials_dict)


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_04_extract_from_qualys')
    etld_lib_config.main()
    #etld_lib_credentials.main()
    etld_lib_authentication_objects.main()
    main()



