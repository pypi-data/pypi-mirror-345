import xmltodict
from gzip import GzipFile
from pathlib import Path
import io
import codecs
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_functions

class BytesStreamer:
    def __init__(self, file_obj, encoding='utf-8', errors='replace', chunk_size=8192):
        self.file_obj = file_obj
        self.encoding = encoding
        self.errors = errors
        self.chunk_size = chunk_size
        self.decoder = codecs.getincrementaldecoder(encoding)(errors)
        self.buffer = b''  # Buffer for leftover bytes
        self.position = 0
        self.file_path = getattr(file_obj, 'name', 'unknown file')

    def read(self, size=-1):
        if size < 0:
            # Read all remaining data
            raw_bytes = self.buffer + self.file_obj.read()
            self.buffer = b''
        else:
            if len(self.buffer) >= size:
                raw_bytes = self.buffer[:size]
                self.buffer = self.buffer[size:]
            else:
                raw_bytes = self.buffer + self.file_obj.read(self.chunk_size)
                self.buffer = b''

        if not raw_bytes:
            final_text = self.decoder.decode(b'', final=True)  # Flush decoder
            return final_text.encode(self.encoding)

        # Decode chunk incrementally
        text = self.decoder.decode(raw_bytes, final=False)
        if '\ufffd' in text:
            pos = -1
            while (pos := text.find('\ufffd', pos + 1)) != -1:
                start = max(0, pos - 10)
                end = min(len(text), pos + 10)
                import codecs
                import xmltodict
                from gzip import GzipFile
                from pathlib import Path
                import io
                from qualys_etl.etld_lib import etld_lib_config
                from qualys_etl.etld_lib import etld_lib_functions

                class BytesWrapper:
                    def __init__(self, file_obj):
                        self.file_obj = file_obj
                        self.file_path = getattr(file_obj, 'name', 'unknown file')
                        self.buffer = b''  # Buffer for leftover bytes
                        self.position = 0
                        self.decoder = codecs.getincrementaldecoder('utf-8')('replace')  # Incremental UTF-8 decoder

                    def read(self, size=-1):
                        if size < 0:
                            raw_bytes = self.buffer + self.file_obj.read()
                            self.buffer = b''
                        else:
                            target_size = max(1, size)  # Read exact size, adjust later
                            if len(self.buffer) >= size:
                                raw_bytes = self.buffer[:size]
                                self.buffer = self.buffer[size:]
                            else:
                                raw_bytes = self.buffer + self.file_obj.read(target_size)
                                self.buffer = b''

                        if not raw_bytes:
                            return b''

                        # Decode incrementally to detect errors
                        text = self.decoder.decode(raw_bytes, final=False)
                        if '\ufffd' in text:
                            pos = -1
                            while (pos := text.find('\ufffd', pos + 1)) != -1:
                                start = max(0, pos - 10)
                                end = min(len(text), pos + 10)
                                snippet = text[start:end]
                                byte_pos = int(pos * len(raw_bytes) / len(text)) if text else 0
                                byte_start = max(0, byte_pos - 5)
                                byte_end = min(len(raw_bytes), byte_pos + 5)
                                raw_snippet = raw_bytes[byte_start:byte_end]
                        #                etld_lib_functions.logger.warning(f"UTF-8 error in {Path(self.file_path).name}: "
                        #                      f"position {self.position + pos}, snippet: {repr(snippet)}, "
                        #                      f"original bytes: {raw_snippet.hex()}")
                        #            etld_lib_functions.logger.warning(
                        #                f"Invalid XML characters found in {self.file_path}: replaced with �"
                        #            )

                        # Re-encode to bytes
                        encoded_bytes = text.encode('utf-8')
                        if size > 0 and len(encoded_bytes) > size:
                            self.buffer = encoded_bytes[size:] + self.buffer
                            encoded_bytes = encoded_bytes[:size]

                        self.position += len(raw_bytes)
                        return encoded_bytes

                def xml_data(element_names, document_item: dict):
                    if len(element_names) > 2 and "HOST" != element_names[3][0]:
                        etld_lib_functions.logger.info(document_item['ASSET_ID'])
                    return True

                def process_files():
                    xml_file_list = []
                    for file_name in sorted(Path(etld_lib_config.host_list_detection_extract_dir).
                                                    glob(
                        etld_lib_config.host_list_detection_extract_dir_file_search_blob)):
                        if str(file_name).endswith('.xml.gz'):
                            xml_file_list.append(file_name)

                    for file_path in xml_file_list:
                        etld_lib_functions.logger.info(file_path.name)
                        try:
                            with GzipFile(file_path, 'rb') as gz_file:
                                bytes_stream = BytesWrapper(gz_file)
                                xmltodict.parse(
                                    bytes_stream,
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
                snippet = text[start:end]
                byte_pos = int(pos * len(raw_bytes) / len(text)) if text else 0
                byte_start = max(0, byte_pos - 5)
                byte_end = min(len(raw_bytes), byte_pos + 5)
                raw_snippet = raw_bytes[byte_start:byte_end]
                etld_lib_functions.logger.warning(f"UTF-8 error in {self.file_path}: "
                      f"position {self.position + pos}, snippet: {repr(snippet)}, "
                      f"original bytes: {raw_snippet.hex()}")
            # etld_lib_functions.logger.warning(
            #     f"Invalid XML characters found in {self.file_path}: replaced with �"
            # )

        encoded_bytes = text.encode(self.encoding)
        if size > 0 and len(encoded_bytes) > size:
            self.buffer = encoded_bytes[size:] + self.buffer
            encoded_bytes = encoded_bytes[:size]

        self.position += len(raw_bytes)
        return encoded_bytes

def xml_data(element_names, document_item: dict):
    if len(element_names) > 2 and "HOST" != element_names[3][0]:
        etld_lib_functions.logger.info(document_item['ASSET_ID'])
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
                streamer = BytesStreamer(gz_file, encoding='utf-8', errors='replace')
                xmltodict.parse(
                    streamer,
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