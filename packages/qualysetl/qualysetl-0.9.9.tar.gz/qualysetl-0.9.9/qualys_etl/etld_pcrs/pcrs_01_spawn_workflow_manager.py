#!/usr/bin/env python3
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_spawn_etl
from qualys_etl.etld_pcrs import pcrs_02_workflow_manager


# def main():
#     etld_lib_config.set_path_qetl_user_home_dir()
#     etld_lib_spawn_etl.log_dir = etld_lib_config.qetl_user_log_dir
#     etld_lib_spawn_etl.log_file_path = etld_lib_config.pcrs_log_file
#     etld_lib_spawn_etl.log_file_rotate_path = etld_lib_config.pcrs_log_rotate_file
#     etld_lib_spawn_etl.lock_file = etld_lib_config.pcrs_lock_file
#     etld_lib_spawn_etl.log_file_max_size = etld_lib_config.pcrs_log_file_max_size                                            # 1024 * size = Max Meg Size
#     etld_lib_spawn_etl.spawned_process_max_run_time = etld_lib_config.pcrs_spawned_process_max_run_time                      # seconds before terminate as there is an issue.
#     etld_lib_spawn_etl.spawned_process_sleep_time = etld_lib_config.pcrs_spawned_process_sleep_time                          # check every n seconds for spawned_process.is_alive()
#     etld_lib_spawn_etl.spawned_process_count_to_status_update = etld_lib_config.pcrs_spawned_process_count_to_status_update  # print status spawned_process.is_alive() after n checks
#     etld_lib_spawn_etl.etl_files_max_time_between_changes = etld_lib_config.pcrs_etl_files_max_time_between_changes
#
#
#     etld_lib_spawn_etl.etl_dir_to_monitor = etld_lib_config.qetl_user_data_dir
#
#     etld_lib_spawn_etl.target_module_to_run = pcrs_02_workflow_manager.pcrs_etl_workflow
#     etld_lib_spawn_etl.target_method_in_module_to_run = "pcrs_etl_workflow"
#     etld_lib_spawn_etl.etl_main()

def main():
    prefix_name = "pcrs"
    etld_lib_spawn_etl.etl_main(etl_workflow_prefix=prefix_name)

if __name__ == '__main__':
    main()
