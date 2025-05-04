#!/usr/bin/env python3
import sys
import timeit
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config
#from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_authentication_objects

from qualys_etl.etld_host_list import host_list_03_extract_controller
from qualys_etl.etld_host_list import host_list_06_distribution
import time

global start_time
global stop_time


def host_list_03_extract_controller_wrapper(module_function=host_list_03_extract_controller, message=""):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def host_list_06_distribution_wrapper(
        module_function=host_list_06_distribution, message=""):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def begin_message_info():
    etld_lib_functions.logger.info(f"data directory: {etld_lib_config.qetl_user_data_dir}")


def begin_host_list_02_workflow_manager():
    global start_time
    start_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"__start__ host_list_etl_workflow {str(sys.argv)}")
    begin_message_info()

# def host_list_start_wrapper():
#     global start_time
#     start_time = timeit.default_timer()
#     etld_lib_functions.logger.info(f"__start__ host_list_etl_workflow {str(sys.argv)}")
#     etld_lib_functions.logger.info(f"data directory: {etld_lib_config.qetl_user_data_dir}")
#     etld_lib_functions.logger.info(f"config file:    {etld_lib_config.qetl_user_config_settings_yaml_file}")
#     etld_lib_functions.logger.info(f"cred yaml file: {etld_lib_credentials.cred_file}")
#     etld_lib_functions.logger.info(f"cookie file:    {etld_lib_credentials.cookie_file}")

def end_host_list_02_workflow_manager():
    global start_time
    global stop_time

    stop_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"runtime for host_list_etl_workflow in seconds: {stop_time - start_time:,}")
    etld_lib_functions.logger.info(f"__end__ host_list_etl_workflow {str(sys.argv)}")

# def host_list_end_wrapper():
#     global start_time
#     global stop_time
#
#     stop_time = timeit.default_timer()
#     etld_lib_functions.logger.info(f"runtime for host_list_etl_workflow in seconds: {stop_time - start_time:,}")
#     etld_lib_functions.logger.info(f"__end__ host_list_etl_workflow {str(sys.argv)}")


def host_list_etl_workflow():
    try:
        begin_host_list_02_workflow_manager()
        host_list_03_extract_controller_wrapper(
            message=f"vm_processed_after={etld_lib_config.host_list_vm_processed_after}")
        host_list_06_distribution_wrapper()
        end_host_list_02_workflow_manager()
    except Exception as e:
        time.sleep(10)
        etld_lib_functions.logger.error(f"Error host_list_02_workflow_manager - host_list_etl_workflow, "
                                        f"please investigate {sys.argv}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def main():
    host_list_etl_workflow()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_02_workflow_manager')
    etld_lib_config.main()
    #etld_lib_credentials.main()
    etld_lib_authentication_objects.main()
    main()
