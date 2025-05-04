import xmltodict
from pathlib import Path
import codecs
import json
import gzip

from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config

def transform_xml_file_to_json_file(xml_file: Path, compression_method=open, logger_method=print, use_codec_to_replace_utf8_errors=False):
    # TODO break feeds down to iterate through them without consuming memory.
    # TODO maybe add option to turn off xml to json transform.
    try:
        # if etld_lib_config.xmltodict_parse_using_codec_to_replace_utf8_error is True:
        if use_codec_to_replace_utf8_errors is True:
            xml_file_args = (str(xml_file), "rb")
            xml_file_kwargs = {}
        else:
            xml_file_args = (str(xml_file), "rt")
            xml_file_kwargs = {"encoding": "utf-8"}

        json_file = Path(str(xml_file).replace('.xml', '.json'))
        logger_method.info(f"Begin transform_xml_file_to_json {xml_file.name} to {json_file.name}")
        with compression_method(json_file, 'wt', encoding='utf-8') as json_file_fd, \
                compression_method(*xml_file_args, **xml_file_kwargs) as xml_file_fd:
                # 2024-01-26 compression_method(xml_file, 'rt', encoding='utf-8') as xml_file_fd:
                logger_method.info(f"reading xmlfile into dictionary")
                if use_codec_to_replace_utf8_errors is True:
                    dict_data = xmltodict.parse(codecs.decode(xml_file_fd.read(), encoding='utf-8', errors='replace'))
                else:
                    dict_data = xmltodict.parse(xml_file_fd.read())
                logger_method.info(f"transforming data dictionary into json file")
                json.dump(dict_data, json_file_fd)
        logger_method.info(f"End   transform_xml_file_to_json {xml_file.name} to {json_file.name}")
    except Exception as e:
        logger_method.error(f"Exception: {e}")
        logger_method.error(f"transform_xml_file_to_json_file error.")
        exit(1)

def main():
    xml_file=Path('/opt/qetl/users/corpdemo/qetl_home/data/knowledgebase_extract_dir/kb_utc_run_datetime_2025-03-21T07_00_07Z_utc_last_modified_after_1970-01-01T00_00_00Z_batch_000001.xml.gz')
    transform_xml_file_to_json_file(xml_file=xml_file, compression_method=gzip.open, logger_method=etld_lib_functions.logger, use_codec_to_replace_utf8_errors=True)


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name="etld_lib_test_transform_xml_file_to_json_file")
    etld_lib_config.main()
    main()