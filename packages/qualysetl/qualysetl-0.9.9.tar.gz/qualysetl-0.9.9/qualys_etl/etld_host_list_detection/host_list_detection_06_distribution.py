#!/usr/bin/env python3
from qualys_etl.etld_lib import etld_lib_config
#from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_authentication_objects
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_csv_distribution


def begin_host_list_detection_06_distribution():
    etld_lib_functions.logger.info(f"start")


def end_host_list_detection_06_distribution():
    etld_lib_functions.logger.info(f"end")


def extract_csv_from_database(test_extract=False):
    etld_lib_functions.logger.info(f"test_extract={test_extract}, "
                                   f"test_system={etld_lib_config.test_system_do_not_test_intermediary_extracts_flag}")
    if test_extract or etld_lib_config.test_system_do_not_test_intermediary_extracts_flag:
        # Including Q_Host_List_Detection_HOSTS, Q_Host_List_Detection_QIDS
        # Test Run
        etld_lib_csv_distribution.distribute_csv_data_for_one_workflow(
            distribution_csv_flag=etld_lib_config.host_list_detection_distribution_csv_flag,
            etl_workflow='host_list_detection_06_distribution',
            distribution_csv_flag_name='host_list_detection_distribution_csv_flag',
        )
    else:
        # Excluding Q_Host_List_Detection_HOSTS, Q_Host_List_Detection_QIDS
        # Production Run
        etld_lib_csv_distribution.distribute_csv_data_for_one_workflow(
            distribution_csv_flag=etld_lib_config.host_list_detection_distribution_csv_flag,
            etl_workflow='host_list_detection_etl_workflow',
            distribution_csv_flag_name='host_list_detection_distribution_csv_flag',
            exclude_table_names=['Q_Host_List_Detection_HOSTS', 'Q_Host_List_Detection_QIDS']
        )


def main(test_extract=False):
    begin_host_list_detection_06_distribution()
    extract_csv_from_database(test_extract)
    end_host_list_detection_06_distribution()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_detection_06_distribution')
    etld_lib_config.main()
    #etld_lib_credentials.main()
    etld_lib_authentication_objects.main()
    main(test_extract=True)
