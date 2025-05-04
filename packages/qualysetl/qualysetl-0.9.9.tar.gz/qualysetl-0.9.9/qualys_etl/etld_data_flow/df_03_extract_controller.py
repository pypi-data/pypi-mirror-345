#!/usr/bin/env python3
import multiprocessing
import traceback
import time
import json
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_config
#from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_authentication_objects
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_datetime
from qualys_etl.etld_lib import etld_lib_extract_transform_load
from qualys_etl.etld_pcrs import pcrs_05_transform_load_json_to_sqlite
from qualys_etl.etld_pcrs import pcrs_04_extract_from_qualys

global utc_datetime

def begin_pcrs_03_extract_controller(message=""):
    etld_lib_functions.logger.info(f"start {message}")


def end_pcrs_03_extract_controller(message=""):
    etld_lib_functions.logger.info(f"end  {message}")

def start_multiprocessing_transform_json_to_sqlite():

    if etld_lib_config.pcrs_json_to_sqlite_via_multiprocessing is True:
        batch_queue_of_file_paths, batch_queue_process = \
            pcrs_05_transform_load_json_to_sqlite.\
            spawn_multiprocessing_queue_to_transform_and_load_json_files_into_sqlite()
        etld_lib_functions.logger.info(f"Queue of json files process id: {batch_queue_process.pid} ")
        batch_queue_of_file_paths.put("BEGIN")
        return batch_queue_of_file_paths, batch_queue_process
    else:
        return None, None


def stop_multiprocessing_transform_json_to_sqlite(batch_queue_process, batch_queue_of_file_paths):

    if etld_lib_config.pcrs_json_to_sqlite_via_multiprocessing is True:
        batch_queue_of_file_paths.put("END")
        while True:
            if batch_queue_process.is_alive():
                etld_lib_functions.logger.info("Waiting for Queue to end.")
                time.sleep(15)
            else:
                etld_lib_functions.logger.info("Queue Completed.")
                break


def add_batch_to_transform_json_to_sqlite(batch_number_str,
                                          json_file,
                                          batch_queue_of_file_paths: multiprocessing.Queue,
                                          batch_queue_process: multiprocessing.Process):

    if etld_lib_config.pcrs_json_to_sqlite_via_multiprocessing is True:
        etld_lib_functions.logger.info(f"Sending batch file to multiprocessing Queue: {Path(json_file).name}")
        try:
            batch_queue_of_file_paths.put(str(json_file), timeout=30)
        except Exception as e:
            etld_lib_functions.logger.error(f"Problem putting file in queue: {str(json_file)}")
            exit(1)

        # if batch_queue_process.is_alive():
        #     pass
        # else:
        #     etld_lib_functions.logger.error("Batch Process was killed or database error, please investigate and retry.")
        #     exit(1)


def check_qualys_connection_rate_limits(batch_number_str, qualys_headers_dict, batch_info):

    if batch_number_str in qualys_headers_dict.keys():
        if 'x_ratelimit_remaining' in qualys_headers_dict[batch_number_str].keys():
            x_ratelimit_remaining = qualys_headers_dict[batch_number_str]['x_ratelimit_remaining']
            if int(x_ratelimit_remaining) < 15:
                etld_lib_functions.logger.warning(f"x_ratelimit_remaining is less than 15. "
                                                  f"Sleeping 5 min.  batch_info: {batch_info}, "
                                                  f"header_info: {qualys_headers_dict[batch_number_str]}")
                time.sleep(300)
        else:
            etld_lib_functions.logger.warning(f"x_ratelimit_remaining missing from Qualys Header. "
                                              f"Sleeping 5 min.  batch_info: {batch_info}, "
                                              f"header_info: {qualys_headers_dict[batch_number_str]}")
            time.sleep(300)


def remove_old_files():

    etld_lib_config.remove_old_files(
        dir_path=etld_lib_config.pcrs_extract_dir,
        dir_search_glob=etld_lib_config.pcrs_extract_dir_file_search_blob,
        other_files_list=etld_lib_config.pcrs_data_files
    )

    etld_lib_config.remove_old_files(
        dir_path=etld_lib_config.pcrs_distribution_dir,
        dir_search_glob=etld_lib_config.pcrs_distribution_dir_file_search_blob
    )


