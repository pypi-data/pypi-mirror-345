#!/usr/bin/env python3
import xmltodict
import json
import re
import time
import sqlite3
from multiprocessing import Process, Queue
from pathlib import Path
import gzip

from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions
# from qualys_etl.etld_lib import etld_lib_credentials
from qualys_etl.etld_lib import etld_lib_authentication_objects
from qualys_etl.etld_lib import etld_lib_sqlite_tables
from qualys_etl.etld_lib import etld_lib_extract_transform_load
from qualys_etl.etld_lib import etld_lib_datetime
from qualys_etl.etld_lib import etld_lib_csv_distribution
from qualys_etl.etld_host_list_detection import host_list_detection_02_workflow_manager
from qualys_etl.etld_knowledgebase import knowledgebase_03_extract_controller
import codecs


def create_counter_objects(database_type='sqlite'):
    counter_obj_host_list_detection_hosts = etld_lib_functions.DisplayCounterToLog(
        display_counter_at=10000,
        logger_func=etld_lib_functions.logger.info,
        display_counter_log_message=f"rows added to {database_type} "
                                    f"table {etld_lib_config.host_list_detection_hosts_table_name}")

    counter_obj_host_list_detection_qids = \
        etld_lib_functions.DisplayCounterToLog(
            display_counter_at=100000,
            logger_func=etld_lib_functions.logger.info,
            display_counter_log_message=f"rows added to {database_type} "
                                        f"table {etld_lib_config.host_list_detection_qids_table_name}")

    counter_obj_host_list_detection_hosts_without_qids = \
        etld_lib_functions.DisplayCounterToLog(
            display_counter_at=10000,
            logger_func=etld_lib_functions.logger.info,
            display_counter_log_message=f"hosts without detection rows added to {database_type} "
                                        f"table {etld_lib_config.host_list_detection_qids_table_name}")

    counter_obj_dict_new = {
        'counter_obj_host_list_detection_hosts': counter_obj_host_list_detection_hosts,
        'counter_obj_host_list_detection_qids': counter_obj_host_list_detection_qids,
        'counter_obj_host_list_detection_hosts_without_qids': counter_obj_host_list_detection_hosts_without_qids,
    }

    return counter_obj_dict_new


def drop_and_create_all_tables(sqlite_obj):
    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.host_list_table_name,
        csv_columns=etld_lib_config.host_list_csv_columns(),
        csv_column_types=etld_lib_config.host_list_csv_column_types(),
        key='ID')

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.host_list_detection_q_knowledgebase_in_host_list_detection,
        csv_columns=etld_lib_config.kb_csv_columns(),
        csv_column_types=etld_lib_config.kb_csv_column_types(),
        key='QID')

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.host_list_detection_hosts_table_name,
        csv_columns=etld_lib_config.host_list_detection_host_csv_columns(),
        csv_column_types=etld_lib_config.host_list_detection_host_csv_column_types(),
        key='ID')

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.host_list_detection_qids_table_name,
        csv_columns=etld_lib_config.host_list_detection_qids_csv_columns(),
        csv_column_types=etld_lib_config.host_list_detection_qids_csv_column_types(),
    )

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.host_list_detection_status_table_name,
        csv_columns=etld_lib_config.status_table_csv_columns(),
        csv_column_types=etld_lib_config.status_table_csv_column_types(),
        key='STATUS_NAME')

    sqlite_obj.execute_statement(f"DROP VIEW IF EXISTS {etld_lib_config.host_list_detection_table_view_name}")
    # create_view_statement = \
    #     '''CREATE VIEW Q_Host_List_Detection as
    # select A.ID HL_ID, A.ASSET_ID HL_ASSET_ID, A.IP HL_IP, A.IPV6 HL_IPV6, A.TRACKING_METHOD HL_TRACKING_METHOD,
    # A.NETWORK_ID HL_NETWORK_ID, A.DNS HL_DNS, A.DNS_DATA HL_DNS_DATA, A.CLOUD_PROVIDER HL_CLOUD_PROVIDER,
    # A.CLOUD_SERVICE HL_CLOUD_SERVICE, A.CLOUD_RESOURCE_ID HL_CLOUD_RESOURCE_ID,
    # A.EC2_INSTANCE_ID HL_EC2_INSTANCE_ID, A.NETBIOS HL_NETBIOS, A.OS HL_OS, A.QG_HOSTID HL_QG_HOSTID,
    # A.TAGS HL_TAGS, A.METADATA HL_METADATA, A.CLOUD_PROVIDER_TAGS HL_CLOUD_PROVIDER_TAGS,
    # A.LAST_VULN_SCAN_DATETIME HL_LAST_VULN_SCAN_DATETIME, A.LAST_VM_SCANNED_DATE HL_LAST_VM_SCANNED_DATE,
    # A.LAST_VM_SCANNED_DURATION HL_LAST_VM_SCANNED_DURATION,
    # A.LAST_VM_AUTH_SCANNED_DATE HL_LAST_VM_AUTH_SCANNED_DATE,
    # A.LAST_VM_AUTH_SCANNED_DURATION HL_LAST_VM_AUTH_SCANNED_DURATION,
    # A.LAST_COMPLIANCE_SCAN_DATETIME HL_LAST_COMPLIANCE_SCAN_DATETIME, A.OWNER HL_OWNER,
    # A.COMMENTS HL_COMMENTS, A.USER_DEF HL_USER_DEF, A.ASSET_GROUP_IDS HL_ASSET_GROUP_IDS,
    # A.ASSET_RISK_SCORE HL_ASSET_RISK_SCORE, A.ASSET_CRITICALITY_SCORE HL_ASSET_CRITICALITY_SCORE,
    # A.ARS_FACTORS HL_ARS_FACTORS,
    # A.BATCH_DATE HL_BATCH_DATE, A.BATCH_NUMBER HL_BATCH_NUMBER, A.Row_Last_Updated HL_Row_Last_Updated,
    # B.ID HLDH_ID, B.ASSET_ID HLDH_ASSET_ID, B.IP HLDH_IP, B.IPV6 HLDH_IPV6, B.TRACKING_METHOD HLDH_TRACKING_METHOD,
    # B.NETWORK_ID HLDH_NETWORK_ID, B.OS HLDH_OS, B.OS_CPE HLDH_OS_CPE, B.DNS HLDH_DNS, B.DNS_DATA HLDH_DNS_DATA,
    # B.NETBIOS HLDH_NETBIOS, B.QG_HOSTID HLDH_QG_HOSTID, B.LAST_SCAN_DATETIME HLDH_LAST_SCAN_DATETIME,
    # B.LAST_VM_SCANNED_DATE HLDH_LAST_VM_SCANNED_DATE, B.LAST_VM_SCANNED_DURATION HLDH_LAST_VM_SCANNED_DURATION,
    # B.LAST_VM_AUTH_SCANNED_DATE HLDH_LAST_VM_AUTH_SCANNED_DATE,
    # B.LAST_VM_AUTH_SCANNED_DURATION HLDH_LAST_VM_AUTH_SCANNED_DURATION,
    # B.LAST_PC_SCANNED_DATE HLDH_LAST_PC_SCANNED_DATE, B.BATCH_DATE HLDH_BATCH_DATE,
    # B.BATCH_NUMBER HLDH_BATCH_NUMBER, B.Row_Last_Updated HLDH_Row_Last_Updated,
    # C.ID HLDQ_ID, C.ASSET_ID HLDQ_ASSET_ID, C.QID HLDQ_QID, C.TYPE HLDQ_TYPE, C.STATUS HLDQ_STATUS,
    # C.PORT HLDQ_PORT, C.PROTOCOL HLDQ_PROTOCOL, C.SEVERITY HLDQ_SEVERITY, C.FQDN HLDQ_FQDN, C.SSL HLDQ_SSL,
    # C.INSTANCE HLDQ_INSTANCE, C.LAST_PROCESSED_DATETIME HLDQ_LAST_PROCESSED_DATETIME,
    # C.FIRST_FOUND_DATETIME HLDQ_FIRST_FOUND_DATETIME, C.LAST_FOUND_DATETIME HLDQ_LAST_FOUND_DATETIME,
    # C.TIMES_FOUND HLDQ_TIMES_FOUND, C.LAST_TEST_DATETIME HLDQ_LAST_TEST_DATETIME,
    # C.LAST_UPDATE_DATETIME HLDQ_LAST_UPDATE_DATETIME, C.LAST_FIXED_DATETIME HLDQ_LAST_FIXED_DATETIME,
    # C.FIRST_REOPENED_DATETIME HLDQ_FIRST_REOPENED_DATETIME, C.LAST_REOPENED_DATETIME HLDQ_LAST_REOPENED_DATETIME,
    # C.TIMES_REOPENED HLDQ_TIMES_REOPENED, C.SERVICE HLDQ_SERVICE, C.IS_IGNORED HLDQ_IS_IGNORED,
    # C.IS_DISABLED HLDQ_IS_DISABLED, C.AFFECT_RUNNING_KERNEL HLDQ_AFFECT_RUNNING_KERNEL,
    # C.AFFECT_RUNNING_SERVICE HLDQ_AFFECT_RUNNING_SERVICE,
    # C.AFFECT_EXPLOITABLE_CONFIG HLDQ_AFFECT_EXPLOITABLE_CONFIG,
    # C.QDS HLDQ_QDS, C.QDS_FACTORS HLDQ_QDS_FACTORS,
    # C.RESULTS HLDQ_RESULTS,
    # C.BATCH_DATE HLDQ_BATCH_DATE,
    # C.BATCH_NUMBER HLDQ_BATCH_NUMBER,
    # C.Row_Last_Updated HLDQ_Row_Last_Updated
    # from Q_Host_List A
    # left outer join Q_Host_List_Detection_HOSTS B ON A.ID = B.ID
    # left outer join Q_Host_List_Detection_QIDS C ON A.ID = C.ID'''
    #
    # sqlite_obj.execute_statement(create_view_statement)
    # create_view_statement_display = create_view_statement.replace('\n', '').replace('  ', ' ')
    # etld_lib_functions.logger.info(f"VIEW CREATED: {create_view_statement_display}")
    sqlite_obj.commit_changes()


