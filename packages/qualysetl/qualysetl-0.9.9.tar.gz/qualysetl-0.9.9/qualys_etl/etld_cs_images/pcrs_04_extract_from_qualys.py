#!/usr/bin/env python3
from pathlib import Path
import json
import collections
import gzip
#from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_authentication_objects
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_datetime
from qualys_etl.etld_lib import etld_lib_extract_transform_load


def pcrs_extract_policy_list(last_evaluation_date,
                             batch_number_str,
                             qualys_headers_dict,
                             payload_dict,
                             cred_dict,
                             file_info_dict) -> list:

    begin_pcrs_04_extract(message=f"extract of Policy List with last evaluation date: {last_evaluation_date}")
    bearer = cred_dict['bearer']
    url = f"https://{cred_dict['gateway_fqdn_server']}/pcrs/1.0/posture/policy/list"
    if 'lastEvaluationDate' in payload_dict:
        url = f"{url}?lastEvaluationDate={payload_dict['lastEvaluationDate']}"
    else:
        url = f"{url}?lastEvaluationDate={last_evaluation_date}" # From command line -d option.

    headers = {'X-Requested-With': 'qualysetl', 'Authorization': bearer, 'Content-Type': 'application/json'}
    etld_lib_functions.logger.info(f"api call     - {url}")

    json_file = Path(file_info_dict['next_file_path'])

    cred_dict = etld_lib_extract_transform_load.extract_qualys(
        try_extract_max_count=etld_lib_config.pcrs_try_extract_max_count,
        url=url,
        headers=headers,
        payload={},
        http_conn_timeout=etld_lib_config.pcrs_http_conn_timeout,
        chunk_size_calc=etld_lib_config.pcrs_chunk_size_calc,
        output_file=json_file,
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers_dict,
        batch_number_formatted=batch_number_str,
        extract_validation_type='json',
        request_method="GET"
    )

    policy_list = pcrs_get_policy_list(json_file=json_file)
    end_pcrs_04_extract(message=f"extract of Policy List with last evaluation date: {last_evaluation_date}")
    return policy_list


def pcrs_extract_hostids_list(last_scan_date,
                              last_evaluation_date,
                             batch_number_str,
                             qualys_headers_dict,
                             cred_dict,
                             payload_dict,
                             payload_postureinfo_dict,
                             policy_id,
                             file_info_dict) -> list:

    #begin_pcrs_04_extract(message=f"extract policy hostids with last scan date: {last_scan_date}")
    begin_pcrs_04_extract(message=f"extract policy hostids")            # Use last evaluation date.
    bearer = cred_dict['bearer']
    url = f"https://{cred_dict['gateway_fqdn_server']}/pcrs/1.0/posture/hostids"
    url = f"{url}?policyId={policy_id}"
    if 'lastScanDate' in payload_dict:
        url = f"{url}&lastScanDate={str(payload_dict['lastScanDate'])}"
    elif 'lastScanDate' in payload_postureinfo_dict:
        etld_lib_functions.logger.info("lastScanDate for hostids obtained from payload_postureinfo lastScanDate")
        url = f"{url}&lastScanDate={str(payload_postureinfo_dict['lastScanDate'])}"
    elif 'lastScanDateFrom' in payload_postureinfo_dict:
        etld_lib_functions.logger.info("lastScanDate for hostids obtained from payload_postureinfo lastScanDateFrom")
        url = f"{url}&lastScanDate={str(payload_postureinfo_dict['lastScanDateFrom'])}"
    elif '1970' not in last_evaluation_date: # Default 1970 date
        last_scan_date = etld_lib_datetime.add_or_subtract_hours_from_rfc_3339_datetime(last_evaluation_date,1,'subtract')
        etld_lib_functions.logger.info("lastScanDate derived from lastEvaluationDate minus one hour.")
        url = f"{url}&lastScanDate={last_scan_date}"


    headers = {'X-Requested-With': 'qualysetl', 'Authorization': bearer, 'Content-Type': 'application/json'}
    etld_lib_functions.logger.info(f"api call     - {url}")

    json_file = Path(file_info_dict['next_file_path'])

    cred_dict = etld_lib_extract_transform_load.extract_qualys(
        try_extract_max_count=etld_lib_config.pcrs_try_extract_max_count,
        url=url,
        headers=headers,
        payload={},
        http_conn_timeout=etld_lib_config.pcrs_http_conn_timeout,
        chunk_size_calc=etld_lib_config.pcrs_chunk_size_calc,
        output_file=json_file,
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers_dict,
        batch_number_formatted=batch_number_str,
        extract_validation_type='json',
        request_method="GET"
    )

    #policy_list = pcrs_get_policy_list(json_file=json_file)
    hostids_list = []
    end_pcrs_04_extract(message=f"extract policy hostids")            # Use last evaluation date.
    return hostids_list


