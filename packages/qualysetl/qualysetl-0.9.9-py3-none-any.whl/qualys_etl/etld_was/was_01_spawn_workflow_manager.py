#!/usr/bin/env python3
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_spawn_etl
from qualys_etl.etld_was import was_02_workflow_manager


# def main():
#     prefix_name = "was_"
#     etld_lib_config.set_path_qetl_user_home_dir()
#     etld_lib_spawn_etl.log_dir = etld_lib_config.qetl_user_log_dir
#     etld_lib_spawn_etl.etl_dir_to_monitor = etld_lib_config.qetl_user_data_dir
#     etld_lib_spawn_etl.log_file_path = getattr(etld_lib_config, f"{prefix_name}log_file")
#     etld_lib_spawn_etl.log_file_rotate_path = getattr(etld_lib_config, f"{prefix_name}log_rotate_file")
#     etld_lib_spawn_etl.lock_file = getattr(etld_lib_config, f"{prefix_name}lock_file")
#     etld_lib_spawn_etl.log_file_max_size = getattr(etld_lib_config, f"{prefix_name}log_file_max_size")                          # 1024 * size = Max Meg Size
#     etld_lib_spawn_etl.spawned_process_max_run_time = getattr(etld_lib_config, f"{prefix_name}spawned_process_max_run_time")    # seconds before terminate as there is an issue.
#     etld_lib_spawn_etl.spawned_process_sleep_time = getattr(etld_lib_config, f"{prefix_name}spawned_process_sleep_time")        # check every n seconds for spawned_process.is_alive()
#     etld_lib_spawn_etl.spawned_process_count_to_status_update = getattr(etld_lib_config, f"{prefix_name}spawned_process_count_to_status_update")  # print status spawned_process.is_alive() after n checks
#     etld_lib_spawn_etl.etl_files_max_time_between_changes = getattr(etld_lib_config, f"{prefix_name}etl_files_max_time_between_changes")
#     etld_lib_spawn_etl.target_module_to_run = getattr(f"{prefix_name}02_workflow_manager", f"{prefix_name}etl_workflow")
#     etld_lib_spawn_etl.target_method_in_module_to_run = f"{prefix_name}etl_workflow"
#     etld_lib_spawn_etl.etl_main()

def main():
    prefix_name = "was"
    etld_lib_spawn_etl.etl_main(etl_workflow_prefix=prefix_name)

if __name__ == '__main__':
    main()
