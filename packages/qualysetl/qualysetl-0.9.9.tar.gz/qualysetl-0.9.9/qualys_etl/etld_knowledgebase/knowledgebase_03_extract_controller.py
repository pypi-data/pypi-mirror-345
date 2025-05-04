#!/usr/bin/env python3
import time
import fcntl
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions
#from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_authentication_objects
from qualys_etl.etld_knowledgebase import knowledgebase_02_workflow_manager


def begin_knowledgebase_03_extract_controller():
    etld_lib_functions.logger.info(f"start")


def end_knowledgebase_03_extract_controller():
    etld_lib_functions.logger.info(f"end")


def knowledgebase_extract_controller(kb_last_modified_after=None, lock_file_required=False):
    if kb_last_modified_after is not None:
        etld_lib_config.kb_last_modified_after = kb_last_modified_after
    else:
        etld_lib_config.kb_last_modified_after = ""

    def get_knowledgebase_data(distribute_data=False):
        try:
            # knowledgebase_04_extract_wrapper(message=f"kb_last_modified_after={etld_lib_config.kb_last_modified_after}")
            knowledgebase_02_workflow_manager.knowledgebase_04_extract_wrapper(
                message=f"kb_last_modified_after={etld_lib_config.kb_last_modified_after}")
            if distribute_data:
                knowledgebase_02_workflow_manager.knowledgebase_05_transform_load_xml_to_sqlite_wrapper()
                knowledgebase_02_workflow_manager.knowledgebase_06_distribution_wrapper()
        except Exception as e2:
            etld_lib_functions.logger.warning(f"Error get_knowledgebase_data")
            etld_lib_functions.logger.warning(f"Exception: {e2}")
            raise Exception("Raise Exception from get_knowledgebase_data in knowledgebase_extract_controller")

    retry_attempts = 12
    retry_attempt = 0
    retry_sleep_time = 300
    while retry_attempt < retry_attempts:
        retry_attempt += 1
        try:
            if lock_file_required:
                with open(etld_lib_config.kb_lock_file, 'wb+') as lock_knowledgebase_fcntl:
                    fcntl.flock(lock_knowledgebase_fcntl, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    get_knowledgebase_data(distribute_data=True) # targeted run from other module.
                    break # Success
            else:
                get_knowledgebase_data(distribute_data=False) # Normal Run through spawn workflow
                break # Success
        except Exception as e:
            etld_lib_functions.logger.warning(f"Exception from knowledgebase_extract_controller.  {__file__} ")
            etld_lib_functions.logger.warning(f"Exception: {e}")
            etld_lib_functions.logger.warning(f"Retrying in {retry_sleep_time} seconds")
            time.sleep(retry_sleep_time)
    else:
        etld_lib_functions.logger.error(f"Retried {retry_attempt} times with no success.")
        etld_lib_functions.logger.error(f"Check to see if KnowledgeBase Program is already running.  {__file__} ")
        exit(1)


def main(kb_last_modified_after=None, lock_file_required=False):
    if kb_last_modified_after is None:
        kb_last_modified_after = etld_lib_config.kb_last_modified_after
    begin_knowledgebase_03_extract_controller()
    knowledgebase_extract_controller(kb_last_modified_after=kb_last_modified_after, lock_file_required=lock_file_required)
    end_knowledgebase_03_extract_controller()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='knowledgebase_extract_03_controller')
    etld_lib_config.main()
    #etld_lib_credentials.main()
    etld_lib_authentication_objects.main()
    main(lock_file_required=True)