def attach_database_to_host_list_detection(
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj, table_name, database_as_name, database_file):
    sqlite_obj.attach_database_to_connection(database_as_name=database_as_name,
                                             database_sqlite_file=database_file)
    table_name = f"{database_as_name}.{table_name}"
    table_columns = sqlite_obj.get_table_columns(table_name=table_name)
    etld_lib_functions.logger.info(f"Found Table {table_name} columns: {table_columns}")
    return table_name, table_columns


def detach_database_to_host_list_detection(
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj, table_name, database_as_name, database_file):
    sqlite_obj.detach_database_to_connection(database_as_name=database_as_name,
                                             database_sqlite_file=database_file)


def get_batch_date_from_status_table(
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj, status_table_name, table_name):
    batch_date = None
    try:
        etld_lib_functions.logger.info(f"Begin retrieving batch_date for {table_name}")
        rows = sqlite_obj.select_all_from_status_table_where_status_name_equals_table_name(
            status_table_name=status_table_name,
            table_name=table_name
        )
        for row in rows:
            status_detail_dict = json.loads(row['STATUS_DETAIL'])
            batch_date = status_detail_dict['BATCH_DATE']
            break  # Any row will do.
        etld_lib_functions.logger.info(f"End   retrieving batch_date for {table_name}")
    except Exception as e:
        etld_lib_functions.logger.error(f"Error retrieving batch_date for {table_name}")
        etld_lib_functions.logger.error(f"Exception is: {e}")
        exit(1)
    return batch_date


# def copy_database_table(
#         sqlite_obj: etld_lib_sqlite_tables.SqliteObj, table_name, new_table_name, where_clause=""):
#     try:
#         etld_lib_functions.logger.info(f"Begin creating {new_table_name} from {table_name}")
#         #        etl_workflow_sqlite_obj.cursor.execute(f"DROP TABLE IF EXISTS {new_table_name}")
#         #        etl_workflow_sqlite_obj.cursor.execute(f"CREATE TABLE {new_table_name} AS SELECT * FROM {table_name} where 1=0")
#         # TODO CHECK ME
#         sqlite_obj.cursor.execute(f"INSERT INTO {new_table_name} SELECT * FROM {table_name} {where_clause}")
#         etld_lib_functions.logger.info(f"End   creating {new_table_name} from {table_name}")
#     except Exception as e:
#         etld_lib_functions.logger.error(f"Error creating table {new_table_name} from {table_name}")
#         etld_lib_functions.logger.error(f"Exception is: {e}")
#         exit(1)


