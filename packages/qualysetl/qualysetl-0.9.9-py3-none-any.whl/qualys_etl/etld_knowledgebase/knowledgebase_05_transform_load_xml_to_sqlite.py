#!/usr/bin/env python3
import xmltodict
import json
import re
from pathlib import Path
import time

from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_sqlite_tables
from qualys_etl.etld_lib import etld_lib_datetime
from qualys_etl.etld_lib import etld_lib_extract_transform_load
import codecs


def create_counter_objects(database_type='sqlite', table_name=""):
    counter_obj_kb = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=25000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added/updated into {database_type} "
                                    f"table {table_name}")

    counter_obj_kb_duplicates = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=25000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"duplicate rows not added to {database_type} "
                                    f"table {table_name}")

    counter_obj_dict_new = {'counter_obj_kb': counter_obj_kb,
                            'counter_obj_kb_duplicates': counter_obj_kb_duplicates}

    return counter_obj_dict_new


def drop_and_create_temp_merge_tables(sqlite_obj):
    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.kb_table_name_merge_new_data,
        csv_columns=etld_lib_config.kb_csv_columns(),
        csv_column_types=etld_lib_config.kb_csv_column_types(),
        key=['QID'])

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.kb_status_table_name,
        csv_columns=etld_lib_config.status_table_csv_columns(),
        csv_column_types=etld_lib_config.status_table_csv_column_types(),
        key=['STATUS_NAME'])


def drop_and_create_status_table(sqlite_obj):
    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.kb_status_table_name,
        csv_columns=etld_lib_config.status_table_csv_columns(),
        csv_column_types=etld_lib_config.status_table_csv_column_types(),
        key=['STATUS_NAME'])


def drop_and_create_all_tables(sqlite_obj):
    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.kb_table_name,
        csv_columns=etld_lib_config.kb_csv_columns(),
        csv_column_types=etld_lib_config.kb_csv_column_types(),
        key=['QID'])

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.kb_status_table_name,
        csv_columns=etld_lib_config.status_table_csv_columns(),
        csv_column_types=etld_lib_config.status_table_csv_column_types(),
        key=['STATUS_NAME'])


def drop_and_create_all_views(sqlite_obj):
    drop_view = f"DROP VIEW IF EXISTS {etld_lib_config.kb_table_name_cve_list_view}"
    sqlite_obj.execute_statement(drop_view)
    create_view_select_statement = '''select SUBSTR(CVE_LIST_ITEM_PREFIX, 0, CVE_LIST_ITEM_PREFIX_LENGTH) AS CVE, * from (
select Q_KnowledgeBase.*, INSTR(json_each.value,'CVE') as BEGIN_CVE_LIST_ITEM, json_each.value as CVE_LIST_ITEM_JSON, 
SUBSTR(json_each.value, INSTR(json_each.value,'CVE')) AS CVE_LIST_ITEM_PREFIX,
INSTR(SUBSTR(json_each.value, INSTR(json_each.value,'CVE')),'","') as CVE_LIST_ITEM_PREFIX_LENGTH 
from Q_KnowledgeBase, json_each( Q_KnowledgeBase.CVE_LIST, '$.CVE' )
where CVE_LIST like '%{%'
) 
ORDER BY CVE DESC'''

    create_view = \
        f"CREATE VIEW {etld_lib_config.kb_table_name_cve_list_view} as " \
        f"{create_view_select_statement}"
    sqlite_obj.execute_statement(create_view)


