import datetime
import inspect
import logging
import sys
import os
import getpass
import psutil
from importlib import util as importlib_util
import time
import re
from pathlib import Path
import timeit
import string
import unicodedata

global logger
global logging_is_on_flag

global logger_datetime
global logger_workflow_datetime
global logger_iso_format_datetime
global logger_database_format_datetime
global my_logger_program_name_for_database_routine

global logger_to_file
global logging_level
global qetl_code_dir        # Parent of qualys_etl directory
global qetl_code_dir_etld_cred_yaml_template_path
global qetl_code_dir_child  # qualys_etl directory
global qetl_pip_installed_version  # qetl installed through pip
import qualys_etl

logging_is_on_flag = False


def set_qetl_code_dir_etld_cred_yaml_template_path():
    global qetl_code_dir_etld_cred_yaml_template_path
    qetl_code_dir_etld_cred_yaml_template_path = \
        Path(qetl_code_dir, "qualys_etl", "etld_templates", ".etld_cred.yaml")

def logger_start_and_stop_function_name_decorator(f):
    #
    # Experimental sending start and finish to logger.
    # @logger_start_and_stop_function_name_decorator
    # def fun_name():
    #     print("blah")
    #
    def new_f(*args, **kwargs):
        logger.info("starting", f.__name__)
        f(*args, **kwargs)
        logger.info("finished", f.__name__)
    return new_f

def check_python_version():
    py_version = sys.version.split('\n')
    try:
        if (sys.version_info[0] >= 3) and (sys.version_info[1] >= 8):
            logger.info(f"Python version found is: {py_version}")
        else:
            logger.info("Error: sys.version.info failed.  Please use Python version 3.8 or greater.")
            raise ValueError(f"Python version < 3.8 found: {py_version}")
    except Exception as e:
        logger.error(f"Please install a version of python that can work with this product.")
        logger.error(f"Exception: {e}")
        exit(1)


def get_file_size(path_to_file):
    if Path(path_to_file).is_file():
        return Path(path_to_file).stat().st_size


def get_file_mtime(path_to_file):
    if Path(path_to_file).is_file():
        statinfo = Path(path_to_file).stat()
        return statinfo.st_mtime


def get_sqlite_version():
    global logger
    import sqlite3
    version_info = sqlite3.sqlite_version_info
    if (version_info[0] >= 3) and (version_info[1] >= 26):
        logger.info(f"SQLite version found is: {sqlite3.sqlite_version}.")
    else:
        logger.error(f"SQLite version {sqlite3.sqlite_version} is older than 3.31. Please upgrade sqlite.")
        exit(1)

    return sqlite3.version


def setup_logging_stdout(log_level=logging.INFO, my_logger_prog_name=None):
    global logger
    global logging_is_on_flag
    global logger_datetime
    global logger_workflow_datetime
    global logger_iso_format_datetime
    global logger_database_format_datetime
    global my_logger_program_name_for_database_routine

    logging_is_on_flag = True
    logging.Formatter.converter = time.gmtime
    d = datetime.datetime.utcnow()
    td = f"{d.year}{d.month:02d}{d.day:02d}{d.hour:02d}{d.minute:02d}{d.second:02d}"
    logger_datetime = td
    logger_iso_format_datetime = f"{d.year}-{d.month:02d}-{d.day:02d}T{d.hour:02d}:{d.minute:02d}:{d.second:02d}Z"
    logger_database_format_datetime = f"{d.year}-{d.month:02d}-{d.day:02d} {d.hour:02d}:{d.minute:02d}:{d.second:02d}"
    my_logger_program_name_for_database_routine = my_logger_prog_name
    username = getpass.getuser()
    prog = Path(__file__).name
    if my_logger_prog_name is not None:
        prog = my_logger_prog_name

    prog = f"{prog}: {logger_datetime}"
    logger_workflow_datetime = prog

    logging.basicConfig(format=f"%(asctime)s | %(levelname)-8s | {prog:54s} | {username:15} | %(funcName)-60s | %(message)s",
                        level=log_level,)

    logger = logging.getLogger()  # Useful in qetl_manage_user when we want to set the name.
    logger.info(f"PROGRAM:     {sys.argv}")
    logger.info(f"QUALYSETL VERSION: {qualys_etl.__version__}")
    logger.info(f"LOGGING SUCCESSFULLY SETUP FOR STREAMING")


def lineno():
    return inspect.currentframe().f_back.f_lineno