def copy_database_table(
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj, table_name, new_table_name, where_clause="", select_clause="*"):
    max_attempts = 15  # Maximum number of attempts
    attempt = 0
    sleep_time = 15
    success_flag = False

    while attempt < max_attempts:
        try:
            etld_lib_functions.logger.info(f"Attempt {attempt + 1}: Begin creating {new_table_name} from {table_name}")

            etld_lib_functions.logger.info(
                f"INSERT INTO {new_table_name} SELECT {select_clause} FROM {table_name} {where_clause}")
            sqlite_obj.cursor.execute(
                f"INSERT INTO {new_table_name} SELECT {select_clause} FROM {table_name} {where_clause}")
            time.sleep(sleep_time)
            etld_lib_functions.logger.info(f"Attempt {attempt + 1}: End creating {new_table_name} from {table_name}")
            success_flag = True
            break  # Success, exit the loop
        except sqlite3.OperationalError as oe:
            time.sleep(sleep_time)
            etld_lib_functions.logger.warning(f"Operational error on attempt {attempt + 1}: {oe}")
        except sqlite3.IntegrityError as ie:
            time.sleep(sleep_time)
            etld_lib_functions.logger.warning(f"Integrity error on attempt {attempt + 1}: {ie}")
            break
        except sqlite3.DatabaseError as de:
            time.sleep(sleep_time)
            etld_lib_functions.logger.warning(f"Database error on attempt {attempt + 1}: {de}")
        except sqlite3.Error as se:
            time.sleep(sleep_time)
            etld_lib_functions.logger.warning(f"sqlite3.Error on attempt {attempt + 1}: {se}")
        except IOError as ioe:
            time.sleep(sleep_time)
            etld_lib_functions.logger.warning(f"IO error on attempt {attempt + 1}: {ioe}")
        except Exception as e:
            time.sleep(sleep_time)
            etld_lib_functions.logger.warning(f"Unexpected error on attempt {attempt + 1}: {e}")

        attempt += 1
        if attempt < max_attempts:
            time.sleep(sleep_time)
            etld_lib_functions.logger.info(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)  # Wait for 30 seconds before retrying

    if attempt == max_attempts:
        time.sleep(5)
        etld_lib_functions.logger.error(
            f"Failed to create table {new_table_name} from {table_name} after {max_attempts} attempts.")
        exit(1)

    if not success_flag:
        time.sleep(5)  # Wait for 30 seconds before retrying
        etld_lib_functions.logger.error(
            f"Success Flag is false; Failed to create table {new_table_name} from {table_name}")
        exit(1)


# def create_kb_and_host_list_tables_in_host_list_detection_database(etl_workflow_sqlite_obj: etld_lib_sqlite_tables.SqliteObj):
#     etld_lib_functions.logger.info(f"Attaching database: {etld_lib_config.host_list_sqlite_file}")
#     host_list_table_name, host_list_table_columns = \
#         attach_database_to_host_list_detection(etl_workflow_sqlite_obj=etl_workflow_sqlite_obj,
#                                                table_name="Q_Host_List",
#                                                database_as_name="H1",
#                                                database_file=etld_lib_config.host_list_sqlite_file)
#
#     # Update knowledgebase after extracting detections in case of edge case qid created during run.
#     host_list_detection_02_workflow_manager.get_knowledgebase_controller(
#        kb_last_modified_after=etld_lib_datetime.get_utc_date_minus_days(days=7))
#
#     etld_lib_functions.logger.info(f"Attaching database: {etld_lib_config.kb_table_name}")
#     kb_table_name, kb_table_columns = \
#         attach_database_to_host_list_detection(etl_workflow_sqlite_obj=etl_workflow_sqlite_obj,
#                                                table_name="Q_KnowledgeBase",
#                                                database_as_name="K1",
#                                                database_file=etld_lib_config.kb_sqlite_file)
#
#     etld_lib_functions.logger.info(f"Copying table: {host_list_table_name}")
#     copy_database_table(etl_workflow_sqlite_obj=etl_workflow_sqlite_obj, table_name=host_list_table_name, new_table_name="Q_Host_List")
#
#     etld_lib_functions.logger.info(f"Copying table: {kb_table_name}")
#     where_clause = f"where {kb_table_name}.QID in (select distinct(QID) from Q_Host_List_Detection_QIDS)"
#     copy_database_table(etl_workflow_sqlite_obj=etl_workflow_sqlite_obj, table_name=kb_table_name,
#                         new_table_name="Q_KnowledgeBase_In_Host_List_Detection", where_clause=where_clause)
#     etld_lib_functions.logger.info(f"Commit copy of table: {host_list_table_name}, {kb_table_name}")
#     etl_workflow_sqlite_obj.commit_changes()


def update_host_list_in_host_list_detection_database(sqlite_obj: etld_lib_sqlite_tables.SqliteObj):
    etld_lib_functions.logger.info(f"Attaching database: {etld_lib_config.host_list_sqlite_file}")
    host_list_table_name, host_list_table_columns = \
        attach_database_to_host_list_detection(sqlite_obj=sqlite_obj,
                                               table_name="Q_Host_List",
                                               database_as_name="H1",
                                               database_file=etld_lib_config.host_list_sqlite_file)

    etld_lib_functions.logger.info(f"Copying table: {host_list_table_name}")
    copy_database_table(sqlite_obj=sqlite_obj, table_name=host_list_table_name, new_table_name="Q_Host_List",
                        select_clause="*")
    etld_lib_functions.logger.info(f"Commit copy of table: {host_list_table_name}")
    sqlite_obj.commit_changes()

    etld_lib_functions.logger.info(f"Detaching database: {etld_lib_config.host_list_sqlite_file}")
    detach_database_to_host_list_detection(sqlite_obj=sqlite_obj,
                                           table_name="Q_Host_List",
                                           database_as_name="H1",
                                           database_file=etld_lib_config.host_list_sqlite_file)
    sqlite_obj.commit_changes()


def refresh_knowledgebase():
    kb_last_modified_after = etld_lib_datetime.get_utc_date_minus_days(days=30)
    knowledgebase_03_extract_controller.knowledgebase_extract_controller(
        kb_last_modified_after=kb_last_modified_after,
        lock_file_required=True
    )


def update_knowledgebase_in_host_list_detection_database(refresh_knowledgebase_flag=True):
    if refresh_knowledgebase_flag:
        refresh_knowledgebase()

    sqlite_obj = etld_lib_sqlite_tables.SqliteObj(
        sqlite_file=etld_lib_config.host_list_detection_sqlite_file)

    sqlite_obj.drop_and_recreate_table(
        table_name=etld_lib_config.host_list_detection_q_knowledgebase_in_host_list_detection,
        csv_columns=etld_lib_config.kb_csv_columns(),
        csv_column_types=etld_lib_config.kb_csv_column_types(),
        key='QID')

    etld_lib_functions.logger.info(f"Attaching database: {etld_lib_config.kb_table_name}")
    kb_table_name, kb_table_columns = \
        attach_database_to_host_list_detection(sqlite_obj=sqlite_obj,
                                               table_name="Q_KnowledgeBase",
                                               database_as_name="K1",
                                               database_file=etld_lib_config.kb_sqlite_file)

    # etld_lib_functions.logger.info(f"Copying table: {kb_table_name}")
    # where_clause = f"where {kb_table_name}.QID in (select distinct(QID) from Q_Host_List_Detection_QIDS)"
    # copy_database_table(sqlite_obj=sqlite_obj, table_name=kb_table_name,
    #                     new_table_name="Q_KnowledgeBase_In_Host_List_Detection", where_clause=where_clause)
    #
    # etld_lib_functions.logger.info(f"Commit copy of table:  {kb_table_name}")
    # sqlite_obj.commit_changes()
    sqlite_obj.create_q_knowledgebase_in_host_list_detection()

    etld_lib_functions.logger.info(f"Detaching database: {etld_lib_config.kb_table_name}")
    detach_database_to_host_list_detection(sqlite_obj=sqlite_obj,
                                           table_name="Q_KnowledgeBase",
                                           database_as_name="K1",
                                           database_file=etld_lib_config.kb_sqlite_file)
    sqlite_obj.commit_changes()
    sqlite_obj.close_connection()