def pcrs_extract_postureinfo(last_scan_date,
                             last_evaluation_date,
                              batch_number_str,
                              qualys_headers_dict,
                              cred_dict,
                              policy_id,
                             payload_postureinfo_dict,
                             payload_dict,
                              file_info_dict) -> str:


    begin_pcrs_04_extract(message=f"extract postureinfo batch: {batch_number_str}")
    number_of_hostids = len(payload_postureinfo_dict[0]['hostIds'])
    etld_lib_functions.logger.info(f"postureinfo hostIds submitted: {number_of_hostids:,}")
    bearer = cred_dict['bearer']
    url = f"https://{cred_dict['gateway_fqdn_server']}/pcrs/1.0/posture/postureInfo" #?evidenceRequired=1&compressionRequired=0
    # Options potentially from etld_config_settings.yaml.
    # lastScanDate, lastEvaluationDate, lastScanDateFrom, lastScanDateTo, statusChangedSince

    url = f"{url}?compressionRequired=1"

    if 'lastScanDate' in payload_dict:
        url = f"{url}&lastScanDate={str(payload_dict['lastScanDate'])}"

    if 'lastEvaluationDate' in payload_dict:
        url = f"{url}&lastEvaluationDate={str(payload_dict['lastEvaluationDate'])}"
    else:
        url = f"{url}&lastEvaluationDate={last_evaluation_date}" # Command Line Selection by Default.

    if 'lastScanDateFrom' in payload_dict and 'lastScanDateTo' in payload_dict:
        url = f"{url}&lastScanDateFrom={str(payload_dict['lastScanDateFrom'])}&lastScanDateTo={str(payload_dict['lastScanDateTo'])}"

    if 'statusChangedSince' in payload_dict:
            url = f"{url}&statusChangedSince={str(payload_dict['statusChangedSince'])}"


    if 'evidenceRequired' in payload_dict:
        url = f"{url}&evidenceRequired={str(payload_dict['evidenceRequired'])}"
    else:
        url = f"{url}&evidenceRequired=1"

    headers = {'X-Requested-With': 'qualysetl', 'Authorization': bearer, 'Content-Type': 'application/json'}
    etld_lib_functions.logger.info(f"api call     - {url}")

    if url.__contains__('compressionRequired=1'):
        compression_method = open
    else:
        compression_method = gzip.open

    json_file = Path(file_info_dict['next_file_path'])
    cred_dict = etld_lib_extract_transform_load.extract_qualys(
        try_extract_max_count=etld_lib_config.pcrs_try_extract_max_count,
        url=url,
        headers=headers,
        payload=json.dumps(payload_postureinfo_dict),
        http_conn_timeout=etld_lib_config.pcrs_http_conn_timeout,
        chunk_size_calc=etld_lib_config.pcrs_chunk_size_calc,
        output_file=json_file,
        cred_dict=cred_dict,
        qualys_headers_multiprocessing_dict=qualys_headers_dict,
        batch_number_formatted=batch_number_str,
        extract_validation_type='json',
        compression_method=compression_method,
        request_method="POST"
    )

    # posture_info_dict = pcrs_get_posture_info_dict(json_file)
    posture_info_chunk_of_characters = pcrs_get_chunk_of_characters_from_file(json_file)
    end_pcrs_04_extract(message=f"extract postureinfo batch: {batch_number_str}, hostIds submitted: {number_of_hostids:,}")
    return posture_info_chunk_of_characters


def pcrs_get_sorted_active_policy_list(policy_list) -> list:

    active_policy_count = 0
    not_active_policy_count = 0
    active_policy_dict = {}
    active_policy_list = []
    sorted_active_policy_list = []
    for policy in policy_list['policyList']:
        if 'status' in policy.keys():
            if policy['status'] == 'active':
                active_policy_count = active_policy_count + 1
                # Create sorted by lastEvaluatedDate policy list
                policy_id = policy['id']
                policy_last_evaluated_date = policy['lastEvaluatedDate']
                sort_key = f"{policy_last_evaluated_date}:{policy_id}"
                active_policy_dict[f"{sort_key}"] = policy
                active_policy_list.append(policy)
            else:
                not_active_policy_count = not_active_policy_count + 1

    sorted_active_policy_dict = collections.OrderedDict(sorted(active_policy_dict.items()))

    for k, v in sorted_active_policy_dict.items():
        sorted_active_policy_list.append(v)

    sorted_active_policy_list.reverse()
    etld_lib_functions.logger.info(f"policyList count active policies: {active_policy_count:,}")
    etld_lib_functions.logger.info(f"policyList count inactive policies: {not_active_policy_count:,}")

    if len(sorted_active_policy_list) == len(active_policy_list):
        pass
    else:
        raise Exception(
            f"Problem sorting active policy list. duplicate key (lastEvaluatedDate:id).")

    return sorted_active_policy_list