def check_modules():
    try:
        import requests
        # 2023-05-13 import oschmod
        import yaml
        import xmltodict
        # 2023-05-18 import boto3
        import base64
        import shutil
        import chardet
    except ImportError as e:
        logger.error(f"Missing Required Module: {e}")
        logger.error(f"Please review installation instructions and ensure you have all required modules installed.")
        exit(1)


def set_qetl_code_dir(log=True): # Module Directories
    global qetl_code_dir         # Parent of qualys_etl directory
    global qetl_code_dir_child   # qualys_etl directory

    test_exec_for_qetl_code_dir = __file__
    test_spec_for_qetl_code_dir = importlib_util.find_spec("qualys_etl")  # Installed on system

    result = ""
    if test_exec_for_qetl_code_dir.__contains__("qualys_etl"):
        result = re.sub("qualys_etl.*", '', test_exec_for_qetl_code_dir)
    elif test_spec_for_qetl_code_dir is not None:
        result = re.sub("qualys_etl.*", '', test_spec_for_qetl_code_dir.origin)
    else:
        logger.error(f"test_exec_for_qetl_code_dir - {test_exec_for_qetl_code_dir}")
        logger.error(f"test_spec_for_qetl_code_dir  - {test_spec_for_qetl_code_dir}")
        logger.error(f"Could not determine qetl code directory location.")
        logger.error(f"Please execute qetl_manage_users.py to test user")
        exit(1)

    # Module Directories
    qetl_code_dir = Path(result)
    qetl_code_dir_child = Path(qetl_code_dir, "qualys_etl")
    qetl_code_dir_child_api_host_list = Path(qetl_code_dir_child, "etld_host_list")
    qetl_code_dir_child_api_knowledgebase = Path(qetl_code_dir_child, "etld_knowledgebase")
    qetl_code_dir_child_api_lib = Path(qetl_code_dir_child, "etld_lib")
    qetl_code_dir_child_api_templates = Path(qetl_code_dir_child, "etld_templates")

    # Ensure modules are on sys.path
    modules = [qetl_code_dir_child, qetl_code_dir_child_api_lib, qetl_code_dir_child_api_templates,
               qetl_code_dir_child_api_knowledgebase, qetl_code_dir_child_api_host_list]
    for path in modules:
        if not sys.path.__contains__(str(path.absolute())):
            sys.path.insert(0, str(path))

    logger.info(f"qualysetl app dir    - {qetl_code_dir}")
    logger.info(f"qualys_etl code dir  - {qetl_code_dir_child}")
    logger.info(f"etld_lib             - {qetl_code_dir_child_api_lib}")
    logger.info(f"etld_templates       - {qetl_code_dir_child_api_templates}")
    logger.info(f"etld_knowledgebase   - {qetl_code_dir_child_api_knowledgebase}")
    logger.info(f"etld_host_list        - {qetl_code_dir_child_api_host_list}")


def get_formatted_file_info_dict(file_name):
    file_path = Path(file_name)
    if file_path.is_file():
        file_size = human_readable_size(Path(file_name).stat().st_size)
        file_change_time = Path(file_name).stat().st_ctime
        d = datetime.datetime.fromtimestamp(file_change_time)
        td = f"{d.year}-{d.month:02d}-{d.day:02d} {d.hour:02d}:{d.minute:02d}:{d.second:02d} local timezone"
        return {'file_size': file_size, 'file_change_time': td}
    else:
        return {'file_size': '', 'file_change_time': ''}


def human_readable_size(size_in_bytes):
    my_bytes = float(size_in_bytes)
    kilobytes = float(1024)
    megabytes = float(kilobytes ** 2)
    gigabytes = float(kilobytes ** 3)
    terabytes = float(kilobytes ** 4)
    petabytes = float(kilobytes ** 5)

    if my_bytes < kilobytes:
        message = 'bytes' if 0 == my_bytes > 1 else 'byte'
        return f'{my_bytes} {message}'
    elif kilobytes <= my_bytes < megabytes:
        return f'{(my_bytes / kilobytes):0.2f} kilobytes'
    elif megabytes <= my_bytes < gigabytes:
        return f'{(my_bytes / megabytes):0.2f} megabytes'
    elif gigabytes <= my_bytes < terabytes:
        return f'{(my_bytes / gigabytes):0.2f} gigabytes'
    elif terabytes <= my_bytes:
        return f'{(my_bytes / terabytes):0.2f} terabytes'
    elif petabytes <= my_bytes:
        return f'{(my_bytes / petabytes):0.2f} petabytes'


def log_file_info(file_name, msg1='output file'):
    file_info = get_formatted_file_info_dict(file_name)
    logger.info(f"{msg1} - {str(file_name)} size: {file_info.get('file_size')} "
                f"change time: {file_info.get('file_change_time')}")