def get_pcrs_policy_list_data(batch_queue_process, batch_queue_of_file_paths):

    etld_lib_functions.logger.info("start get_pcrs_policy_list_data")
    qualys_headers_dict = {}
    batch_number = 0
    batch_number_str = f'batch_{batch_number:06d}'
    etld_lib_authentication_objects.qualys_authentication_obj.get_current_bearer_token()
    cred_dict = etld_lib_authentication_objects.qualys_authentication_obj.get_credentials_dict()

    file_info_dict = \
        etld_lib_config.prepare_extract_batch_file_name(
            next_batch_number_str='batch_000000',
            next_batch_date=utc_datetime,
            extract_dir=etld_lib_config.pcrs_extract_dir,
            file_name_type="pcrs_policy_list",
            file_name_option="lastEvaluationDate",
            file_name_option_date=etld_lib_config.pcrs_last_evaluation_date,
            file_extension="json",
            compression_method=etld_lib_config.pcrs_open_file_compression_method)

    policy_list = pcrs_04_extract_from_qualys.pcrs_extract_policy_list(
        last_evaluation_date=etld_lib_config.pcrs_last_evaluation_date,
        batch_number_str=batch_number_str,
        payload_dict=etld_lib_config.pcrs_policy_list_payload_option,
        qualys_headers_dict=qualys_headers_dict,
        cred_dict=cred_dict,
        file_info_dict=file_info_dict)

    if len(policy_list) > 0:
        add_batch_to_transform_json_to_sqlite(
            batch_number_str=batch_number_str, json_file=file_info_dict['next_file_path'],
            batch_queue_process=batch_queue_process, batch_queue_of_file_paths=batch_queue_of_file_paths)
    else:
        etld_lib_functions.logger.warning(f"Zero Policies Found Active")
        etld_lib_functions.logger.warning(f"Check permissions of Qualys User and determine if Policies are Active.")
        exit(0)

    etld_lib_functions.logger.info("end get_pcrs_policy_list_data")

