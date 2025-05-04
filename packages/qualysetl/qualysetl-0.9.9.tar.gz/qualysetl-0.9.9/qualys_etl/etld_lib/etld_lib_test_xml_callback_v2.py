import xmltodict
from gzip import GzipFile
from pathlib import Path
import io
import codecs
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions


# Note: BytesWrapper is defined but unused in this version
class BytesWrapper:
    def __init__(self, file_obj, encoding='utf-8', errors='replace'):
        self.text_stream = io.TextIOWrapper(file_obj, encoding=encoding, errors=errors)
        self.file_path = getattr(file_obj, 'name', 'unknown file')

    def read(self, size=-1):
        text = self.text_stream.read(size)
        if text is None:
            return b''
        if '\ufffd' in text:
            etld_lib_functions.logger.warning(
                f"Invalid XML characters found in {self.file_path}: replaced with �"
            )
        return text.encode('utf-8')


def xml_data(element_names, document_item: dict):
    if len(element_names) > 2 and "HOST" != element_names[3][0]:
        etld_lib_functions.logger.info(document_item['ASSET_ID'])
#    else:
        # etld_lib_functions.logger.info(document_item['ASSET_ID'])
    return True


def process_files():
    xml_file_list = []
    for file_name in sorted(Path(etld_lib_config.host_list_detection_extract_dir).glob(
            etld_lib_config.host_list_detection_extract_dir_file_search_blob)):
        if str(file_name).endswith('.xml.gz'):
            xml_file_list.append(file_name)

    for file_path in xml_file_list:
        print(file_path)
        try:
            with GzipFile(file_path, 'rb') as gz_file:
                # Read all bytes
                raw_bytes = gz_file.read()
                # Decode with error handling
                decoded_text = codecs.decode(raw_bytes, encoding='utf-8', errors='replace')

                # Check for UTF-8 errors (replacement characters)
                if '\ufffd' in decoded_text:
                    # Find positions and snippets of invalid characters
                    pos = -1
                    while (pos := decoded_text.find('\ufffd', pos + 1)) != -1:
                        start = max(0, pos - 10)
                        end = min(len(decoded_text), pos + 10)
                        snippet = decoded_text[start:end]
                        # Approximate original bytes (tricky since we've decoded, but we can slice raw_bytes)
                        byte_pos = int(pos * len(raw_bytes) / len(decoded_text))  # Rough estimate
                        byte_start = max(0, byte_pos - 5)
                        byte_end = min(len(raw_bytes), byte_pos + 5)
                        raw_snippet = raw_bytes[byte_start:byte_end]
                        print(f"UTF-8 error in {file_path}: "
                              f"position {pos}, snippet: {repr(snippet)}, "
                              f"original bytes (approx): {raw_snippet.hex()}")

                # Parse the fixed string
                xmltodict.parse(
                    decoded_text,
                    item_depth=4,
                    item_callback=xml_data
                )
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            exit(1)


if __name__ == "__main__":
    etld_lib_functions.main(my_logger_prog_name='etld_lib_test_xml_callback')
    etld_lib_config.main()
    process_files()