class DisplayCounterToLog:
    # TODO Create method to display counters as json.
    # {"Q_Host_List": "283,129", "Q_Host_List_Detection_HOSTS": "171,452","Q_Host_List_Detection_QIDS": "1,335,871"}
    def __init__(self, display_counter_at=10000, logger_func=None, display_counter_log_message="count"):
        self.counter = 0
        self.display_counter = 0
        self.batch_name = ''
        self.batch_number = 0
        self.batch_date = ''
        self.status_table_name = 'TABLE_NAME'
        self.status_name_column = 'TABLE_NAME_LOAD_STATUS'
        self.display_counter_at = display_counter_at
        self.logger_func = logger_func
        self.display_counter_log_message = display_counter_log_message

    def update_counter(self):
        self.counter += 1
        self.display_counter += 1

    def get_counter(self):
        return self.counter

    def get_batch_name(self):
        return self.batch_name

    def set_batch_name(self, batch_name):
        self.batch_name = batch_name

    def get_batch_number(self):
        return self.batch_number

    def get_batch_date(self):
        return self.batch_date

    def set_batch_date(self, batch_date):
        self.batch_date = batch_date

    def get_status_table_name(self):
        return self.status_table_name

    def get_status_name_column(self):
        return self.status_name_column

    def update_batch_info(self, batch_name, batch_number, batch_date, status_table_name, status_name_column):
        self.batch_name = batch_name
        self.batch_number = batch_number
        self.batch_date = batch_date
        self.status_table_name = status_table_name
        self.status_name_column = status_name_column

    def get_batch_info(self):
        return {
            'batch_name': self.batch_name,
            'batch_number': self.batch_number,
            'batch_date': self.batch_date,
            'etl_workflow_status_table_name': self.status_table_name,
            'status_name_column': self.status_name_column
        }

    def update_counter_and_display_to_log(self):
        self.update_counter()
        if self.display_counter >= self.display_counter_at:
            self.display_counter = 0
            if self.logger_func is None:
                print(f"{self.display_counter_log_message}: {self.counter:,}")
            else:
                self.logger_func(f"{self.display_counter_log_message}: {self.counter:,}")

    def display_final_counter_to_log(self):
        if self.logger_func is None:
            print(f"{self.display_counter_log_message} - Total: {self.counter:,}")
        else:
            self.logger_func(f"{self.display_counter_log_message} - Total: {self.counter:,}")

    def display_counter_to_log(self):
        if self.logger_func is None:
            print(f"{self.display_counter_log_message} - Updated: {self.counter:,}")
        else:
            self.logger_func(f"{self.display_counter_log_message} - Updated: {self.counter:,}")


def log_system_information(logger_method=print, data_directory="/opt/qetl/users"):
    # TODO Calculate final averages of cpu, mem usage.
    sys_stat_counters = {
        'cpu_usage_pct': get_cpu_usage_pct(),
        'cpu_frequency': get_cpu_frequency(),
        'cpu_count': get_cpu_count(),
        'ram_usage_pct': get_ram_usage_pct(),
        'ram_size_total_in_mb': get_ram_size_total_in_mb(),
        'ram_size_usage_in_mb': get_ram_size_usage_in_mb(),
        'ram_size_available_in_mb': get_ram_size_available_in_mb(),
        'swap_usage_pct': get_swap_usage_pct(),
        'swap_size_total_in_mb': get_swap_size_total_in_mb(),
        'swap_size_usage_in_mb': get_swap_size_usage_in_mb(),
        'swap_size_available_in_mb': get_swap_size_available_in_mb(),
        'disk_usage_pct': 0,
        'disk_size_total_in_mb': 0,
        'disk_size_usage_in_mb': 0,
        'disk_size_available_in_mb': 0,
    }

    logger_method(
        f'SYS STAT: CPU usage={sys_stat_counters["cpu_usage_pct"]} %, '
        f'frequency='
        f'{sys_stat_counters["cpu_frequency"]} MHz, '
        f'count='
        f'{sys_stat_counters["cpu_count"]}'
    )
    logger_method(
        f'SYS STAT: RAM usage='
        f'{sys_stat_counters["ram_usage_pct"]} %, '
        f'total='
        f'{sys_stat_counters["ram_size_total_in_mb"]:,.0f} MB, '
        f'used='
        f'{sys_stat_counters["ram_size_usage_in_mb"]:,.0f} MB, '
        f'available='
        f'{sys_stat_counters["ram_size_available_in_mb"]:,.0f} MB '
    )
    logger_method(
        f'SYS STAT: SWAP usage='
        f'{sys_stat_counters["swap_usage_pct"]} %, '
        f'total='
        f'{sys_stat_counters["swap_size_total_in_mb"]:,.0f} MB, '
        f'used='
        f'{sys_stat_counters["swap_size_usage_in_mb"]:,.0f} MB, '
        f'available='
        f'{sys_stat_counters["swap_size_available_in_mb"]:,.0f} MB '
    )

    try:
        disk_usage_pct = get_disk_usage_pct(data_dir=data_directory)
        disk_size_total_in_mb = get_disk_size_total_in_mb(data_dir=data_directory)
        disk_size_usage_in_mb = get_disk_size_usage_in_mb(data_dir=data_directory)
        disk_size_available_in_mb = get_disk_size_available_in_mb(data_dir=data_directory)
        sys_stat_counters['disk_usage_pct'] = disk_usage_pct
        sys_stat_counters['disk_size_total_in_mb'] = disk_size_total_in_mb
        sys_stat_counters['disk_size_usage_in_mb'] = disk_size_usage_in_mb
        sys_stat_counters['disk_size_available_in_mb'] = disk_size_available_in_mb
        logger_method(
            f'SYS STAT: DISK usage='
            f'{sys_stat_counters["disk_usage_pct"]} %, '
            f'total='
            f'{sys_stat_counters["disk_size_total_in_mb"]:,.0f} MB, '
            f'used='
            f'{sys_stat_counters["disk_size_usage_in_mb"]:,.0f} MB, '
            f'available='
            f'{sys_stat_counters["disk_size_available_in_mb"]:,.0f} MB, '
            f'path='
            f'{data_directory}, '
        )
    except Exception as e:
        pass

    return sys_stat_counters