def update_final_status_in_host_list_detection_database():
    sqlite_obj = etld_lib_sqlite_tables.SqliteObj(
        sqlite_file=etld_lib_config.host_list_detection_sqlite_file)
    batch_date = get_batch_date_from_status_table(
        sqlite_obj=sqlite_obj,
        status_table_name=etld_lib_config.host_list_detection_status_table_name,
        table_name=etld_lib_config.host_list_detection_hosts_table_name
    )
    sqlite_obj.update_status_table(
        batch_date=batch_date,
        batch_number="0",
        total_rows_added_to_database=0,
        status_table_name=etld_lib_config.host_list_detection_status_table_name,
        status_table_columns=etld_lib_config.status_table_csv_columns(),
        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
        status_name_column='ALL_TABLES_LOADED_SUCCESSFULLY',
        status_column='final')
    sqlite_obj.commit_changes()
    sqlite_obj.close_connection()


def insert_into_sqlite_host_list_detection_host_and_associated_qids(
        host_list_detection_document: dict,
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        counter_obj: dict,
        csv_distribution_dict: dict,
        batch_number: str = '000001',
        batch_date: str = '1970-01-01 00:00:00'
):
    # def prepare_database_field(field_data, field_name_tmp) -> dict:
    #     if field_data is None:
    #         field_data = ""
    #     elif 'DATE' in field_name_tmp:
    #         field_data = field_data.replace("T", " ").replace("Z", "")
    #         field_data = re.sub("\\..*$", "", field_data)
    #     elif isinstance(field_data, int):
    #         field_data = str(field_data)
    #     elif not isinstance(field_data, str):
    #         field_data = json.dumps(field_data)
    #
    #     return field_data

    # def prepare_database_row(item: dict, database_columns: list) -> list:
    #     row_in_sqlite_form = []
    #     for field_name in database_columns:
    #         if field_name in item.keys():
    #             item[field_name] = \
    #                 prepare_database_field(item[field_name], field_name)
    #             row_in_sqlite_form.append(item[field_name])
    #         else:
    #             row_in_sqlite_form.append("")  # Ensure blank is added to each required empty field
    #     return row_in_sqlite_form

    def insert_host_rows_into_database_and_csv(host_document):
        # host_row_in_sqlite_form: list = \
        #     prepare_database_row(
        #         item=host_document,
        #         database_columns=etld_lib_config.host_list_detection_host_csv_columns())

        # host_row_in_sqlite_form: list = \
        #     sqlite_obj.prepare_database_row(
        #         item=host_document,
        #         database_columns=etld_lib_config.host_list_detection_host_csv_columns(),
        #         database_column_types=etld_lib_config.host_list_detection_host_csv_column_types()
        #     )

        host_row_in_sqlite_form: list = \
            sqlite_obj.prepare_database_row_vmpc(
                item_dict=host_document,
                csv_columns=etld_lib_config.host_list_detection_host_csv_columns(),
                csv_column_types=etld_lib_config.host_list_detection_host_csv_column_types(),
                batch_date=batch_date,
                batch_number=batch_number
            )

        result = sqlite_obj.insert_or_replace_row_pristine(
            table_name=etld_lib_config.host_list_detection_hosts_table_name,
            row=host_row_in_sqlite_form)

        if result is True:
            counter_obj['counter_obj_host_list_detection_hosts'].update_counter_and_display_to_log()
            if etld_lib_config.host_list_detection_distribution_csv_flag:
                # CSV - WRITE ROW
                # Write one row to Q_Host_List_Detection_HOSTS CSV File.
                #
                csv_obj: etld_lib_csv_distribution.CsvDistribution = \
                    csv_distribution_dict['q_host_list_detection_hosts_csv_obj']
                csv_obj.write_csv_row_to_file_handle(row=host_row_in_sqlite_form)

        else:
            etld_lib_functions.logger.error("Error inserting detection")
            row = re.sub('\n', '', '|'.join(host_row_in_sqlite_form))
            json_str = json.dumps(host_document)
            json_str = re.sub('\n', '', json_str)
            etld_lib_functions.logger.error(f"ROW: {row}")
            etld_lib_functions.logger.error(f"JSON: {json_str}")
            exit(1)

    def insert_qids_rows_into_database_and_csv(detection_list: list):
        if isinstance(detection_list, dict):
            detection_list = [detection_list]

        for one_detection_dict in detection_list:
            if isinstance(one_detection_dict, dict):
                one_detection_dict['ID'] = host_list_detection_document['ID']
                if 'ASSET_ID' in host_list_detection_document.keys():
                    one_detection_dict['ASSET_ID'] = host_list_detection_document['ASSET_ID']
                # one_detection_dict['BATCH_DATE'] = batch_date
                # one_detection_dict['BATCH_NUMBER'] = batch_number

                qids_row_in_sqlite_form = \
                    sqlite_obj.prepare_database_row_vmpc(
                        item_dict=one_detection_dict,
                        csv_columns=etld_lib_config.host_list_detection_qids_csv_columns(),
                        csv_column_types=etld_lib_config.host_list_detection_qids_csv_column_types(),
                        batch_date=batch_date,
                        batch_number=batch_number
                    )

                result = sqlite_obj.insert_or_replace_row_pristine(
                    table_name=etld_lib_config.host_list_detection_qids_table_name,
                    row=qids_row_in_sqlite_form)

                if result is True:
                    counter_obj['counter_obj_host_list_detection_qids'].update_counter_and_display_to_log()
                    if etld_lib_config.host_list_detection_distribution_csv_flag:
                        #
                        # Write one row to Q_Host_List_Detection_QIDS CSV File.
                        #
                        csv_obj: etld_lib_csv_distribution.CsvDistribution = \
                            csv_distribution_dict['q_host_list_detection_qids_csv_obj']
                        csv_obj.write_csv_row_to_file_handle(qids_row_in_sqlite_form)
                else:
                    etld_lib_functions.logger.error("Error inserting detection")
                    row = re.sub('\n', '', '|'.join(qids_row_in_sqlite_form))
                    json_str = json.dumps(one_detection_dict)
                    json_str = re.sub('\n', '', json_str)
                    etld_lib_functions.logger.error(f"ROW: {row}")
                    etld_lib_functions.logger.error(f"JSON: {json_str}")
                    exit(1)

    def qids_found():
        qids_found_flag = False
        if 'DETECTION_LIST' in host_list_detection_document:
            if 'DETECTION' in host_list_detection_document['DETECTION_LIST']:
                qids_found_flag = True
            else:
                json_message = \
                    {'ID': host_list_detection_document['ID'], 'BATCH_NUMBER': batch_number, 'BATCH_DATE': batch_date}
                etld_lib_functions.logger.warning(f"No DETECTION for: {json_message}")
        else:
            json_message = \
                {'ID': host_list_detection_document['ID'], 'BATCH_NUMBER': batch_number, 'BATCH_DATE': batch_date}
            etld_lib_functions.logger.warning(f"No DETECTION_LIST for: {json_message}")
        return qids_found_flag

    #
    # Insert Host and QIDS into targets database and csv
    #
    # host_list_detection_document['BATCH_DATE'] = batch_date
    # host_list_detection_document['BATCH_NUMBER'] = batch_number
    insert_host_rows_into_database_and_csv(host_list_detection_document)
    if qids_found():
        insert_qids_rows_into_database_and_csv(host_list_detection_document['DETECTION_LIST']['DETECTION'])