def get_pcrs_hostids_data(batch_queue_process, batch_queue_of_file_paths):

    etld_lib_functions.logger.info("start get_pcrs_hostids_data")
    # Get Policy List
    file_list = etld_lib_config.get_list_of_matching_files(
        dir_path=etld_lib_config.pcrs_extract_dir,
        dir_search_glob=etld_lib_config.pcrs_extract_dir_file_search_blob_policy_list
    )
    if len(file_list) > 1:
        etld_lib_functions.logger.error(f"ERROR: Old pcrs_policy_list files exist in {etld_lib_config.pcrs_extract_dir}")
        etld_lib_functions.logger.error(f"ERROR: {file_list}")
        etld_lib_functions.logger.error(f"ERROR: please determine if files are locked due to permissions or other issues and rerun.")
        exit(1)
    elif len(file_list) != 1:
        etld_lib_functions.logger.error(f"ERROR: could not find pcrs_policy_list file in {etld_lib_config.pcrs_extract_dir}")
        etld_lib_functions.logger.error(f"ERROR: {file_list}")
        etld_lib_functions.logger.error(f"ERROR: please determine if your Qualys API User has access to PC Module.")
        exit(1)

    with etld_lib_config.pcrs_open_file_compression_method(file_list[0], "rt", encoding='utf-8') as read_file:
       policy_list = json.load(read_file)
       batch_number = 0
       active_policy_list = pcrs_04_extract_from_qualys.pcrs_get_sorted_active_policy_list(policy_list)
       for policy_item in active_policy_list:
           # Extract hostids for a policy.
           policy_id = policy_item['id']
           if get_pcrs_postureinfo_process_policy_id_status(policy_id):
               pass
           else:
               etld_lib_functions.logger.info(f"Bypassing Policy Id:{policy_id} due to include/exclude in etld_config_settings.yaml")
               continue

           batch_number = batch_number + 1
           batch_number_str = f'batch_{batch_number:06d}'
           batch_number_str = f'{batch_number_str}_policyId_{policy_id}'

           file_info_dict = \
               etld_lib_config.prepare_extract_batch_file_name(
                   next_batch_number_str=batch_number_str,
                   next_batch_date=utc_datetime,
                   extract_dir=etld_lib_config.pcrs_extract_dir,
                   file_name_type="pcrs_hostids",
                   file_name_option="lastEvaluationDate",
                   file_name_option_date=etld_lib_config.pcrs_last_evaluation_date,
                   file_extension="json",
                   compression_method=etld_lib_config.pcrs_open_file_compression_method)

           #cred_dict = etld_lib_credentials.get_bearer_stored_in_env(update_bearer=False, cred=cred_dict)
           etld_lib_authentication_objects.qualys_authentication_obj.get_current_bearer_token()
           cred_dict = etld_lib_authentication_objects.qualys_authentication_obj.get_credentials_dict()

           qualys_headers_dict = {}
           pcrs_04_extract_from_qualys.pcrs_extract_hostids_list(
               last_scan_date=etld_lib_config.pcrs_last_scan_date,
               last_evaluation_date=etld_lib_config.pcrs_last_evaluation_date,
               batch_number_str=batch_number_str,
               qualys_headers_dict=qualys_headers_dict,
               payload_dict=etld_lib_config.pcrs_hostids_payload_option,
               payload_postureinfo_dict=etld_lib_config.pcrs_postureinfo_payload_option,
               cred_dict=cred_dict,
               policy_id=policy_item['id'],
               file_info_dict=file_info_dict)

           hostids_list = pcrs_04_extract_from_qualys.pcrs_get_hostids_list(json_file=file_info_dict['next_file_path'])
           if len(hostids_list[0]['hostIds']) > 0:
               add_batch_to_transform_json_to_sqlite(
                   batch_number_str=batch_number_str, json_file=file_info_dict['next_file_path'],
                   batch_queue_process=batch_queue_process, batch_queue_of_file_paths=batch_queue_of_file_paths)
           else:
              etld_lib_functions.logger.info(f"PolicyID: {hostids_list[0]['policyId']}, Zero Hosts Found, not loaded to database")

       etld_lib_functions.logger.info("end   get_pcrs_hostids_data")


def get_pcrs_postureinfo_process_policy_id_status(pcrs_policy_id):
    process_policy_id_status = False

    pcrs_policy_id_include_list = etld_lib_config.pcrs_policy_id_include_list
    pcrs_policy_id_exclude_list = etld_lib_config.pcrs_policy_id_exclude_list
    if isinstance(pcrs_policy_id_include_list, list):
        if len(pcrs_policy_id_include_list) > 0:
            for policy_id in pcrs_policy_id_include_list:
                if str(policy_id) == str(pcrs_policy_id):
                    process_policy_id_status = True
                    break
        else:
            process_policy_id_status = True
    else:
        process_policy_id_status = True

    if isinstance(pcrs_policy_id_exclude_list, list):
        if len(pcrs_policy_id_exclude_list) > 0:
            for policy_id in pcrs_policy_id_exclude_list:
                if str(policy_id) == str(pcrs_policy_id):
                    process_policy_id_status = False
                    break

    return process_policy_id_status


def get_pcrs_postureinfo_data(batch_queue_process, batch_queue_of_file_paths):

    etld_lib_functions.logger.info("start get_pcrs_postureinfo_data")

    file_list = etld_lib_config.get_list_of_matching_files(
        dir_path=etld_lib_config.pcrs_extract_dir,
        dir_search_glob=etld_lib_config.pcrs_extract_dir_file_search_blob_hostids
    )
    # Loop through policy hostids files and extract postureinfo.
    for pcrs_hostids_file in file_list:
        get_pcrs_postureinfo_for_one_policy_with_multiprocessing(pcrs_hostids_file,
                                            batch_queue_process,
                                            batch_queue_of_file_paths,
                                            max_batch_size=etld_lib_config.pcrs_multi_proc_batch_size)

    etld_lib_functions.logger.info("end   get_pcrs_postureinfo_data")