def insert_one_row_into_table(
        item_dict: dict,
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        table_name: str,
        counter_obj: dict,
        batch_date: str,
        batch_number: str

):

    # def prepare_field(field_data: dict, field_name_tmp):
    #     if field_data is None:
    #         field_data = ""
    #     elif 'DATE' in field_name_tmp:
    #         field_data = field_data.replace("T", " ").replace("Z", "")
    #         field_data = re.sub("\\..*$", "", field_data)
    #     elif isinstance(field_data, int):
    #         field_data = str(field_data)
    #     elif 'CVE_LIST' in field_name_tmp:
    #         if 'CVE' in field_data.keys():
    #             if isinstance(field_data['CVE'], dict):
    #                 one_item_dict = [field_data['CVE']]
    #                 field_data['CVE'] = one_item_dict
    #                 field_data = json.dumps(field_data)
    #             else:
    #                 field_data = json.dumps(field_data)
    #     elif not isinstance(field_data, str):
    #         field_data = json.dumps(field_data)
    #
    #     return field_data

    # row_in_sqlite_form = []
    #
    # for field_name in etld_lib_config.kb_csv_columns():  # Iterate through expected columns (contract)
    #     if field_name in item_dict.keys():  # Iterate through columns found in dictionary
    #         item_dict[field_name] = \
    #             sqlite_obj.prepare_knowledgebase_database_field(
    #                 item_dict[field_name],
    #                 field_name,
    #                 etld_lib_config.kb_csv_column_types())
    #         row_in_sqlite_form.append(item_dict[field_name])
    #     else:
    #         row_in_sqlite_form.append("")  # Ensure blank is added to each required empty field

    row_in_sqlite_form = \
        sqlite_obj.prepare_database_row_vmpc(
            item_dict,
            etld_lib_config.kb_csv_columns(),
            etld_lib_config.kb_csv_column_types(), batch_date=batch_date, batch_number=batch_number)

    result = sqlite_obj.insert_or_replace_row_pristine(table_name, row_in_sqlite_form)

    if result is True:
        counter_obj['counter_obj_kb'].update_counter_and_display_to_log()
    else:
        counter_obj['counter_obj_kb_duplicates'].update_counter_and_display_to_log()


def insert_xml_file_into_sqlite(xml_file: Path,
                                sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
                                table_name: str,
                                counter_obj: dict,
                                compression_method=open):

    def callback_to_insert_host_into_sqlite(element_names: tuple, document_item: dict):
        if len(element_names) > 2 and "VULN" != element_names[3][0]:
            return True
        # document_item['BATCH_DATE'] = batch_date
        # document_item['BATCH_NUMBER'] = int(batch_number)
        #document_item['Row_Last_Updated'] = etld_lib_datetime.get_utc_datetime_sqlite_database_format()
        insert_one_row_into_table(
            document_item, sqlite_obj, table_name, counter_obj=counter_obj,
            batch_date=batch_date, batch_number=batch_number)
        return True

    if etld_lib_config.xmltodict_parse_using_codec_to_replace_utf8_error is False:
        with compression_method(str(xml_file), "rt", encoding='utf-8') as xml_file_fd:
            batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(xml_file)
            batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(xml_file)
            xmltodict.parse(xml_file_fd.read(),
                            item_depth=4,
                            item_callback=callback_to_insert_host_into_sqlite)
    else:
        with compression_method(str(xml_file), "rb") as xml_file_fd:
            batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(xml_file)
            batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(xml_file)
            xmltodict.parse(codecs.decode(xml_file_fd.read(), encoding='utf-8', errors='replace'),
                            item_depth=4,
                            item_callback=callback_to_insert_host_into_sqlite)