# def q_hosts_csv_info_setup(batch_date, batch_number) -> dict:
#     q_host_list_detection_hosts_target_csv_file_name, \
#     table_name_utc_run_datetime,  \
#     table_name_batch_number,  \
#     q_host_list_detection_hosts_target_tmp_csv_file_name = \
#         etld_lib_csv_distribution.get_target_csv_file_name(
#             batch_date, batch_number,
#             etld_lib_config.host_list_detection_hosts_table_name,
#             csv_file_open_method=etld_lib_config.host_list_detection_open_file_compression_method
#         )
#     # FINAL CSV FILENAME Target
#     q_host_list_detection_hosts_target_csv_file_path = \
#         Path(etld_lib_config.host_list_detection_distribution_dir,
#              q_host_list_detection_hosts_target_csv_file_name)
#     # TEMP CSV FILENAME WHILE BUILDING FILE
#     q_host_list_detection_hosts_target_tmp_csv_file_path = \
#         Path(etld_lib_config.host_list_detection_distribution_dir,
#              q_host_list_detection_hosts_target_tmp_csv_file_name
#              )
#
#     q_hosts_csv_info = {}
#     q_hosts_csv_info['target_csv_file_name'] = q_host_list_detection_hosts_target_csv_file_name
#     q_hosts_csv_info['table_name_utc_run_datetime'] = table_name_utc_run_datetime
#     q_hosts_csv_info['table_name_batch_number'] = table_name_batch_number
#     q_hosts_csv_info['target_tmp_csv_file_name'] = q_host_list_detection_hosts_target_tmp_csv_file_name
#     q_hosts_csv_info['target_csv_file_path'] = q_host_list_detection_hosts_target_csv_file_path
#     q_hosts_csv_info['target_tmp_csv_file_path'] = q_host_list_detection_hosts_target_tmp_csv_file_path
#     q_hosts_csv_info['distribution_dir'] = etld_lib_config.host_list_detection_distribution_dir
#     q_hosts_csv_info['compression_method'] = etld_lib_config.host_list_detection_open_file_compression_method
#     #
#     # Create Q_Host_List_Detection_HOSTS CSV OBJECT
#     #
#     q_hosts_csv_info['csv_obj'] = \
#         etld_lib_csv_distribution.CsvDistribution(
#             target_csv_path=q_hosts_csv_info['target_tmp_csv_file_path'],
#             target_csv_data_directory=Path(q_hosts_csv_info['distribution_dir']))
#
#     return q_hosts_csv_info


# def q_qids_csv_info_setup(batch_date, batch_number) -> dict:
#     q_host_list_detection_qids_target_csv_file_name, \
#     table_name_utc_run_datetime, \
#     table_name_batch_number, \
#     q_host_list_detection_qids_target_tmp_csv_file_name = \
#         etld_lib_csv_distribution.get_target_csv_file_name(
#             batch_date, batch_number,
#             etld_lib_config.host_list_detection_qids_table_name,
#             csv_file_open_method=etld_lib_config.host_list_detection_open_file_compression_method
#         )
#
#     # FINAL CSV FILENAME Target
#     q_host_list_detection_qids_target_csv_file_path = \
#         Path(etld_lib_config.host_list_detection_distribution_dir,
#              q_host_list_detection_qids_target_csv_file_name)
#     # TEMP CSV FILENAME WHILE BUILDING FILE
#     q_host_list_detection_qids_target_tmp_csv_file_path = \
#         Path(etld_lib_config.host_list_detection_distribution_dir,
#              q_host_list_detection_qids_target_tmp_csv_file_name)
#
#     q_qids_csv_info = {}
#     q_qids_csv_info['target_csv_file_name'] = q_host_list_detection_qids_target_csv_file_name
#     q_qids_csv_info['table_name_utc_run_datetime'] = table_name_utc_run_datetime
#     q_qids_csv_info['table_name_batch_number'] = table_name_batch_number
#     q_qids_csv_info['tmp_csv_file_name'] = q_host_list_detection_qids_target_tmp_csv_file_name
#     q_qids_csv_info['target_csv_file_path'] = q_host_list_detection_qids_target_csv_file_path
#     q_qids_csv_info['target_tmp_csv_file_path'] = q_host_list_detection_qids_target_tmp_csv_file_path
#     q_qids_csv_info['distribution_dir'] = etld_lib_config.host_list_detection_distribution_dir
#     q_qids_csv_info['compression_method'] = etld_lib_config.host_list_detection_open_file_compression_method
#
#     #
#     # Create Q_Host_List_Detection_QIDS CSV OBJECT
#     #
#
#     q_qids_csv_info['csv_obj'] = \
#         etld_lib_csv_distribution.CsvDistribution(
#             target_csv_path=q_qids_csv_info['target_tmp_csv_file_path'],
#             target_csv_data_directory=Path(q_qids_csv_info['distribution_dir']))
#
#     return q_qids_csv_info