def get_pcrs_postureinfo_for_one_policy_with_multiprocessing_wrapper():
    pass


def get_pcrs_postureinfo_for_one_policy_with_multiprocessing(
        pcrs_hostids_file:Path,
        batch_queue_process: multiprocessing.Process,
        batch_queue_of_file_paths: multiprocessing.Queue,
        max_batch_size=300
):
    with etld_lib_config.pcrs_open_file_compression_method(pcrs_hostids_file, "rt", encoding='utf-8') as read_file:
        pcrs_dict = json.load(read_file)

    pcrs_hostids_file_name_split = str(pcrs_hostids_file).split('_')
    # Get Batch Number from File Name
    pcrs_hostids_file_name_split.reverse()

    batch_number_str = "0"
    while pcrs_hostids_file_name_split:
        component = pcrs_hostids_file_name_split.pop()
        if component == 'batch':
            batch_number_str = pcrs_hostids_file_name_split.pop()
            break
    batch_number_str = f'batch_{batch_number_str}'

    subscription_id =  pcrs_dict[0]['subscriptionId']
    policy_id =  pcrs_dict[0]['policyId']
    pcrs_hostids_template_str = \
        '[{' + f'"policyId": "{policy_id}","subscriptionId":"{subscription_id}","hostIds":[]' + '}]'

    pcrs_hostids_template_dict = json.loads(pcrs_hostids_template_str)
    hostids_slice_counter = 0
    hostids_batch_counter = 0
    # Extract Posture info
    etld_lib_functions.logger.info(f"start get posture info for policy_id: {policy_id}, File: {Path(pcrs_hostids_file).name}")
    count_total_hostids_for_policy_id = 0
    proc_list = []
    for hostid in list(pcrs_dict[0]['hostIds']):
        pcrs_hostids_template_dict[0]['hostIds'].append(hostid)
        hostids_batch_counter = hostids_batch_counter + 1
        count_total_hostids_for_policy_id = count_total_hostids_for_policy_id + 1

        if int(hostids_batch_counter) >= int(max_batch_size):
            hostids_batch_counter = 0
            hostids_slice_counter = hostids_slice_counter + 1
            batch_number_and_slice_and_policy_str = f'{batch_number_str}_slice_{hostids_slice_counter:06d}_policyId_{policy_id}'

            if etld_lib_config.pcrs_postureinfo_turn_on_multiprocessing_flag == True:
                etld_lib_functions.logger.info(f"spawn {batch_number_and_slice_and_policy_str}")
                proc_list = get_pcrs_postureinfo_for_batch_of_hostids_multiprocessing(
                    batch_number_str=batch_number_and_slice_and_policy_str,
                    policy_id=policy_id,
                    payload_postureinfo_dict=pcrs_hostids_template_dict,
                    batch_queue_process=batch_queue_process,
                    batch_queue_of_file_paths=batch_queue_of_file_paths,
                    proc_list=proc_list,
                    concurrency_limit=etld_lib_config.pcrs_concurrency_limit
                )
            else:
                get_pcrs_postureinfo_for_batch_of_hostids(batch_number_str=batch_number_and_slice_and_policy_str,
                                                          policy_id=policy_id,
                                                          payload_postureinfo_dict=pcrs_hostids_template_dict,
                                                          batch_queue_process=batch_queue_process,
                                                          batch_queue_of_file_paths=batch_queue_of_file_paths)

            pcrs_hostids_template_dict = json.loads(pcrs_hostids_template_str)

    # Final extract if needed.
    if len(pcrs_hostids_template_dict[0]['hostIds']) > 0:
        #print(f"{batch_number_str}: {pcrs_hostids_template_dict}")
        hostids_slice_counter = hostids_slice_counter + 1
        batch_number_and_slice_and_policy_str = f'{batch_number_str}_slice_{hostids_slice_counter:06d}_policyId_{policy_id}'
        get_pcrs_postureinfo_for_batch_of_hostids(batch_number_str=batch_number_and_slice_and_policy_str,
                                                   policy_id=policy_id,
                                                   payload_postureinfo_dict=pcrs_hostids_template_dict,
                                                   batch_queue_process=batch_queue_process,
                                                   batch_queue_of_file_paths=batch_queue_of_file_paths)

    if etld_lib_config.pcrs_postureinfo_turn_on_multiprocessing_flag == True:
        etld_lib_functions.logger.info(f"Start Block waiting for final pcrs_postureinfo policy_id: {policy_id} processes to finish.")
        block_waiting_for_final_processes_to_finish(proc_list)
        validate_processes_finished_exit_code_zero(proc_list, reporting=True)
        etld_lib_functions.logger.info(f"End Block waiting for final pcrs_postureinfo policy_id: {policy_id} processes to finish.")

    etld_lib_functions.logger.info(f"end   get posture info for policy_id: {policy_id}, count: {count_total_hostids_for_policy_id:,}")