def kb_transform_and_load_all_xml_files_into_sqlite():
    # TODO Drop Merge Table if exists, load new data into merge table,
    #  if not 1970, load data from old table where not exists into merge table,
    #  rename merge table to old table name.
    begin_knowledgebase_05_tranform_load()
    xml_file_to_import_into_sqlite = ""
    try:
        kb_sqlite_obj = etld_lib_sqlite_tables.SqliteObj(sqlite_file=etld_lib_config.kb_sqlite_file)
        xml_file_list = []
        rebuild_flag = False
        for file_name in sorted(Path(etld_lib_config.kb_extract_dir).glob(etld_lib_config.kb_extract_dir_file_search_blob)):
            if str(file_name).endswith('.xml') or str(file_name).endswith('.xml.gz'):
                xml_file_list.append(file_name)

        xml_file_to_import_into_sqlite = ""
        if len(xml_file_list) > 0:
            xml_file_to_import_into_sqlite = xml_file_list[-1]
            if xml_file_to_import_into_sqlite.name.__contains__("1970"):
                rebuild_flag = True
        else:
            etld_lib_functions.logger.error("No xml files to process, rerun extract when ready.")
            etld_lib_functions.logger.error(f"Directory: {etld_lib_config.kb_extract_dir}")
            exit(1)

        drop_and_create_status_table(sqlite_obj=kb_sqlite_obj)

        if rebuild_flag is True:
            # REBUILD KNOWLEDGEBASE
            counter_obj_dict = create_counter_objects(table_name=etld_lib_config.kb_table_name)
            drop_and_create_all_tables(sqlite_obj=kb_sqlite_obj)
            drop_and_create_all_views(sqlite_obj=kb_sqlite_obj)
            insert_xml_file_into_sqlite(
                xml_file=xml_file_to_import_into_sqlite,
                sqlite_obj=kb_sqlite_obj,
                table_name=etld_lib_config.kb_table_name,
                counter_obj=counter_obj_dict,
                compression_method=etld_lib_config.kb_open_file_compression_method)
        else:
            counter_obj_dict = create_counter_objects(table_name=etld_lib_config.kb_table_name)
            drop_and_create_all_views(sqlite_obj=kb_sqlite_obj)
            insert_xml_file_into_sqlite(
                xml_file=xml_file_to_import_into_sqlite,
                sqlite_obj=kb_sqlite_obj,
                table_name=etld_lib_config.kb_table_name,
                counter_obj=counter_obj_dict,
                compression_method=etld_lib_config.kb_open_file_compression_method)
        batch_name = etld_lib_extract_transform_load.get_batch_name_from_filename(
            file_name=xml_file_to_import_into_sqlite)
        batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(
            file_name=xml_file_to_import_into_sqlite)
        batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(
            file_name=xml_file_to_import_into_sqlite)
        etld_lib_functions.logger.info(f"Received batch file from multiprocessing Queue: {batch_name}")

        kb_sqlite_obj.update_status_table(
                batch_date=batch_date, batch_number=batch_number,
                total_rows_added_to_database=counter_obj_dict['counter_obj_kb'].get_counter(),
                status_table_name=etld_lib_config.kb_status_table_name,
                status_table_columns=etld_lib_config.status_table_csv_columns(),
                status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                status_name_column=etld_lib_config.kb_table_name, status_column='final')

        kb_sqlite_obj.update_status_table(
            batch_date=batch_date,
            batch_number=0,
            total_rows_added_to_database=0,
            status_table_name=etld_lib_config.kb_status_table_name,
            status_table_columns=etld_lib_config.status_table_csv_columns(),
            status_table_column_types=etld_lib_config.status_table_csv_column_types(),
            status_name_column='ALL_TABLES_LOADED_SUCCESSFULLY',
            status_column='final')

        kb_sqlite_obj.commit_changes()
        etld_lib_functions.log_file_info(xml_file_to_import_into_sqlite, "File loaded into database")
        kb_sqlite_obj.vacuum_database()
        kb_sqlite_obj.commit_changes()
        etld_lib_functions.log_file_info(etld_lib_config.kb_sqlite_file, "Database Vacuum Completed")
        kb_sqlite_obj.validate_all_tables_loaded_successfully()
        kb_sqlite_obj.close_connection()
        counter_obj_dict['counter_obj_kb'].display_final_counter_to_log()
        end_knowledgebase_05_transform_load()

    except Exception as e:
        etld_lib_functions.logger.warning(f"Exception: {e}")
        etld_lib_functions.logger.warning(f"Issue with xml file: {xml_file_to_import_into_sqlite}")
        raise Exception("Raise exception warning processing knowledgebase for retry attempt.")


def end_knowledgebase_05_transform_load():
    etld_lib_functions.logger.info(f"end")


def begin_knowledgebase_05_tranform_load():
    etld_lib_functions.logger.info("start")


def main():
    max_retry_count = 5
    retry_count = 0
    sleep_seconds = 300
    while retry_count < max_retry_count:
        try:
            kb_transform_and_load_all_xml_files_into_sqlite()
            break  # Success
        except Exception as e:
            retry_count += 1
            etld_lib_functions.logger.warning(f"Retry kb_transform_and_load_all_xml_files_into_sqlite")
            etld_lib_functions.logger.warning(f"Retry number: {retry_count} of max_retry_count: {max_retry_count}")
            etld_lib_functions.logger.warning(f"Sleeping {sleep_seconds} before retry...")
            time.sleep(sleep_seconds)
    else:
        raise Exception("Retries for processing knowledgebase failed.")


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='knowledgebase_05_transform_load_xml_to_sqlite')
    etld_lib_config.main()
    main()