def insert_xml_file_into_sqlite(xml_file, sqlite_obj: etld_lib_sqlite_tables.SqliteObj, counter_obj):
    def callback_to_insert_host_into_sqlite_and_csv(element_names: tuple, document_item: dict):
        if len(element_names) > 2 and "HOST" != element_names[3][0]:
            return True
        else:
            batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(xml_file)
            batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(xml_file)
            try:
                # CSV - CSV_OBJ
                insert_into_sqlite_host_list_detection_host_and_associated_qids(
                    host_list_detection_document=document_item,
                    sqlite_obj=sqlite_obj,
                    batch_date=batch_date,
                    batch_number=batch_number,
                    counter_obj=counter_obj,
                    csv_distribution_dict=csv_distribution_dict
                )

            except Exception as e:
                etld_lib_functions.logger.error(f"Exception: {e}")
                etld_lib_functions.logger.error(
                    f"Issue inserting xml file into sqlite: {document_item}, counter={counter_obj}")
                exit(1)
            return True

    # READ XML FILE
    # with etld_lib_config.host_list_detection_open_file_compression_method(
    #         str(xml_file), "rt", encoding='utf-8') as xml_file_fd:
    # Commented out on 4/10/2025 for testing codec logging.
    # if etld_lib_config.xmltodict_parse_using_codec_to_replace_utf8_error is True:
    #     xml_file_args = (str(xml_file), "rb")
    #     xml_file_kwargs = {}
    # else:
    #     xml_file_args = (str(xml_file), "rt")
    #     xml_file_kwargs = {"encoding": "utf-8"}

    # added 4/10/2025 for codec logging.  No need for flag xmltodict_parse_using_codec_to_replace_utf8_error

    if etld_lib_config.xmltodict_parse_using_codec_to_replace_utf8_error is True:
        xml_file_args = (str(xml_file), "rb")
        xml_file_kwargs = {}
    else:
        xml_file_args = (str(xml_file), "rb")
        xml_file_kwargs = {}
        #xml_file_args = (str(xml_file), "rt")
        #xml_file_kwargs = {"encoding": "utf-8"}

    # 2024-01-26 with etld_lib_config.host_list_detection_open_file_compression_method(str(xml_file), "rb") as xml_file_fd:

    with etld_lib_config.host_list_detection_open_file_compression_method(*xml_file_args,
                                                                          **xml_file_kwargs) as xml_file_fd:
        sqlite_obj.cursor.execute("BEGIN TRANSACTION;")  # 2025-04-07 performance tuning
        batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(xml_file)
        batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(xml_file)

        csv_distribution_dict = {}
        if etld_lib_config.host_list_detection_distribution_csv_flag:
            # CSV - INFO
            # Create csv_info with all file and object locations for csv creation
            #
            q_hosts_csv_info = etld_lib_csv_distribution.get_csv_info_dict(
                batch_date=batch_date,
                batch_number=batch_number,
                table_name=etld_lib_config.host_list_detection_hosts_table_name,
                csv_file_open_method=etld_lib_config.host_list_detection_open_file_compression_method,
                distribution_dir=etld_lib_config.host_list_detection_distribution_dir
            )
            q_qids_csv_info = etld_lib_csv_distribution.get_csv_info_dict(
                batch_date=batch_date,
                batch_number=batch_number,
                table_name=etld_lib_config.host_list_detection_qids_table_name,
                csv_file_open_method=etld_lib_config.host_list_detection_open_file_compression_method,
                distribution_dir=etld_lib_config.host_list_detection_distribution_dir
            )
            # CSV - OPEN FILES FOR WRITING
            # BEGIN WRITING DATABASE AND CSV FILES
            #

            with q_hosts_csv_info['compression_method'](q_hosts_csv_info['target_tmp_csv_file_path'], 'wt',
                                                        newline='') as \
                    q_hosts_target_tmp_csv_file_handle:
                with q_qids_csv_info['compression_method'](q_qids_csv_info['target_tmp_csv_file_path'], 'wt',
                                                           newline='') as \
                        q_qids_target_tmp_csv_file_handle:
                    # CSV - SET FILE HANDLE FOR WRITE ROW
                    # Set csv writer file handles in csv_obj for reuse in callback_to_insert_host_into_sqlite_and_csv
                    q_hosts_csv_info['csv_obj'].set_csv_writer_with_file_handle(q_hosts_target_tmp_csv_file_handle)
                    q_qids_csv_info['csv_obj'].set_csv_writer_with_file_handle(q_qids_target_tmp_csv_file_handle)

                    csv_distribution_dict['q_host_list_detection_hosts_csv_obj'] = q_hosts_csv_info['csv_obj']
                    csv_distribution_dict['q_host_list_detection_qids_csv_obj'] = q_qids_csv_info['csv_obj']

                    # Added 4/10/2025 for testing improvement to parsing errors.
                    if etld_lib_config.xmltodict_parse_using_codec_to_replace_utf8_error is True:
                        try:
                            xml_content = codecs.decode(xml_file_fd.read(), encoding='utf-8', errors='strict')
                            xmltodict.parse(xml_content, item_depth=4,
                                            item_callback=callback_to_insert_host_into_sqlite_and_csv)
                        except UnicodeDecodeError as e:
                            etld_lib_functions.logger.warning(
                                f"decoding issue, fixing decoding issue in {str(xml_file)}: {str(e)}")
                            xml_file_fd.seek(0)  # Reset file pointer
                            xml_content = codecs.decode(xml_file_fd.read(), encoding='utf-8', errors='replace')
                            xmltodict.parse(xml_content, item_depth=4,
                                            item_callback=callback_to_insert_host_into_sqlite_and_csv)
                    else:
                        try:
                            xmltodict.parse(xml_file_fd, item_depth=4,
                                            item_callback=callback_to_insert_host_into_sqlite_and_csv)
                        except Exception as e:
                            etld_lib_functions.logger.error(f"decoding error, error in {str(xml_file)}: {str(e)}")
                            etld_lib_functions.logger.error(
                                f"Rerun after setting xmltodict_parse_using_codec_to_replace_utf8_error: True")
                            exit(1)

                    # COMMENTED OUT 4/10/2025 for testing.
                    # if etld_lib_config.xmltodict_parse_using_codec_to_replace_utf8_error is False:
                    #     xmltodict.parse(xml_file_fd.read(),
                    #                     item_depth=4,
                    #                     item_callback=callback_to_insert_host_into_sqlite_and_csv
                    #                     )
                    # else:
                    #     xmltodict.parse(codecs.decode(xml_file_fd.read(), encoding='utf-8', errors='replace'),
                    #                     item_depth=4,
                    #                     item_callback=callback_to_insert_host_into_sqlite_and_csv
                    #                     )

            # Rename temp csv files to final naming .csv.gz.tmp to .csv.gz
            Path(q_hosts_csv_info['target_tmp_csv_file_path']).rename(q_hosts_csv_info['target_csv_file_path'])
            Path(q_qids_csv_info['target_tmp_csv_file_path']).rename(q_qids_csv_info['target_csv_file_path'])
        else:


            # Added 4/10/2025 for testing improvement to parsing errors.
            if etld_lib_config.xmltodict_parse_using_codec_to_replace_utf8_error is True:
                try:
                    xml_content = codecs.decode(xml_file_fd.read(), encoding='utf-8', errors='strict')
                    xmltodict.parse(xml_content, item_depth=4, item_callback=callback_to_insert_host_into_sqlite_and_csv )
                except UnicodeDecodeError as e:
                    etld_lib_functions.logger.warning(f"decoding issue, fixing decoding issue in {str(xml_file)}: {str(e)}")
                    xml_file_fd.seek(0)  # Reset file pointer
                    xml_content = codecs.decode(xml_file_fd.read(), encoding='utf-8', errors='replace')
                    xmltodict.parse(xml_content, item_depth=4, item_callback=callback_to_insert_host_into_sqlite_and_csv )
            else:
                try:
                    xmltodict.parse(xml_file_fd, item_depth=4, item_callback=callback_to_insert_host_into_sqlite_and_csv )
                except Exception as e:
                    etld_lib_functions.logger.error(f"decoding error, error in {str(xml_file)}: {str(e)}")
                    etld_lib_functions.logger.error(f"Rerun after setting xmltodict_parse_using_codec_to_replace_utf8_error: True")
                    exit(1)

            # COMMENTED OUT 4/10/2025 for testing.
            # if etld_lib_config.xmltodict_parse_using_codec_to_replace_utf8_error is False:
            #     etld_lib_functions.logger.info(f"xmltodict.parse begin transaction")
            #     xmltodict.parse(xml_file_fd.read(),
            #                     item_depth=4,
            #                     item_callback=callback_to_insert_host_into_sqlite_and_csv
            #                     )
            #     etld_lib_functions.logger.info(f"xmltodict.parse end Transaction.")
            # else:
            #     xmltodict.parse(codecs.decode(xml_file_fd.read(), encoding='utf-8', errors='replace'),
            #                     item_depth=4,
            #                     item_callback=callback_to_insert_host_into_sqlite_and_csv
            #                     )

        # sqlite_obj.commit_changes()
        csv_distribution_dict = None