def get_pcrs_postureinfo_for_batch_of_hostids_multiprocessing(
        batch_number_str,
        policy_id,
        payload_postureinfo_dict,
        batch_queue_process,
        batch_queue_of_file_paths,
        proc_list,
        concurrency_limit
):

    pcrs_postureinfo_arg_dict = {
        'batch_number_str': batch_number_str,
        'policy_id': policy_id,
        'payload_postureinfo_dict': payload_postureinfo_dict,
        'batch_queue_process': batch_queue_process,
        'batch_queue_of_file_paths': batch_queue_of_file_paths,
        'api_call_name': batch_number_str
    }
    pcrs_postureinfo_proc = multiprocessing.Process(
        target=get_pcrs_postureinfo_for_batch_of_hostids_multiprocessing_wrapper,
        name=batch_number_str,
        args=(pcrs_postureinfo_arg_dict,)
    )
    pcrs_postureinfo_proc.daemon = True
    pcrs_postureinfo_proc.start()
    proc_list.append(pcrs_postureinfo_proc)
    block_if_max_concurrent_processes_running(concurrency_limit, proc_list)
    return proc_list

def get_pcrs_postureinfo_for_batch_of_hostids_multiprocessing_wrapper(pcrs_postureinfo_arg_dict):

    get_pcrs_postureinfo_for_batch_of_hostids(pcrs_postureinfo_arg_dict['batch_number_str'],
                                              pcrs_postureinfo_arg_dict['policy_id'],
                                              pcrs_postureinfo_arg_dict['payload_postureinfo_dict'],
                                              pcrs_postureinfo_arg_dict['batch_queue_process'],
                                              pcrs_postureinfo_arg_dict['batch_queue_of_file_paths'])


def get_pcrs_postureinfo_for_batch_of_hostids(
        batch_number_str, policy_id, payload_postureinfo_dict, batch_queue_process,batch_queue_of_file_paths):

    qualys_headers_dict = {}

    file_info_dict = \
        etld_lib_config.prepare_extract_batch_file_name(
            next_batch_number_str=batch_number_str,
            next_batch_date=utc_datetime,
            extract_dir=etld_lib_config.pcrs_extract_dir,
            file_name_type="pcrs_postureinfo",
            file_name_option="lastEvaluationDate",
            file_name_option_date=etld_lib_config.pcrs_last_evaluation_date,
            file_extension="json",
            compression_method=etld_lib_config.pcrs_open_file_compression_method)

    etld_lib_authentication_objects.qualys_authentication_obj.get_current_bearer_token()
    cred_dict = etld_lib_authentication_objects.qualys_authentication_obj.get_credentials_dict()

    # posture_info_dict = pcrs_04_extract_from_qualys.pcrs_extract_postureinfo(
    posture_info_chunk_of_characters=pcrs_04_extract_from_qualys.pcrs_extract_postureinfo(
        last_scan_date=etld_lib_config.pcrs_last_scan_date,
        last_evaluation_date=etld_lib_config.pcrs_last_evaluation_date,
        batch_number_str=batch_number_str,
        qualys_headers_dict=qualys_headers_dict,
        cred_dict=cred_dict,
        policy_id=policy_id,
        payload_postureinfo_dict=payload_postureinfo_dict,
        payload_dict=etld_lib_config.pcrs_postureinfo_payload_option,
        file_info_dict=file_info_dict)

    # Json usually starts with '[ {"id":...'
    if '{"' in posture_info_chunk_of_characters:
        add_batch_to_transform_json_to_sqlite(
            batch_number_str=batch_number_str,
            json_file=file_info_dict['next_file_path'],
            batch_queue_process=batch_queue_process,
            batch_queue_of_file_paths=batch_queue_of_file_paths)
    else:
        etld_lib_functions.logger.info(f"PolicyID: {policy_id}, Zero Hosts Found Active")


