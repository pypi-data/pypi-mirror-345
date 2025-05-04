import os
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config


def display_log_error_messages(error_messages_list):
    for error_message in error_messages_list:
        etld_lib_functions.logger.error(f"{error_message}")


def get_workflow_log_entry_dict(log_entry_line):
    log_entry_row_list = str(log_entry_line).split('|')
    log_entry_dict = {}
    if len(log_entry_row_list) == len(etld_lib_config.run_log_csv_columns()) and \
            log_entry_row_list[0].startswith("20"):
        for csv_index in range(len(etld_lib_config.run_log_csv_columns())):
            column_name = etld_lib_config.run_log_csv_columns()[csv_index]
            log_entry_dict[f'{column_name}'] = str(log_entry_row_list[csv_index]).strip()

        log_workflow_list = str(log_entry_dict['LOG_WORKFLOW']).split(':')
        if len(log_workflow_list) != 2:
            log_entry_dict['LOG_WORKFLOW_NAME'] = log_workflow_list[0]
            log_entry_dict['LOG_WORKFLOW_DATE'] = log_workflow_list[0]
        else:
            log_entry_dict['LOG_WORKFLOW_NAME'] = log_workflow_list[0]
            log_entry_dict['LOG_WORKFLOW_DATE'] = log_workflow_list[1]

        log_entry_dict['LOG_ROW_STRUCTURE_ISVALID'] = True
    else:
        log_entry_string = "".join(log_entry_line).strip()
        log_entry_dict['LOG_MESSAGE'] = f"UNBOUND LOG ERROR: {log_entry_string}"
        log_entry_dict['LOG_LEVEL'] = "ERROR"
        log_entry_dict['LOG_ROW_STRUCTURE_ISVALID'] = False

    return log_entry_dict


def get_workflow_log_last_entry(log_file):
    if not Path(log_file).is_file():
        etld_lib_functions.logger.error(
            f"Log File Doesn't Exist: {str(log_file)}, rerun after executing corresponding etl")
        raise FileNotFoundError(f"{str(log_file)}, rerun after executing corresponding etl")

    with open(str(log_file), "rb") as log_file_handle:
        try:
            log_file_handle.seek(-2, os.SEEK_END)
            while log_file_handle.read(1) != b'\n':
                log_file_handle.seek(-2, os.SEEK_CUR)
        except OSError:
            log_file_handle.seek(0)
        log_entry = log_file_handle.readline().decode()
        log_entry_dict = get_workflow_log_entry_dict(log_entry)
    return log_entry_dict


def get_workflow_log(log_file_path):
    last_log_entry_dict = get_workflow_log_last_entry(log_file_path)
    all_log_entries = []
    found_first_log_workflow = False
    if last_log_entry_dict['LOG_ROW_STRUCTURE_ISVALID']:
        with open(str(log_file_path), "rt", encoding='utf-8') as read_file:
            for log_entry_line in read_file:
                log_entry_dict = get_workflow_log_entry_dict(log_entry_line)
                if log_entry_dict['LOG_ROW_STRUCTURE_ISVALID']:
                    if str(log_entry_dict['LOG_WORKFLOW']).strip() == str(last_log_entry_dict['LOG_WORKFLOW']).strip():
                        all_log_entries.append(log_entry_dict)
                        found_first_log_workflow = True
                elif found_first_log_workflow:
                    # log_entry_dict = craft_log_out_of_bound_entry(last_log_entry_dict)
                    # Keep 'LOG_MESSAGE', 'LOG_LEVEL', change ['LOG_ROW_STRUCTURE_ISVALID'] = True
                    log_entry_dict['LOG_DATETIME'] = last_log_entry_dict['LOG_DATETIME']
                    log_entry_dict['LOG_WORKFLOW'] = last_log_entry_dict['LOG_WORKFLOW']
                    log_entry_dict['LOG_WORKFLOW_NAME'] = last_log_entry_dict['LOG_WORKFLOW_NAME']
                    log_entry_dict['LOG_WORKFLOW_DATE'] = last_log_entry_dict['LOG_WORKFLOW_DATE']
                    log_entry_dict['LOG_USERNAME'] = last_log_entry_dict['LOG_USERNAME']
                    log_entry_dict['LOG_FUNCTION'] = 'etld_lib_log_validation_out_of_bounds'
                    log_entry_dict['LOG_ROW_STRUCTURE_ISVALID'] = True
                    all_log_entries.append(log_entry_dict)
    else:
        # log_entry_dict = craft_log_out_of_bound_entry(last_log_entry_dict)
        # Completely out of bounds error.
        log_entry_dict = {
            'LOG_DATETIME': 'UNKNOWN',
            'LOG_LEVEL': 'ERROR',
            'LOG_MESSAGE': 'LAST LINE OF LOG FILE IS IN ERROR, PLEASE INVESTIGATE ISSUE',
            'LOG_WORKFLOW': 'UNKNOWN:UNKNOWN',
            'LOG_WORKFLOW_NAME': 'UNKNOWN',
            'LOG_WORKFLOW_DATE': 'UNKNOWN',
            'LOG_USERNAME': 'UNKNOWN',
            'LOG_FUNCTION': 'etld_lib_log_validation_completely_out_of_bounds',
            'LOG_ROW_STRUCTURE_ISVALID': True
        }
        all_log_entries.append(log_entry_dict)
    return all_log_entries