def load_one_file_into_sqlite(sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
                              file_path: Path,
                              counter_obj: dict,
                              from_queue_or_directory="Queue",
                              batch_number: int = 0,
                              batch_name: str = "batch_000000",
                              batch_date: str = "2022-01-01 00:00:00",
                              ):
    etld_lib_functions.logger.info(f"Received batch file from {from_queue_or_directory}: {batch_name}")
    sqlite_obj.update_status_table(
        batch_date=batch_date, batch_number=batch_number,
        total_rows_added_to_database=counter_obj['counter_obj_host_list_detection_hosts'].get_counter(),
        status_table_name=etld_lib_config.host_list_detection_status_table_name,
        status_table_columns=etld_lib_config.status_table_csv_columns(),
        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
        status_name_column=etld_lib_config.host_list_detection_hosts_table_name,
        status_column='begin')
    try:
        etld_lib_functions.logger.info(f"Begin insert_xml_file_into_sqlite: {from_queue_or_directory}: {batch_name}")
        insert_xml_file_into_sqlite(file_path, sqlite_obj, counter_obj)
        etld_lib_functions.logger.info(f"End   insert_xml_file_into_sqlite: {from_queue_or_directory}: {batch_name}")
    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Issue inserting xml file into sqlite: {file_path}, counter={counter_obj}")
        exit(1)

    sqlite_obj.update_status_table(
        batch_date=batch_date, batch_number=batch_number,
        total_rows_added_to_database=counter_obj['counter_obj_host_list_detection_hosts'].get_counter(),
        status_table_name=etld_lib_config.host_list_detection_status_table_name,
        status_table_columns=etld_lib_config.status_table_csv_columns(),
        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
        status_name_column=etld_lib_config.host_list_detection_hosts_table_name,
        status_column='end')
    etld_lib_functions.logger.info(f"Committed batch file to Database: {batch_name}")


def spawn_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite():
    queue_of_file_paths_to_load_to_sqlite = Queue()
    queue_process_to_load_to_sqlite = \
        Process(
            target=host_list_detection_transform_and_load_all_xml_files_into_sqlite,
            args=(queue_of_file_paths_to_load_to_sqlite, True),
            name="load_all_xml_files_into_sqlite")
    queue_process_to_load_to_sqlite.daemon = True
    queue_process_to_load_to_sqlite.start()

    queue_of_file_paths_to_load_to_sqlite.put("BEGIN")
    etld_lib_functions.logger.info(f"Queue of files process id: {queue_process_to_load_to_sqlite.pid} ")

    return queue_process_to_load_to_sqlite, queue_of_file_paths_to_load_to_sqlite


def load_files_into_sqlite_via_multiprocessing_queue(
        sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
        queue_of_file_paths,
        counter_obj=None,
):
    def get_next_file_in_queue(bookend, queue_file_path):
        time.sleep(2)
        queue_data = queue_file_path.get()
        if queue_data == bookend:
            etld_lib_functions.logger.info(f"Found {bookend} of Queue.")
            queue_data = bookend
        return queue_data

    file_path = get_next_file_in_queue('BEGIN', queue_of_file_paths)
    batch_number = ""
    batch_date = ""
    if file_path == 'BEGIN':
        while True:
            file_path = get_next_file_in_queue('END', queue_of_file_paths)
            if file_path == 'END':
                sqlite_obj.update_status_table(
                    batch_date=batch_date, batch_number=batch_number,
                    total_rows_added_to_database=counter_obj['counter_obj_host_list_detection_hosts'].get_counter(),
                    status_table_name=etld_lib_config.host_list_detection_status_table_name,
                    status_table_columns=etld_lib_config.status_table_csv_columns(),
                    status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                    status_name_column=etld_lib_config.host_list_detection_hosts_table_name,
                    status_column='final')

                sqlite_obj.update_status_table(
                    batch_date=batch_date, batch_number=batch_number,
                    total_rows_added_to_database=counter_obj['counter_obj_host_list_detection_qids'].get_counter(),
                    status_table_name=etld_lib_config.host_list_detection_status_table_name,
                    status_table_columns=etld_lib_config.status_table_csv_columns(),
                    status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                    status_name_column=etld_lib_config.host_list_detection_qids_table_name,
                    status_column='final')

                # etl_workflow_sqlite_obj.update_status_table(
                #     batch_date=batch_date,
                #     batch_number=0,
                #     total_rows_added_to_database=0,
                #     etl_workflow_status_table_name=etld_lib_config.host_list_detection_status_table_name,
                #     status_table_columns=etld_lib_config.status_table_csv_columns(),
                #     status_table_column_types=etld_lib_config.status_table_csv_column_types(),
                #     status_name_column='ALL_TABLES_LOADED_SUCCESSFULLY',
                #     status_column='final')
                break  # SUCCESSFUL END

            batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(file_path)
            batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(file_path)
            batch_name = etld_lib_extract_transform_load.get_batch_name_from_filename(file_path)
            load_one_file_into_sqlite(sqlite_obj=sqlite_obj,
                                      file_path=file_path,
                                      counter_obj=counter_obj,
                                      from_queue_or_directory="Queue",
                                      batch_number=batch_number,
                                      batch_name=batch_name,
                                      batch_date=batch_date,
                                      )
            sqlite_obj.commit_changes()
    else:
        etld_lib_functions.logger.error(f"Invalid begin of Queue, {file_path}.  Please restart.")
        exit(1)


