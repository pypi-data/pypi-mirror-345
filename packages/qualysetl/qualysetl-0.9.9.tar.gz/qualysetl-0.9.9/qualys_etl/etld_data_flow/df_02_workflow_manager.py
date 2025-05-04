#!/usr/bin/env python3
import sys
import timeit
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config
#from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_authentication_objects

from qualys_etl.etld_pcrs import pcrs_03_extract_controller
from qualys_etl.etld_pcrs import pcrs_05_transform_load_json_to_sqlite
from qualys_etl.etld_pcrs import pcrs_06_distribution
import traceback
import time

global start_time
global stop_time


def pcrs_03_extract_controller_wrapper(
        module_function=pcrs_03_extract_controller, message=""
):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def pcrs_05_transform_load_json_to_sqlite_wrapper(
        module_function=pcrs_05_transform_load_json_to_sqlite, message=""
):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def pcrs_06_distribution_wrapper(
        module_function=pcrs_06_distribution, message=""):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def begin_pcrs_02_workflow_manager():
    global start_time
    start_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"__start__ pcrs_etl_workflow {str(sys.argv)}")


def end_pcrs_workflow_manager():
    global start_time
    global stop_time

    stop_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"runtime for pcrs_etl_workflow in seconds: {stop_time - start_time:,}")
    etld_lib_functions.logger.info(f"__end__ pcrs_etl_workflow {str(sys.argv)}")


def pcrs_etl_workflow():
    try:
        begin_pcrs_02_workflow_manager()
        pcrs_03_extract_controller_wrapper(
            message=f"pcrs_hostids_last_scan_date={etld_lib_config.pcrs_last_scan_date}")
        pcrs_06_distribution_wrapper()
        end_pcrs_workflow_manager()
    except Exception as e:
        time.sleep(10)
        etld_lib_functions.logger.error(f"Error pcrs_02_workflow_manager - pcrs_etl_workflow, "
                                        f"please investigate {sys.argv}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)
    #     formatted_lines = traceback.format_exc().splitlines()
    #     etld_lib_functions.logger.error(f"TRACEBACK: {formatted_lines}")
    #     exit(1)
    # except KeyboardInterrupt:
    #     time.sleep(10)
    #     etld_lib_functions.logger.error(f"Error pcrs_02_workflow_manager - pcrs_etl_workflow, "
    #                                     f"please investigate {sys.argv}")
    #     etld_lib_functions.logger.error("Caught a KeyboardInterrupt, performing cleanup...")
    #     formatted_lines = traceback.format_exc().splitlines()
    #     etld_lib_functions.logger.error(f"TRACEBACK: {formatted_lines}")
    #     exit(1)
    # except SystemExit:
    #     time.sleep(10)
    #     etld_lib_functions.logger.error(f"Error pcrs_02_workflow_manager - pcrs_etl_workflow, "
    #                                     f"please investigate {sys.argv}")
    #     etld_lib_functions.logger.error("Caught a SystemExit, performing cleanup...")
    #     formatted_lines = traceback.format_exc().splitlines()
    #     etld_lib_functions.logger.error(f"TRACEBACK: {formatted_lines}")
    #     exit(1)
    #

def main():
    pcrs_etl_workflow()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='pcrs_02_workflow_manager')
    etld_lib_config.main()
    #etld_lib_credentials.main()
    etld_lib_authentication_objects.main()
    main()
