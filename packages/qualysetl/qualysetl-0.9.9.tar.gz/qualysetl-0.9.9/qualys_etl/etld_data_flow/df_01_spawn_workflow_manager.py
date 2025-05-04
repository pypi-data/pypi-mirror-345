#!/usr/bin/env python3
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_spawn_etl
from qualys_etl.etld_data_flow import df_02_workflow_manager


def main():
    prefix_name = etld_lib_config.df_workflow_prefix_name # Set in qetl_manage_user
    etld_lib_spawn_etl.etl_main(etl_workflow_prefix=prefix_name)

if __name__ == '__main__':
    main()
