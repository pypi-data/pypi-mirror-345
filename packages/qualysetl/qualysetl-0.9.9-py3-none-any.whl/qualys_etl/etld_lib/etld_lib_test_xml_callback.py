import xmltodict
from gzip import GzipFile
from pathlib import Path
import io
import codecs
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions

# IN MEMORY PARSING IS FASTED.

def xml_data(element_names, document_item: dict):
    if len(element_names) > 2 and "HOST" != element_names[3][0]:
        etld_lib_functions.logger.info(document_item['ASSET_ID'])
#    else:
#        etld_lib_functions.logger.info(document_item['ASSET_ID'])
    return True


def process_files():
    xml_file_list = []
    for file_name in sorted(Path(etld_lib_config.host_list_detection_extract_dir).glob(
            etld_lib_config.host_list_detection_extract_dir_file_search_blob)):
        if str(file_name).endswith('.xml.gz'):
            xml_file_list.append(file_name)

    for file_path in xml_file_list:
        etld_lib_functions.logger.info(file_path)
        try:
            with GzipFile(file_path, 'rb') as gz_file:
                xmltodict.parse(
                    (codecs.decode(gz_file.read(), encoding='utf-8', errors='replace')),
                    item_depth=4,
                    item_callback=xml_data
                )
        except Exception as e:
            etld_lib_functions.logger.error(f"Error processing {file_path}: {e}")
            exit(1)


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='etld_lib_test_xml_callback')
    etld_lib_config.main()
    process_files()