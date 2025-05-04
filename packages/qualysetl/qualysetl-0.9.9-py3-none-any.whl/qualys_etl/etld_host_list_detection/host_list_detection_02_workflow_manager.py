#!/usr/bin/env python3
import sys
import timeit
import time
import fcntl
#import traceback
from pathlib import Path
import multiprocessing
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config
#from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_authentication_objects

from qualys_etl.etld_host_list_detection import host_list_detection_03_extract_controller
from qualys_etl.etld_host_list_detection import host_list_detection_05_transform_load_xml_to_sqlite
from qualys_etl.etld_host_list_detection import host_list_detection_06_distribution
from qualys_etl.etld_host_list import host_list_02_workflow_manager
from qualys_etl.etld_knowledgebase import knowledgebase_02_workflow_manager

global start_time
global stop_time


def host_list_02_workflow_manager_wrapper(module_function=host_list_02_workflow_manager, message=""):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def knowledgebase_02_workflow_manager_wrapper(
       module_function=knowledgebase_02_workflow_manager, message=""
):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def host_list_detection_03_extract_controller_wrapper(module_function=host_list_detection_03_extract_controller, message=""):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def host_list_detection_05_transform_load_xml_to_sqlite_wrapper(
        module_function=host_list_detection_05_transform_load_xml_to_sqlite):
    etld_lib_functions.logger.info(f"start {module_function}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def host_list_detection_06_distribution_wrapper(module_function=host_list_detection_06_distribution):
    etld_lib_functions.logger.info(f"start {module_function}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def begin_message_info():
    etld_lib_functions.logger.info(f"data directory: {etld_lib_config.qetl_user_data_dir}")
    etld_lib_functions.logger.info(f"config file:    {etld_lib_config.qetl_user_config_settings_yaml_file}")


def begin_host_list_detection_02_workflow_manager():
    global start_time
    start_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"__start__ host_list_detection_etl_workflow {str(sys.argv)}")
    begin_message_info()


def end_host_list_detection_02_workflow_manager():
    global start_time
    global stop_time

    stop_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"runtime for host_list_detection_etl_workflow in seconds: {stop_time - start_time:,}")
    etld_lib_functions.logger.info(f"__end__ host_list_detection_etl_workflow {str(sys.argv)}")


def spawn_knowledgebase_02_workflow_manager_wrapper():
    try:
        etld_lib_config.kb_last_modified_after = ""
        process = \
            multiprocessing.Process(target=knowledgebase_02_workflow_manager_wrapper,
                                    name='knowledgebase_02_workflow_manager',
                                    args=(knowledgebase_02_workflow_manager, ""))
        return process
    except Exception as e:
        etld_lib_functions.logger.error(f"Error spawn_knowledgebase_02_workflow_manager_wrapper")
        etld_lib_functions.logger.error(f"Exception: {e}")
        raise Exception("Raise Exception from spawn_knowledgebase_02_workflow_manager_wrapper")


def get_host_list_data():

    try:
        etld_lib_config.host_list_detection_vm_processed_after = etld_lib_config.host_list_vm_processed_after
        long_message = f"host_list_detection_vm_processed_after = " \
                       f"host_list_vm_processed_after={etld_lib_config.host_list_vm_processed_after}"
        host_list_02_workflow_manager_wrapper(message=long_message)
    except Exception as e:
        etld_lib_functions.logger.error(f"Error get_host_list_data")
        etld_lib_functions.logger.error(f"Exception: {e}")
        raise Exception("Raise Exception from host_list_02_workflow_manager_wrapper")