def block_if_max_concurrent_processes_running(max_proc_count, proc_list):
    proc_item: multiprocessing.Process
    while True:
        is_alive_count = 0
        for proc_item in proc_list:
            if proc_item.is_alive():
               is_alive_count = is_alive_count + 1
        if int(is_alive_count) >= int(max_proc_count):
           time.sleep(1)
           validate_processes_finished_exit_code_zero(proc_list)
        else:
            break

def block_waiting_for_final_processes_to_finish(proc_list):
    proc_item: multiprocessing.Process
    while True:
        is_alive_count = 0
        for proc_item in proc_list:
            if proc_item.is_alive():
                is_alive_count = is_alive_count + 1
        if is_alive_count >0:
            time.sleep(1)
        else:
            break

def validate_processes_finished_exit_code_zero(proc_list, reporting=False):
    for proc_item in proc_list:
        if proc_item.is_alive():
            pass
        elif proc_item.exitcode == 0:
            if reporting:
                etld_lib_functions.logger.info(f"process info: {proc_item}")
        else:
            etld_lib_functions.logger.error(f"{proc_item.name} exited with error code: {proc_item.exitcode}")
            etld_lib_functions.logger.error(f"{proc_item.name} failed, please investigate why job ran so long and rerun.")
            for proc_item_to_kill in proc_list:
                proc_item_to_kill.kill()
            exit(1)

def test_system_option(file_path: Path, has_more_records, number_of_files_to_extract, test_system_flag):
    if test_system_flag is True:
        test_batch_number = \
            etld_lib_extract_transform_load.get_batch_number_from_filename(file_path)
        if int(test_batch_number) >= int(number_of_files_to_extract):
            has_more_records = '0'
    return has_more_records


def main():
    global utc_datetime
    utc_datetime = etld_lib_datetime.get_utc_datetime_qualys_format()
    begin_pcrs_03_extract_controller()
    remove_old_files()
    batch_queue_of_file_paths, batch_queue_process = start_multiprocessing_transform_json_to_sqlite()
    try:
        get_pcrs_policy_list_data(batch_queue_process=batch_queue_process,
                                  batch_queue_of_file_paths=batch_queue_of_file_paths)
        get_pcrs_hostids_data(batch_queue_process=batch_queue_process,
                              batch_queue_of_file_paths=batch_queue_of_file_paths)
        get_pcrs_postureinfo_data(batch_queue_process=batch_queue_process,
                                  batch_queue_of_file_paths=batch_queue_of_file_paths)
    except Exception as e:
        etld_lib_functions.logger.error(f"ERROR: get_pcrs function failed. policy_list or hostids_data or postureinfo_data.  Check log for last exec.")
        etld_lib_functions.logger.error(f"ERROR: {e}")
        formatted_lines = traceback.format_exc().splitlines()
        etld_lib_functions.logger.error(f"ERROR: {formatted_lines}")
        exit(1)
    finally:
        stop_multiprocessing_transform_json_to_sqlite(batch_queue_of_file_paths=batch_queue_of_file_paths,
                                                      batch_queue_process=batch_queue_process)

    end_pcrs_03_extract_controller()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='pcrs_03_extract_controller')
    etld_lib_config.main()
    etld_lib_authentication_objects.main()
    main()