def load_files_into_sqlite_via_directory_listing(sqlite_obj: etld_lib_sqlite_tables.SqliteObj,
                                                 extract_dir,
                                                 extract_dir_file_search_blob,
                                                 counter_obj,
                                                 ):
    xml_file_list = []
    for file_name in sorted(Path(extract_dir).glob(extract_dir_file_search_blob)):
        if str(file_name).endswith('.xml') or str(file_name).endswith('.xml.gz'):
            xml_file_list.append(file_name)

    batch_number = ""
    batch_date = ""

    for file_path in xml_file_list:
        batch_number = etld_lib_extract_transform_load.get_batch_number_from_filename(file_path)
        batch_date = etld_lib_extract_transform_load.get_batch_date_from_filename(file_path)
        batch_name = etld_lib_extract_transform_load.get_batch_name_from_filename(file_path)
        load_one_file_into_sqlite(sqlite_obj=sqlite_obj,
                                  file_path=file_path,
                                  counter_obj=counter_obj,
                                  from_queue_or_directory="directory",
                                  batch_number=batch_number,
                                  batch_name=batch_name,
                                  batch_date=batch_date,
                                  )
        sqlite_obj.commit_changes()

    sqlite_obj.update_status_table(
        batch_date=batch_date, batch_number=batch_number,
        total_rows_added_to_database=counter_obj['counter_obj_host_list_detection_hosts'].get_counter(),
        status_table_name=etld_lib_config.host_list_detection_status_table_name,
        status_table_columns=etld_lib_config.status_table_csv_columns(),
        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
        status_name_column=etld_lib_config.host_list_detection_hosts_table_name,
        status_column='final')

    sqlite_obj.update_status_table(
        batch_date=batch_date, batch_number=batch_number,
        total_rows_added_to_database=counter_obj['counter_obj_host_list_detection_qids'].get_counter(),
        status_table_name=etld_lib_config.host_list_detection_status_table_name,
        status_table_columns=etld_lib_config.status_table_csv_columns(),
        status_table_column_types=etld_lib_config.status_table_csv_column_types(),
        status_name_column=etld_lib_config.host_list_detection_qids_table_name,
        status_column='final')

    sqlite_obj.commit_changes()

    # etl_workflow_sqlite_obj.update_status_table(
    #     batch_date=batch_date,
    #     batch_number=0,
    #     total_rows_added_to_database=0,
    #     etl_workflow_status_table_name=etld_lib_config.host_list_detection_status_table_name,
    #     status_table_columns=etld_lib_config.status_table_csv_columns(),
    #     status_table_column_types=etld_lib_config.status_table_csv_column_types(),
    #     status_name_column='ALL_TABLES_LOADED_SUCCESSFULLY',
    #     status_column='final')


def host_list_detection_transform_and_load_all_xml_files_into_sqlite(
        queue_of_file_paths: Queue = Queue(), multiprocessing_flag=False):
    begin_host_list_detection_05_transform_load()
    xml_file_path = ""
    counter_obj_dict = create_counter_objects()
    try:
        host_list_detection_sqlite_obj = etld_lib_sqlite_tables.SqliteObj(
            sqlite_file=etld_lib_config.host_list_detection_sqlite_file)
        drop_and_create_all_tables(
            sqlite_obj=host_list_detection_sqlite_obj)
        #
        update_host_list_in_host_list_detection_database(sqlite_obj=host_list_detection_sqlite_obj)

        if multiprocessing_flag is True:
            load_files_into_sqlite_via_multiprocessing_queue(
                sqlite_obj=host_list_detection_sqlite_obj,
                queue_of_file_paths=queue_of_file_paths,
                counter_obj=counter_obj_dict
            )
        else:
            load_files_into_sqlite_via_directory_listing(
                sqlite_obj=host_list_detection_sqlite_obj,
                counter_obj=counter_obj_dict,
                extract_dir=etld_lib_config.host_list_detection_extract_dir,
                extract_dir_file_search_blob=etld_lib_config.host_list_detection_extract_dir_file_search_blob,
            )

        for counter_obj_key in counter_obj_dict.keys():
            counter_obj_dict[counter_obj_key].display_final_counter_to_log()

        # TODO update final batch number as multiprocessing results in out of order last batch
        # Move to end of program update_final_status_in_host_list_detection_database(sqlite_obj=host_list_detection_sqlite_obj)
        host_list_detection_sqlite_obj.close_connection()
        end_host_list_detection_05_transform_load()

    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Issue with xml file: {xml_file_path}")
        exit(1)


def host_list_detection_05_update_knowledgebase(refresh_knowledgebase_flag=True):
    begin_host_list_detection_05_update_knowledgebase()

    try:
        update_knowledgebase_in_host_list_detection_database(refresh_knowledgebase_flag=refresh_knowledgebase_flag)
    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Issue updating knowledgebase")
        exit(1)

    end_host_list_detection_05_update_knowledgebase()


def host_list_detection_05_final_validation():
    sqlite_file = etld_lib_config.host_list_detection_sqlite_file
    try:
        sqlite_obj = etld_lib_sqlite_tables.SqliteObj(sqlite_file=sqlite_file)
        sqlite_obj.validate_all_tables_loaded_successfully()
        sqlite_obj.close_connection()

    except Exception as e:
        etld_lib_functions.logger.error(f"Exception: {e}")
        etld_lib_functions.logger.error(f"Issue updating final validation for {sqlite_file}")
        exit(1)


def end_message_info():
    xml_file_list = sorted(
        Path(etld_lib_config.host_list_detection_extract_dir).glob(
            etld_lib_config.host_list_detection_extract_dir_file_search_blob))
    for host_list_detection_xml_file in xml_file_list:
        if str(host_list_detection_xml_file).endswith('.xml') or str(host_list_detection_xml_file).endswith('.xml.gz'):
            etld_lib_functions.log_file_info(host_list_detection_xml_file, 'input file')


def end_host_list_detection_05_transform_load():
    end_message_info()
    etld_lib_functions.logger.info(f"end")


def begin_host_list_detection_05_transform_load():
    etld_lib_functions.logger.info("start")


def end_host_list_detection_05_update_knowledgebase():
    etld_lib_functions.logger.info(f"end")


def begin_host_list_detection_05_update_knowledgebase():
    etld_lib_functions.logger.info("start")


def main(multiprocessing_flag=False, queue_of_file_paths: Queue = Queue(), run_transform=True,
         refresh_knowledgebase_flag=True):
    # Multiprocessing is executed through spawn_multiprocessing_queue_to_transform_and_load_xml_files_into_sqlite()
    # Toggle run_transform and refresh_knowledgebase_flag for testing.
    if run_transform:
        host_list_detection_transform_and_load_all_xml_files_into_sqlite(multiprocessing_flag=multiprocessing_flag,
                                                                         queue_of_file_paths=queue_of_file_paths)
    host_list_detection_05_update_knowledgebase(refresh_knowledgebase_flag)
    update_final_status_in_host_list_detection_database()
    host_list_detection_05_final_validation()


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='host_list_detection_05_transform_load_xml_to_sqlite')
    etld_lib_config.main()
    # etld_lib_credentials.main()
    etld_lib_authentication_objects.main()
    main(multiprocessing_flag=False, queue_of_file_paths=Queue(), run_transform=True, refresh_knowledgebase_flag=False)
    # Toggle run_transform and refresh_knowledgebase_flag for testing.