def pcrs_get_policy_list(json_file) -> list:
    etld_lib_functions.logger.info(f"pcrs_get_policy_list from file: {json_file}")
    active_policy_list = []
    sorted_active_policy_list = []
    try:
        with etld_lib_config.pcrs_open_file_compression_method(str(json_file), "rt", encoding='utf-8') as read_file:
           policy_list = json.load(read_file)
           if "policyList" in policy_list.keys():
               etld_lib_functions.logger.info(f"policyList file: {json_file}")
               etld_lib_functions.logger.info(f"policyList found, total count of policies: {len(policy_list['policyList'])}")
           else:
               raise Exception(f"Policy List not correctly formed, please review file: {json_file}")

           sorted_active_policy_list = pcrs_get_sorted_active_policy_list(policy_list)

    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Potential JSON File corruption or api error detected: {json_file}")
        raise Exception(f"Exception: {e}")

    return sorted_active_policy_list


def pcrs_get_hostids_list(json_file) -> list:
    etld_lib_functions.logger.info(f"pcrs_get_hostids_list from file: {json_file}")
    hostids_list = []
    try:
        with etld_lib_config.pcrs_open_file_compression_method(
                str(json_file), "rt", encoding='utf-8') as read_file:
            hostids_list = json.load(read_file)
    except Exception as e:
        etld_lib_functions.logger.error(f"pcrs_get_hostids_list Exception: {e}")
        etld_lib_functions.logger.error(f"pcrs_get_hostids_list Potential JSON File corruption or api error detected: {json_file}")
        exit(1)
    return hostids_list


# def pcrs_get_posture_info_dict(json_file) -> dict:
#     etld_lib_functions.logger.info(f"pcrs_get_posture_info_dict from file: {json_file}")
#     posture_info = {}
#     try:
#         with etld_lib_config.pcrs_open_file_compression_method(
#                 str(json_file), "rt", encoding='utf-8') as read_file:
#             posture_info = json.load(read_file)
#     except Exception as e:
#         etld_lib_functions.logger.error(f"pcrs_get_hostids_list Exception: {e}")
#         etld_lib_functions.logger.error(f"pcrs_get_hostids_list Potential JSON File corruption or api error detected: {json_file}")
#         exit(1)
#     return posture_info


def pcrs_get_chunk_of_characters_from_file(file_name, number_of_characters=100) -> str:
    etld_lib_functions.logger.info(f"pcrs_get_chunk_of_characters_from_file: {file_name}")
    try:
        with etld_lib_config.pcrs_open_file_compression_method(
                str(file_name), "rt", encoding='utf-8') as read_file:
            get_chunk = read_file.read(number_of_characters)
    except Exception as e:
        etld_lib_functions.logger.error(f"pcrs_get_chunk_of_characters_from_file Exception: {e}")
        etld_lib_functions.logger.error(
            f"Potential File corruption or api error detected: {file_name}")
        exit(1)
    return get_chunk

# def pcrs_get_policy_list(json_file) -> list:
#     try:
#         with etld_lib_config.pcrs_open_file_compression_method(
#                 str(json_file), "rt", encoding='utf-8') as read_file:
#             policy_list = json.load(read_file)
#
#             if "policyList" in policy_list.keys():
#                 etld_lib_functions.logger.info(f"pcrs get policyList from file: {json_file}")
#             else:
#                 raise Exception(f"pcrs policy list not correctly formed, please review file: {json_file}")
#             return policy_list['policyList']
#
#     except Exception as e:
#         etld_lib_functions.logger.error(f"pcrs_get_policy_list Exception: {e}")
#         etld_lib_functions.logger.error(f"pcrs_get_policy_list Potential JSON File corruption or api error detected: {json_file}")
#         exit(1)


def begin_pcrs_04_extract(message=""):
    etld_lib_functions.logger.info(f"start {message}")


def end_pcrs_04_extract(message=""):
    etld_lib_functions.logger.info(f"end   {message}")


def main(args=None):
    etld_lib_authentication_objects.qualys_authentication_obj.get_current_bearer_token()
    credentials_dict = etld_lib_authentication_objects.qualys_authentication_obj.get_credentials_dict()
    # TODO FOR TESTING, CREATE TEST BATCH OPTIONS HERE.
    # pcrs_extract(cred_dict=credentials_dict)


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='pcrs_04_extract_from_qualys')
    etld_lib_config.main()
    #etld_lib_credentials.main()
    etld_lib_authentication_objects.main()
    main()



