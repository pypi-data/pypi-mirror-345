#!/usr/bin/env python3
import sys
import timeit
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config
#from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_authentication_objects
from qualys_etl.etld_test_system import test_system_03_controller


global start_time
global stop_time


def test_system_03_extract_controller_wrapper(module_function=test_system_03_controller, message=""):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def begin_message():
    etld_lib_functions.logger.info(f"data directory: {etld_lib_config.qetl_user_data_dir}")


def begin_test_system_02_workflow_manager():
    global start_time
    start_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"__start__ test_system_etl_workflow {str(sys.argv)}")


def end_test_system_02_workflow_manager():
    global start_time
    global stop_time

    stop_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"runtime for test_system_etl_workflow in seconds: {stop_time - start_time:,}")
    etld_lib_functions.logger.info(f"__end__ test_system_etl_workflow {str(sys.argv)}")


def test_system_etl_workflow():
    try:
        begin_test_system_02_workflow_manager()
        test_system_03_controller.main()
        end_test_system_02_workflow_manager()
    except Exception as e:
        etld_lib_functions.logger.error(f"Error occurred, please investigate {sys.argv}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def main():
    test_system_etl_workflow()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='test_system_etl_workflow')
    etld_lib_config.main()
    #etld_lib_credentials.main()
    etld_lib_authentication_objects.main()
    main()