def test_workflow_spawned_process_ended(all_log_entries: list):
    etl_workflow_completed = False
    for log_entry_dict in all_log_entries:
        if str(log_entry_dict['LOG_FUNCTION']).strip() == 'spawn_etl_in_background' and \
                str(log_entry_dict['LOG_MESSAGE']).strip().__contains__('Spawned Process Succeeded'):
            etld_lib_functions.logger.info(f"{str(log_entry_dict['LOG_MESSAGE']).strip()}")
            etl_workflow_completed = True

    if etl_workflow_completed:
        pass
    else:
        etld_lib_functions.logger.error(f"ERROR: spawn_etl_in_background, not successful.")

    return etl_workflow_completed


def test_workflow_log_no_errors_found_thus_far(all_log_entries: list):
    etl_workflow_valid_flag = True
    error_messages_list = []
    for log_entry_dict in all_log_entries:
        if log_entry_dict['LOG_LEVEL'] == 'ERROR':
            error_messages_list.append(f"ERROR: {log_entry_dict['LOG_MESSAGE']}")
            etl_workflow_valid_flag = False

    if etl_workflow_valid_flag:
        etld_lib_functions.logger.info(f"Passed Tests: {all_log_entries[0]['LOG_WORKFLOW']} ")
    else:
        display_log_error_messages(error_messages_list=error_messages_list)

    return etl_workflow_valid_flag


def test_workflow_log_completed_successfully(all_log_entries: list):
    etl_workflow_valid_flag = True
    error_messages_list = []
    for log_entry_dict in all_log_entries:
        if log_entry_dict['LOG_LEVEL'] == 'ERROR':
            error_messages_list.append(f"ERROR: {log_entry_dict['LOG_MESSAGE']}")
            etl_workflow_valid_flag = False

    if etl_workflow_valid_flag:
        etld_lib_functions.logger.info(f"Passed Tests: {all_log_entries[0]['LOG_WORKFLOW']} ")
    else:
        display_log_error_messages(error_messages_list=error_messages_list)

    if test_workflow_spawned_process_ended(all_log_entries):
        pass
    else:
        etl_workflow_valid_flag = False

    return etl_workflow_valid_flag


def validate_log_has_no_errors(etl_workflow_option):
    etl_workflow_location_dict = \
        etld_lib_config.get_etl_workflow_data_location_dict(etl_workflow_option)
    all_log_entries = get_workflow_log(log_file_path=Path(etl_workflow_location_dict['log_file']))
    return test_workflow_log_completed_successfully(all_log_entries)


def validate_log_has_no_errors_prior_to_distribution(etl_workflow_option):
    # Called by in process programs before end of job.
    etl_workflow_location_dict = \
        etld_lib_config.get_etl_workflow_data_location_dict(etl_workflow_option)
    all_log_entries = get_workflow_log(log_file_path=Path(etl_workflow_location_dict['log_file']))
    return test_workflow_log_no_errors_found_thus_far(all_log_entries)


def main_validate_log_has_no_errors(etl_workflow):
    etld_lib_functions.main(my_logger_prog_name='main_validate_log_has_no_errors')
    etld_lib_config.main()
    passed_all_tests = validate_log_has_no_errors(etl_workflow_option=etl_workflow)
    if passed_all_tests:
        pass
    else:
        exit(2)

    return passed_all_tests


def main_validate_all_logs_have_no_errors():
    etld_lib_functions.main(my_logger_prog_name='main_validate_all_logs_have_no_errors')
    etld_lib_config.main()
    main()


def main():
    final_exit_status = 0
    etl_workflow_list = etld_lib_config.etl_workflow_list
    etl_workflow_list = ['test_system_etl_workflow']
    for etl_workflow in etl_workflow_list:
        passed_all_tests = \
            validate_log_has_no_errors(etl_workflow_option=etl_workflow)
        if passed_all_tests:
            pass
        else:
            final_exit_status = 2
    exit(final_exit_status)


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='etld_lib_log_validation')
    etld_lib_config.main()
    main()
