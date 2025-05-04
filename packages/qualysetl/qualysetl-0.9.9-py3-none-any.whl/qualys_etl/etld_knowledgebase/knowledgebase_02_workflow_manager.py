#!/usr/bin/env python3
import sys
import timeit
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config
#from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_authentication_objects

from qualys_etl.etld_knowledgebase import knowledgebase_03_extract_controller
from qualys_etl.etld_knowledgebase import knowledgebase_04_extract
from qualys_etl.etld_knowledgebase import knowledgebase_05_transform_load_xml_to_sqlite
from qualys_etl.etld_knowledgebase import knowledgebase_06_distribution
#import traceback
import time

global start_time
global stop_time


def knowledgebase_03_extract_controller_wrapper(module_function=knowledgebase_03_extract_controller, message=""):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def knowledgebase_04_extract_wrapper(module_function=knowledgebase_04_extract, message=""):
    etld_lib_functions.logger.info(f"start {module_function} {message}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def knowledgebase_05_transform_load_xml_to_sqlite_wrapper(module_function=knowledgebase_05_transform_load_xml_to_sqlite):
    etld_lib_functions.logger.info(f"start {module_function}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def knowledgebase_06_distribution_wrapper(module_function=knowledgebase_06_distribution):
    etld_lib_functions.logger.info(f"start {module_function}")
    module_function.main()
    etld_lib_functions.logger.info(f"end   {module_function}")


def begin_knowledgebase_02_workflow_manager():
    global start_time
    start_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"__start__ knowledgebase_etl_workflow {str(sys.argv)}")
    etld_lib_functions.logger.info(f"data directory: {etld_lib_config.qetl_user_data_dir}")


def end_knowledgebase_02_workflow_manager():
    global start_time
    global stop_time

    stop_time = timeit.default_timer()
    etld_lib_functions.logger.info(f"runtime for knowledgebase_etl_workflow in seconds: {stop_time - start_time:,}")
    etld_lib_functions.logger.info(f"__end__ knowledgebase_etl_workflow {str(sys.argv)}")


def knowledgebase_etl_workflow():
    try:
        begin_knowledgebase_02_workflow_manager()
        knowledgebase_03_extract_controller_wrapper()
        knowledgebase_05_transform_load_xml_to_sqlite_wrapper()
        knowledgebase_06_distribution_wrapper()
        end_knowledgebase_02_workflow_manager()
    except Exception as e:
        time.sleep(10)
        etld_lib_functions.logger.error(f"Error knowledgebase_02_workflow_manager - knowledgebase_etl_workflow, "
                                        f"please investigate {sys.argv}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)
    #     formatted_lines = traceback.format_exc().splitlines()
    #     etld_lib_functions.logger.error(f"TRACEBACK: {formatted_lines}")
    #     exit(1)
    # except KeyboardInterrupt:
    #     time.sleep(10)
    #     etld_lib_functions.logger.error(f"Error knowledgebase_02_workflow_manager - knowledgebase_etl_workflow, "
    #                                     f"please investigate {sys.argv}")
    #     etld_lib_functions.logger.error("Caught a KeyboardInterrupt, performing cleanup...")
    #     formatted_lines = traceback.format_exc().splitlines()
    #     etld_lib_functions.logger.error(f"TRACEBACK: {formatted_lines}")
    #     exit(1)
    # except SystemExit:
    #     time.sleep(10)
    #     etld_lib_functions.logger.error(f"Error knowledgebase_02_workflow_manager - knowledgebase_etl_workflow, "
    #                                     f"please investigate {sys.argv}")
    #     etld_lib_functions.logger.error("Caught a SystemExit, performing cleanup...")
    #     formatted_lines = traceback.format_exc().splitlines()
    #     etld_lib_functions.logger.error(f"TRACEBACK: {formatted_lines}")
    #     exit(1)


def main():
    knowledgebase_etl_workflow()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name="knowledgebase_02_workflow_manager")
    etld_lib_config.main()
    #etld_lib_credentials.main()
    etld_lib_authentication_objects.main()
    main()