def get_knowledgebase_and_host_list_data():

    try:
        knowledgebase_process = spawn_knowledgebase_02_workflow_manager_wrapper()

        proc_list = [
            knowledgebase_process,
        ]

        knowledgebase_process.daemon = True
        knowledgebase_process.start()
        get_host_list_data()  # blocking as host list database is built.

        proc_timeout = 3600  # 1 hour catch all for knowledgebase
        for proc_item in proc_list:
            proc_item.join(timeout=proc_timeout)

        for proc_item in proc_list:
            if proc_item.exitcode == 0:
                etld_lib_functions.logger.info(f"{proc_item.name} exited successfully, exit code: {proc_item.exitcode}")
            else:
                etld_lib_functions.logger.warning(
                    f"{proc_item.name} exited after .join timeout of {proc_timeout} seconds "
                    f"with error code: {proc_item.exitcode}")
                etld_lib_functions.logger.warning(
                    f"{proc_item.name} failed, please investigate why job ran so long.")
                for proc_item_to_kill in proc_list:
                    proc_item_to_kill.kill()
                raise Exception("get_knowledgebase_and_host_list_data multiprocessing exception")

    except Exception as e:
        etld_lib_functions.logger.warning(f"Exception: {e}")
        raise Exception("get_knowledgebase_and_host_list_data outer catch exception")


def get_knowledgebase_and_host_list_controller():
    retry_attempts = 6
    retry_attempt = 0
    retry_sleep_time = 300
    while retry_attempt < retry_attempts:
        retry_attempt += 1
        try:
            with open(etld_lib_config.kb_lock_file, 'wb+') as lock_knowledgebase_fcntl, \
                    open(etld_lib_config.host_list_lock_file, 'wb+') as lock_host_list_fcntl:        # If locked, exit.
                fcntl.flock(lock_knowledgebase_fcntl, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(lock_host_list_fcntl, fcntl.LOCK_EX | fcntl.LOCK_NB)
                get_knowledgebase_and_host_list_data()
                break # Success
        except Exception as e:
            etld_lib_functions.logger.warning(f"KnowledgeBase or Host List Program Exception.  {__file__} ")
            etld_lib_functions.logger.warning(f"Retrying in {retry_sleep_time} seconds")
            time.sleep(retry_sleep_time)
    else:
        etld_lib_functions.logger.error(f"Retried {retry_attempt} times with no success.")
        etld_lib_functions.logger.error(f"Check to see if KnowledgeBase or Host List Program is already running.  {__file__} ")
        exit(1)


def host_list_detection_etl_workflow():

    try:
        begin_host_list_detection_02_workflow_manager()
        get_knowledgebase_and_host_list_controller()
        host_list_detection_03_extract_controller_wrapper(
            message=f"vm_processed_after={etld_lib_config.host_list_detection_vm_processed_after}")
        host_list_detection_06_distribution_wrapper()
        end_host_list_detection_02_workflow_manager()
    except Exception as e:
        time.sleep(10)
        etld_lib_functions.logger.error(f"Error host_list_detection_02_workflow_manager - "
                                        f"host_list_detection_etl_workflow, "
                                        f"please investigate {sys.argv}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)
    #     formatted_lines = traceback.format_exc().splitlines()
    #     etld_lib_functions.logger.error(f"TRACEBACK: {formatted_lines}")
    #     exit(1)
    # except KeyboardInterrupt:
    #     time.sleep(10)
    #     etld_lib_functions.logger.error(f"Error host_list_detection_02_workflow_manager - "
    #                                     f"host_list_detection_etl_workflow, "
    #                                     f"please investigate {sys.argv}")
    #     etld_lib_functions.logger.error("Caught a KeyboardInterrupt, performing cleanup...")
    #     formatted_lines = traceback.format_exc().splitlines()
    #     etld_lib_functions.logger.error(f"TRACEBACK: {formatted_lines}")
    #     exit(1)
    # except SystemExit:
    #     time.sleep(10)
    #     etld_lib_functions.logger.error(f"Error host_list_detection_02_workflow_manager - "
    #                                     f"host_list_detection_etl_workflow, "
    #                                     f"please investigate {sys.argv}")
    #     etld_lib_functions.logger.error("Caught a SystemExit, performing cleanup...")
    #     formatted_lines = traceback.format_exc().splitlines()
    #     etld_lib_functions.logger.error(f"TRACEBACK: {formatted_lines}")
    #     exit(1)


def main():
    host_list_detection_etl_workflow()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_detection_02_workflow_manager')
    etld_lib_config.main()
    #etld_lib_credentials.main()
    etld_lib_authentication_objects.main()
    main()
