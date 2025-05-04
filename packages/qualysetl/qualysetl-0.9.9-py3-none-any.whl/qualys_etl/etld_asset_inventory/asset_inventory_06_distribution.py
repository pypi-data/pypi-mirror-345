#!/usr/bin/env python3
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_csv_distribution


def begin_asset_inventory_06_distribution():
    etld_lib_functions.logger.info(f"start")


def end_asset_inventory_06_distribution():
    etld_lib_functions.logger.info(f"end")


def extract_csv_from_database(test_extract=False):
    etld_lib_functions.logger.info(f"test_extract={test_extract}, "
                                   f"test_system={etld_lib_config.test_system_do_not_test_intermediary_extracts_flag}")
    if test_extract or etld_lib_config.test_system_do_not_test_intermediary_extracts_flag:
        etld_lib_csv_distribution.distribute_csv_data_for_one_workflow(
            distribution_csv_flag=etld_lib_config.asset_inventory_distribution_csv_flag,
            etl_workflow='asset_inventory_06_distribution',
            distribution_csv_flag_name='asset_inventory_distribution_csv_flag'
        )
    else:
        etld_lib_csv_distribution.distribute_csv_data_for_one_workflow(
            distribution_csv_flag=etld_lib_config.asset_inventory_distribution_csv_flag,
            etl_workflow='asset_inventory_etl_workflow',
            distribution_csv_flag_name='asset_inventory_distribution_csv_flag',
            exclude_table_names=['Q_Asset_Inventory']
        )


def main(test_extract=False):
    begin_asset_inventory_06_distribution()
    extract_csv_from_database(test_extract)
    end_asset_inventory_06_distribution()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='asset_inventory_06_distribution')
    etld_lib_config.main()
    main(test_extract=True)