def if_disk_space_usage_greater_than_90_log_warning(logger_method=print, data_directory="/opt/qetl/users"):
    try:
        disk_size_usage_pct = int(get_disk_usage_pct(data_dir=data_directory))
        if disk_size_usage_pct > 90:
            logger_method(f'SYS WARNING: DISK percent usage > 90% at {disk_size_usage_pct}%')
    except Exception as e:
        pass


def if_swap_space_total_is_zero_abort(logger_method=print):
    if int(get_swap_size_total_in_mb()) > 0:
        pass
    else:
        logger_method(f'SYS ERROR: Please contact your systems administrator to configure swap space.')
        logger_method(f'SYS ERROR: Swap space is usually 4GB to 8GB depending on memory allocated and OS.')
        logger_method(f'SYS ERROR: current swap space size is: {get_swap_size_total_in_mb():,.0f} MB, ')
        exit(1)


def if_swap_space_total_is_low_log_warning(logger_method=print):
    if int(get_swap_size_total_in_mb()) < 4000:
        logger_method(f'SYS WARNING: SWAP size total is < 4 Gig. '
                      f'Consider increasing SWAP to support larger batch jobs and sql queries')


def if_ram_space_size_is_low_log_warning(logger_method=print):
    ram_size_total_in_mb = int(get_ram_size_total_in_mb())
    if ram_size_total_in_mb < 8100:
        logger_method(f'SYS WARNING: RAM size total < 8 Gig.  '
                      f'Consider increasing RAM to support larger batch jobs and sql queries')


def get_disk_usage_pct(data_dir="/opt/qetl/users"):
    return psutil.disk_usage(data_dir).percent


def get_disk_size_total_in_mb(data_dir="/opt/qetl/users"):
    return int(psutil.disk_usage(data_dir).total / 1024 / 1024)


def get_disk_size_usage_in_mb(data_dir="/opt/qetl/users"):
    return int(psutil.disk_usage(data_dir).used / 1024 / 1024)


def get_disk_size_available_in_mb(data_dir="/opt/qetl/users"):
    total_disk_space = psutil.disk_usage(data_dir).total / 1024 / 1024
    used_disk_space = psutil.disk_usage(data_dir).used / 1024 / 1024
    available_disk_space = total_disk_space - used_disk_space
    return int(available_disk_space)


def get_cpu_usage_pct():
    return psutil.cpu_percent(interval=0.5)


def get_cpu_frequency():
    return int(psutil.cpu_freq().current)


def get_cpu_count():
    return int(psutil.cpu_count())


def get_ram_size_usage_in_mb():
    return int(psutil.virtual_memory().total - psutil.virtual_memory().available) / 1024 / 1024


def get_ram_size_total_in_mb():
    return int(psutil.virtual_memory().total) / 1024 / 1024


def get_ram_usage_pct():
    return psutil.virtual_memory().percent


def get_ram_size_available_in_mb():
    return int(psutil.virtual_memory().available) / 1024 / 1034


def get_swap_size_usage_in_mb():
    return int(psutil.swap_memory().used) / 1024 / 1024


def get_swap_size_total_in_mb():
    return int(psutil.swap_memory().total) / 1024 / 1024


def get_swap_size_available_in_mb():
    total_swap_space = psutil.swap_memory().total / 1024 / 1024
    used_swap_space = psutil.swap_memory().used / 1024 / 1024
    available_swap_space = total_swap_space - used_swap_space
    return int(available_swap_space)


def get_swap_usage_pct():
    return psutil.swap_memory().percent

def replace_non_printable_with_hex(input_string):
    result = []
    for char in input_string:
        if char in string.printable:
            result.append(char)
        else:
            hex_representation = f"\\x{ord(char):02x}"
            result.append(hex_representation)
    return ''.join(result)


def remove_values_from_string(input_string, values_to_remove):
    for value in values_to_remove:
        input_string = input_string.replace(value, '')
    return input_string


def find_non_printable_ascii_characters(input_string):
    # Non Printable Ascii or UTF-8 characters outside ascii set.
    non_printable_chars = []

    for char in input_string:
        if char not in string.printable:
            hex_representation = format(ord(char), "x")
            non_printable_chars.append(f"\\x{hex_representation}")
    return non_printable_chars


def find_non_printable_unicode_characters_with_description(input_string):
    non_printable_chars_with_desc = []

    for char in input_string:
        if char not in string.printable and not char.isspace():
            unicode_point = ord(char)
            char_name = unicodedata.name(char, f"Unknown (U+{unicode_point:04X})")
            if unicode_point <= 0xFFFF:
                hex_representation = f"\\u{unicode_point:04x}"
            else:
                hex_representation = f"\\U{unicode_point:08x}"
            non_printable_chars_with_desc.append(f"{hex_representation} ({char_name})")
    return non_printable_chars_with_desc


def find_unique_unicode_characters_with_description(input_string):
    seen = set()
    unique_non_printable_chars_with_desc = []

    for char in input_string:
        if char not in string.printable and not char.isspace() and char not in seen:
            seen.add(char)
            unicode_point = ord(char)
            char_name = unicodedata.name(char, f"Unknown (U+{unicode_point:04X})")
            if unicode_point <= 0xFFFF:
                hex_representation = f"\\u{unicode_point:04x}"
            else:
                hex_representation = f"\\U{unicode_point:08x}"
            unique_non_printable_chars_with_desc.append(f"{hex_representation} ({char_name})")
    return unique_non_printable_chars_with_desc

# Moved to etld_lib_config so options to display can be recognized.
# def remove_null_soh_cr_and_display_utf8(field_column_type, field_name_tmp, field_data):
#     ## New Code as of Nov 26th.
#     if field_column_type != 'INTEGER':
#         #field_data = etld_lib_functions.remove_non_printable_except_tab_and_newline(str(field_data))
#         field_data = remove_values_from_string(str(field_data), ['\x00', '\x01', '\r'])
#         unicode_character_list = find_unique_unicode_characters_with_description(str(field_data))
#         if len(unicode_character_list) > 0:
#             logger.info(f"Unicode characters in fieldname: {field_name_tmp} - {unicode_character_list}")
#     return field_data

def find_non_printable_utf8_hex(input_string):
    non_printable_utf8_hex = []

    for char in input_string:
        if char not in string.printable:
            for byte in char.encode('utf-8'):
                non_printable_utf8_hex.append(f"\\x{byte:02x}")
    return non_printable_utf8_hex


def remove_non_printable_except_tab_and_newline(input_string):
        output = []
        for char in input_string:
            # ASCII control characters are in the range 0x00-0x1F (0-31) and 0x7F (127).
            # We exclude 0x09 (Tab) and 0x0A (Line Feed) from removal.
            if ord(char) in range(32) or ord(char) == 127:
                if char not in ('\t', '\n'):
                    continue
            output.append(char)
        return ''.join(output)


def main(log_level=logging.INFO, my_logger_prog_name=None):
    global logging_level
    global qetl_code_dir_etld_cred_yaml_template_path
    setup_logging_stdout(log_level, my_logger_prog_name)
    check_modules()
    check_python_version()
    get_sqlite_version()
    set_qetl_code_dir()
    set_qetl_code_dir_etld_cred_yaml_template_path()


if __name__ == '__main__':
    main()
