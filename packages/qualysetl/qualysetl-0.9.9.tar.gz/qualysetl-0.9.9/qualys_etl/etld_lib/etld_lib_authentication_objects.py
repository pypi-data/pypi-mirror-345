import base64
import time
import requests
from pathlib import Path
import shutil
import yaml
# 2023-05-13 import oschmod
import re
import os
import stat
from urllib.parse import urlencode, quote_plus
from qualys_etl.etld_lib import etld_lib_functions
from qualys_etl.etld_lib import etld_lib_config
from qualys_etl.etld_lib import etld_lib_datetime
from qualys_etl.etld_lib import etld_lib_timer_obj
from qualys_etl.etld_lib import etld_lib_oschmod as oschmod
from qualys_etl.etld_lib import etld_lib_qualys_platform_identification
from dataclasses import dataclass
import qualys_etl

global qualys_authentication_obj
#global qualys_basic_authorization_obj
#global qualys_bearer_token_obj

@dataclass
class QualysAuthenticationObj:

    def __init__(self, username="", password="", api_fqdn_server="", gateway_fqdn_server="",
                 acquire_bearer_token=False, max_bearer_token_age=900, test_basic_authorization=False,
                 initialize_etld_cred_yaml_flag=True,
                 logger_info=print, logger_error=print, logger_warning=print,
                 http_user_agent_etl_workflow_message="auth_obj", test_about_qualys_flag=True,
                 get_qualys_portal_version_flag=False):
        self.username = username
        self.password = password
        self.api_fqdn_server = api_fqdn_server
        self.gateway_fqdn_server = gateway_fqdn_server
        self.authorization = ""
        self.bearer = ""
        self.bearer_timer_obj : etld_lib_timer_obj.TimerObj = ""
        self.bearer_token_required = acquire_bearer_token
        self.max_bearer_token_age = max_bearer_token_age
        self.get_bearer_token_from_qualys_succeeded = False
        self.test_authorization_result = False
        self.test_about_qualys_flag = test_about_qualys_flag
        self.get_qualys_portal_version_flag = get_qualys_portal_version_flag
        self.test_basic_authorization = test_basic_authorization
        self.initialize_etld_cred_yaml_flag = initialize_etld_cred_yaml_flag
        self.logger_info = logger_info
        self.logger_error = logger_error
        self.logger_warning = logger_warning
        self.http_user_agent_etl_workflow_message = http_user_agent_etl_workflow_message
        self.credentials_source = ""
        self.set_credentials()
        self._set_authorization()
        self.test_qualys_login_logout_basic_auth_result_dict = ""
        if self.test_about_qualys_flag:
            self.test_about_qualys()
        if self.get_qualys_portal_version_flag:
            self.get_qualys_portal_version()
        if self.bearer_token_required:
            self.bearer = self.get_current_bearer_token()
        if self.test_basic_authorization:
            self.test_authorization_result = \
                self.test_qualys_login_logout_basic_auth(
                    username=self.username, password=self.password, api_fqdn_server=self.api_fqdn_server)

    def get_authorization(self) -> str:
        if self.authorization == "":
            self._set_authorization()
        return self.authorization

    def _set_authorization(self, username="", password=""):

        def get_base64_encoding(username="", password=""):
            auth_base64 = ""
            if username != "" and password != "":
                auth_base64 = 'Basic ' + base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
            return auth_base64

        if username != "" and password != "":
            self.authorization = get_base64_encoding(username, password)
        elif self.username != "" and self.password != "":
            self.authorization = get_base64_encoding(self.username, self.password)
        else:
            self.authorization = ""

    def _get_gateway_fqdn_server(self):
        if self.gateway_fqdn_server == "":
            self._set_gateway_fqdn_server()
        return self.gateway_fqdn_server

    def _set_gateway_fqdn_server(self, api_fqdn_server="", gateway_fqdn_server=""):
        def get_gateway_platform_fqdn(api_fqdn_server) -> str:
            platform_identification = \
                etld_lib_qualys_platform_identification.get_platform_identification_with_fqdn(api_fqdn_server)
            if platform_identification:
                gateway_fqdn_server = platform_identification['gateway']
            else:
                gateway_fqdn_server = ""
            return gateway_fqdn_server

        # def get_gateway_platform_fqdn(api_fqdn_server) -> str:
        #     platform_url = self.get_platform_url_dict()
        #     gateway_fqdn_server = ""
        #     if api_fqdn_server in platform_url.keys():
        #         gateway_fqdn_server = platform_url[api_fqdn_server]
        #     return gateway_fqdn_server

        if gateway_fqdn_server != "":
            self.gateway_fqdn_server = gateway_fqdn_server
        elif api_fqdn_server != "":
            self.gateway_fqdn_server = get_gateway_platform_fqdn(api_fqdn_server)
        else:
            self.gateway_fqdn_server = get_gateway_platform_fqdn(self.api_fqdn_server)

    def get_credentials(self) -> dict:
        cred = {'username': self.username, 'password': self.password,
                'api_fqdn_server': self.api_fqdn_server, 'gateway_fqdn_server': self.gateway_fqdn_server}
        return cred

    def set_credentials(self, force_from_file=False):

        def initialize_eltd_cred_yaml_file(cred_file: Path = None):
            if not Path.is_file(cred_file):
                etld_lib_config.set_qetl_code_dir_etld_cred_yaml_template_path()
                cred_example_file_path = Path(etld_lib_config.qetl_code_dir_etld_cred_yaml_template_path)
                #cred_example_file_path = Path(etld_lib_config.set_qetl_code_dir_etld_cred_yaml_template_path())
                destination_file_path = Path(etld_lib_config.qetl_user_cred_file)
                shutil.copy(str(cred_example_file_path), str(destination_file_path), follow_symlinks=True)
                cred_example_file = open(str(cred_example_file_path), "r", encoding='utf-8')
                cred_example = cred_example_file.read()
                cred_example_file.close()
                local_date = etld_lib_datetime.get_local_date()  # Add date updated to file
                cred_example = re.sub('\$DATE', local_date, cred_example)
                cred_file_example = open(str(cred_file), 'w', encoding='utf-8')
                cred_file_example.write(cred_example)
                cred_file_example.close()
            oschmod.set_mode(str(cred_file), "u+rw,u-x,go-rwx")

        def set_credentials_from_environment(username="", password="", api_fqdn_server="", gateway_fqdn_server=""):
            k = os.environ.keys()
            if 'q_username' in k:
                username = os.environ.get('q_username')
            if 'q_password' in k:
                password = os.environ.get('q_password')
            if 'q_api_fqdn_server' in k:
                api_fqdn_server = os.environ.get('q_api_fqdn_server')
            if 'q_gateway_fqdn_server' in k:
                gateway_fqdn_server = os.environ.get('q_gateway_fqdn_server')

            if username != "" and password != "" and api_fqdn_server != "":
                self.username = username
                self.password = password
                self.api_fqdn_server = api_fqdn_server
                self.gateway_fqdn_server = gateway_fqdn_server
                self.credentials_source = 'set_credentials_from_environment'
                self.logger_info("set_credentials_from_environment: "
                                               f"username: {username}, "
                                               f"api_fqdn_server:  {api_fqdn_server}, "
                                               f"gateway_fqdn_server={gateway_fqdn_server}")

        def set_credentials_from_yaml_file(cred_file=""):
            try:
                with open(cred_file, 'r', encoding='utf-8') as cred_yaml_file:
                    cred = yaml.safe_load(cred_yaml_file)
                    if 'username' in cred.keys() and 'password' in cred.keys() and 'api_fqdn_server' in cred.keys():
                        username = cred['username']
                        password = cred['password']
                        api_fqdn_server = cred['api_fqdn_server']
                    else:
                        self.logger_error(f"cred yaml contents: {cred}")
                        raise Exception(f"credentials not in file: {cred_file}")

                    if 'gateway_fqdn_server' in cred.keys():
                        gateway_fqdn_server = cred['gateway_fqdn_server']
                    else:
                        self._set_gateway_fqdn_server(api_fqdn_server=api_fqdn_server)
                        gateway_fqdn_server = self._get_gateway_fqdn_server()

                    self.username = username
                    self.password = password
                    self.api_fqdn_server = api_fqdn_server
                    self.gateway_fqdn_server = gateway_fqdn_server
                    self.credentials_source = 'set_credentials_from_yaml_file'
                    self.logger_info("set_credentials_from_yaml_file: "
                                                       f"username: {username}, "
                                                       f"api_fqdn_server:  {api_fqdn_server}, "
                                                       f"gateway_fqdn_server={gateway_fqdn_server}")

            except Exception as e:
                self.logger_error(f"Please remove corrupted credentials file: {cred_file} and rerun qetl_manage_user -c -u [yourdir] to rebuild credentials file.")
                self.logger_error(f"Exception: {e}")
                raise Exception(f"Exception {e}")

        def set_credentials_from_vault(vault_type='hashicorp'):
            # Holder for vault
            pass

        #
        # MAIN ROUTINE
        #

        if self.initialize_etld_cred_yaml_flag:
            initialize_eltd_cred_yaml_file(cred_file=etld_lib_config.qetl_user_cred_file)

        obtain_credentials_from_vault = False
        if force_from_file:
            set_credentials_from_yaml_file(cred_file=etld_lib_config.qetl_user_cred_file)
        elif self.username != "" or self.api_fqdn_server != "" or self.gateway_fqdn_server != "" or self.password != "":
            self.credentials_source = 'Testing - QualysAuthenticationObject __init__ args'
            self.logger_info("set_credentials_at_init_options: "
                             f"username: {self.username}, "
                             f"api_fqdn_server:  {self.api_fqdn_server}, "
                             f"gateway_fqdn_server={self.gateway_fqdn_server}")
        elif 'q_username' in os.environ.keys() \
                and 'q_password' in os.environ.keys() \
                and 'q_api_fqdn_server' in os.environ.keys():
            set_credentials_from_environment()
        elif obtain_credentials_from_vault:
            # Add method to obtain credentials from vault
            pass
        else:
            set_credentials_from_yaml_file(cred_file=etld_lib_config.qetl_user_cred_file)

        if self.username == "" or self.password == "" or self.api_fqdn_server == "" or self.credentials_source == "":
            self.logger_error("Could not set credentials. Please ensure credentials are set via stdin, environment or in .etld_cred.yaml.")
            exit(1)

    def update_yaml_file_credentials(self, new_cred):
        # Get Current .etld_cred.yaml file
        with open(etld_lib_config.qetl_user_cred_file, 'r', encoding='utf-8') as cred_yaml_file:
            current_cred = yaml.safe_load(cred_yaml_file)
        # Get Template
        cred_example_file_path = Path(etld_lib_config.qetl_code_dir_etld_cred_yaml_template_path)
        with open(str(cred_example_file_path), "r", encoding='utf-8') as cred_template_file:
            cred_template_string = cred_template_file.read()
        # Update Template # username: initialuser  password: initialpassword  api_fqdn_server: qualysapi.qualys.com
        if current_cred == new_cred:
            pass
        else:
            if new_cred['username'] == current_cred['username']:
                new_username = f"username: '{current_cred.get('username')}'"
            else:
                new_username = f"username: '{new_cred.get('username')}'"

            if new_cred['password'] == current_cred['password']:
                new_password = f"password: '{current_cred.get('password')}'"
            else:
                new_password = f"password: '{new_cred.get('password')}'"

            if new_cred['api_fqdn_server'] == current_cred['api_fqdn_server']:
                new_api_fqdn_server = f"api_fqdn_server: '{current_cred.get('api_fqdn_server')}'"
            else:
                new_api_fqdn_server = f"api_fqdn_server: '{new_cred.get('api_fqdn_server')}'"

            if new_cred['gateway_fqdn_server'] == current_cred['gateway_fqdn_server']:
                new_gateway_fqdn_server = f"gateway_fqdn_server: '{current_cred.get('gateway_fqdn_server')}'"
            else:
                new_gateway_fqdn_server = f"gateway_fqdn_server: '{new_cred.get('gateway_fqdn_server')}'"

            local_date = etld_lib_datetime.get_local_date()
            cred_template_string = re.sub('\$DATE', local_date, cred_template_string)
            cred_template_string = re.sub('username: initialuser', new_username, cred_template_string)
            # cred_template_string = re.sub('password: initialpassword', new_password, cred_template_string)
            cred_template_string = cred_template_string.replace('password: initialpassword', new_password)
            cred_template_string = re.sub('api_fqdn_server: qualysapi.qualys.com', new_api_fqdn_server,
                                          cred_template_string)
            cred_template_string = re.sub('gateway_fqdn_server: gateway.qg1.apps.qualys.com', new_gateway_fqdn_server,
                                          cred_template_string)
            with open(etld_lib_config.qetl_user_cred_file, 'w', encoding='utf-8') as cred_file_to_update:
                cred_file_to_update.write(cred_template_string)
            oschmod.set_mode(etld_lib_config.qetl_user_cred_file, "u+rw,u-x,go-rwx")

    def get_current_bearer_token(self, force_update_to_bearer_token=False) -> str:
        if force_update_to_bearer_token:
            self.bearer = ""
            self.bearer_timer_obj = ""

        if self.bearer == "":
            self.bearer = self._get_bearer_token_from_qualys()
            if self.bearer == "":
                self.get_bearer_token_from_qualys_succeeded = False
            else:
                self.get_bearer_token_from_qualys_succeeded = True

        if self.bearer_timer_obj == "" and self.get_bearer_token_from_qualys_succeeded:
            self.bearer_timer_obj = etld_lib_timer_obj.TimerObj(max_time=self.max_bearer_token_age)

        if self.get_bearer_token_from_qualys_succeeded:
            max_time_exceeded_flag = \
                self.bearer_timer_obj.if_time_elapsed_past_max_time(max_time=self.max_bearer_token_age)
            if max_time_exceeded_flag:
                self.bearer = self._get_bearer_token_from_qualys(
                    gateway_fqdn_server=self.gateway_fqdn_server,
                    username=self.username,
                    password=self.password
                )
                if self.bearer == "":
                    self.get_bearer_token_from_qualys_succeeded = False
                else:
                    self.get_bearer_token_from_qualys_succeeded = True
                    self.bearer_timer_obj.reset_timer()

        return self.bearer

    def _get_bearer_token_from_qualys(self, gateway_fqdn_server="", username="", password="") -> str:

        bearer_token = ""
        if gateway_fqdn_server == "":
            gateway_fqdn_server = self.gateway_fqdn_server
            if gateway_fqdn_server == "":
                self._set_gateway_fqdn_server(api_fqdn_server=self.api_fqdn_server)
        if gateway_fqdn_server == "" or username == "" or password == "":
            gateway_fqdn_server = self.gateway_fqdn_server
            username = self.username
            password = self.password

        if gateway_fqdn_server == "" or username == "" or password == "":
            self.logger_error(f"Please add gateway_fqdn_server credentials file or environment.  "
                                            f"gateway: {gateway_fqdn_server}, username: {username}")
            return bearer_token

        url = f"https://{gateway_fqdn_server}/auth"  # Qualys Endpoint
        payload = {'token': 'true', 'password': password, 'username': username, 'permissions': 'true'}
        payload = urlencode(payload, quote_via=quote_plus)

        headers = {'X-Requested-With': f'qualysetl_v{qualys_etl.__version__} {self.http_user_agent_etl_workflow_message}',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'User-Agent': f"qualysetl_v{qualys_etl.__version__} {self.http_user_agent_etl_workflow_message}"}

        max_retries = 10
        sleep_time_requests_module_failed = 600
        sleep_time_503 = 30
        retry_number = 0
        for retry_number in range(max_retries):
            try:
                response = requests.request("POST", url, headers=headers, data=payload,
                                            verify=etld_lib_config.requests_module_tls_verify_status)
                if isinstance(response, str):  # Edge Case
                    self.gateway_log_message(
                        response=response,
                        message=f"Gateway Login Failed - Retry number {retry_number} for response set to str",
                        log_level=self.logger_warning)
                    time.sleep(sleep_time_503)
                elif requests.models.Response != type(response):  # Edge Case
                    self.gateway_log_message(
                        response=response,
                        message=f"Gateway Login Failed - Retry number {retry_number} as response is not equal to requests.models.Response type(response): {type(response)}",
                        log_level=self.logger_warning)
                    time.sleep(sleep_time_503)
                elif response.status_code == 503 or response.status_code == 500:  # 503/500:  # Service Temporarily Unavailable
                    self.gateway_log_message(
                        response=response,
                        message=f"Gateway Login Failed - Retry number {retry_number} for HTTP Response Code: {response.status_code} ",
                        log_level=self.logger_warning)
                    time.sleep(sleep_time_503)
                elif response.status_code == 201: # Success
                    bearer_token = f"Bearer {response.text}"
                    if self.bearer_timer_obj == "":
                       bearer_timer_obj_message = "bearer_timer_obj= NOT SET"
                    else:
                        bearer_timer_obj_message = f"bearer_timer_obj={self.bearer_timer_obj.__dict__}"
                    self.gateway_log_message(
                        response=response,
                        message=f"Gateway Login Success - Bearer Token Reset - HTTP Response Code: {response.status_code}, max_bearer_token_age={self.max_bearer_token_age}, {bearer_timer_obj_message} ",
                        log_level=self.logger_info)
                    break
                else:
                    self.gateway_log_message(
                        response=response,
                        message=f"Gateway Login Failed - HTTP Response Code: {response.status_code} ",
                        log_level=self.logger_error)
                    break
            except requests.exceptions.RequestException as e:
                # Timeout Example
                self.gateway_log_message(
                    response="",
                    message=f"Gateway Login Failed - Exception {e}",
                    log_level=self.logger_warning)
                time.sleep(sleep_time_requests_module_failed)
        else:
            self.gateway_log_message(
                response="ALL RETRIES FAILED",
                message=f"Gateway Login Failed - Retry number {retry_number} of {max_retries}",
                log_level=self.logger_error)

        return bearer_token

    def test_about_qualys(self, message=""):
        api_fqdn_server = self.api_fqdn_server
        authorization = self.authorization

        url = f"https://{api_fqdn_server}/msp/about.php"  # Qualys Endpoint
        headers = {
            'X-Requested-With': f'qualysetl_v{qualys_etl.__version__} {self.http_user_agent_etl_workflow_message} QETLM: {message}',
            'User-Agent': f"qualysetl_v{qualys_etl.__version__} {self.http_user_agent_etl_workflow_message} QETLM: {message}",
            'Authorization': authorization}
        payload = {}

        try:
            response = requests.request("POST", url, headers=headers, data=payload,
                                        verify=etld_lib_config.requests_module_tls_verify_status)

            if response.status_code == 200:
                response_text = str(response.text).replace('\n', ' ')
                self.logger_info(f"msp/about http_response_status_code={response.status_code}, "
                                 f"response_text={response_text}")
            else:
                response_text = str(response.text).replace('\n', ' ')
                self.logger_info(f"msp/about http_response_status_code={response.status_code}, "
                                 f"response_text={response_text}")

        except Exception as e:
            self.logger_warning(f"msp/about failed with exception: {e}")

    def get_qualys_portal_version(self, message=""):
        api_fqdn_server = self.api_fqdn_server
        authorization = self.authorization

        url = f"https://{api_fqdn_server}/qps/rest/portal/version"  # Qualys Endpoint
        headers = {
            'X-Requested-With': f'qualysetl_v{qualys_etl.__version__} {self.http_user_agent_etl_workflow_message} QETLM: {message}',
            'User-Agent': f"qualysetl_v{qualys_etl.__version__} {self.http_user_agent_etl_workflow_message} QETLM: {message}",
            'Authorization': authorization}
        payload = {}

        try:
            response = requests.request("GET", url, headers=headers, data=payload,
                                        verify=etld_lib_config.requests_module_tls_verify_status)

            if response.status_code == 200:
                response_text = str(response.text).replace('\n', ' ')
                self.logger_info(f"qps/rest/portal/version http_response_status_code={response.status_code}, "
                                 f"response_text={response_text}")
            else:
                response_text = str(response.text).replace('\n', ' ')
                self.logger_info(f"qps/rest/portal/version http_response_status_code={response.status_code}, "
                                 f"response_text={response_text}")

        except Exception as e:
            self.logger_warning(f"qps/rest/portal/version failed with exception: {e}")

    def test_qualys_login_logout_basic_auth(self, api_fqdn_server="", username="", password="") -> bool:

        def test_qualys_logout(login_status_dict=None) -> dict:
            logout_status_dict = {'test_response': False, 'response_status_code': "", 'Exception': "", 'message': ""}
            if login_status_dict is None:
                logout_status_dict['test_response'] = True
                logout_status_dict['message'] = "No login_status_dict, continue without logout"
            elif login_status_dict['cookie'] == "":
                logout_status_dict['test_response'] = True
                logout_status_dict['message'] = "No login_status_dict['cookie'], continue without logout"
            else:
                url = f"https://{api_fqdn_server}/api/2.0/fo/session/"  # Qualys Endpoint
                payload = {'action': 'logout'}
                cookie = login_status_dict['cookie']
                headers = {'X-Requested-With': f'qualysetl_v{qualys_etl.__version__} {self.http_user_agent_etl_workflow_message}',
                           'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': cookie,
                           'User-Agent': f"qualysetl_v{qualys_etl.__version__} {self.http_user_agent_etl_workflow_message}"}
                try:
                    response = requests.request("POST", url, headers=headers, data=payload,
                                                verify=etld_lib_config.requests_module_tls_verify_status)
                    logout_status_dict['response_status_code'] = str(response.status_code)
                    if response.status_code == 200:
                        logout_status_dict['test_response'] = True
                except Exception as e:
                    logout_status_dict['test_response'] = False
                    logout_status_dict['message'] = "Logout with Exception, continue without logout"
                    logout_status_dict['response_status_code'] = ""
                    logout_status_dict['Exception'] = e

            return logout_status_dict

        # def get_cookie_from_response(response):
        #     cookie_dict = response.cookies.get_dict()
        #     cookie = f"DWRSESSIONID={cookie_dict['DWRSESSIONID']}; QualysSession={cookie_dict['QualysSession']}"
        #     cookie = cookie.replace('\n', '').replace('\r', '')
        #     return cookie

        def get_cookie_from_response(response):
            cookie_dict = response.cookies.get_dict()

            if 'DWRSESSIONID' in cookie_dict and 'QualysSession' in cookie_dict:
                cookie = f"DWRSESSIONID={cookie_dict['DWRSESSIONID']}; QualysSession={cookie_dict['QualysSession']}"
                cookie = cookie.replace('\n', '').replace('\r', '')
            else:
                cookie = ""

            return cookie

        def test_qualys_login(username="", password="", api_fqdn_server=""):
            login_status_dict = \
                {'test_response': False, 'response_status_code': "",
                 'Exception': "", 'message': "", 'cookie': ""}

            url = f"https://{api_fqdn_server}/api/2.0/fo/session/"
            payload = {'action': 'login', 'username': username, 'password': password}
            payload = urlencode(payload, quote_via=quote_plus)

            headers = {'X-Requested-With': f'qualysetl_v{qualys_etl.__version__} {self.http_user_agent_etl_workflow_message}',
                       'Content-Type': 'application/x-www-form-urlencoded',
                       'User-Agent': f"qualysetl_v{qualys_etl.__version__} {self.http_user_agent_etl_workflow_message}"}

            try:
                response = requests.request("POST", url, headers=headers, data=payload,
                                            verify=etld_lib_config.requests_module_tls_verify_status)
                cleaned_reponse_text = str(response.text).replace('\n', '').replace('\r', '').replace('|', '')
                login_status_dict['response_status_code'] = str(response.status_code)
                if response.status_code == 200:
                    cookie = get_cookie_from_response(response)
                    if cookie == '':
                        login_status_dict['message'] = f'Error, could not obtain cookie'
                        login_status_dict['Exception'] = f'XML Response: {cleaned_reponse_text}'
                    else:
                        login_status_dict['cookie'] = cookie
                        login_status_dict['test_response'] = True
                elif response.status_code == 401:
                    login_status_dict['message'] = 'Invalid userid/password or api_fqdn_servers.  ' \
                                                   'Please check your credentials and rerun.'
                elif str(response.status_code).startswith('5'):
                    login_status_dict['message'] = 'Please check if Qualys is in a maintenance window, and rerun.'
            except requests.exceptions.RequestException as e:
                login_status_dict['message'] = 'API Exception, determine if you have connectivity issues and rerun.'
                login_status_dict['Exception'] = e

            return login_status_dict

        if username == "" or password == "" or api_fqdn_server == "":
            username = self.username
            password = self.password
            api_fqdn_server = self.api_fqdn_server

        self.test_qualys_login_logout_basic_auth_result_dict = {}
        login_status: dict = test_qualys_login(
            username=username, password=password, api_fqdn_server=api_fqdn_server)
        self.test_qualys_login_logout_basic_auth_result_dict = login_status
        login_test_flag = False

        if login_status['test_response']:
            self.logger_info(f"LOGIN  - Qualys Success with user: {username}")
            logout_status: dict = test_qualys_logout(login_status)
            login_test_flag = True
            if logout_status['test_response']:
                self.logger_info(f"LOGOUT - Qualys Success with user: {username}")
            else:
                self.logger_warning(f"LOGOUT - Qualys did not work for user: {username}")
                self.logger_warning(f"LOGOUT - Response:  {logout_status['response_status_code']}")
                self.logger_warning(f"LOGOUT - Message:   {logout_status['message']}")
                self.logger_warning(f"LOGOUT - Exception: {logout_status['Exception']}")
        else:
            self.logger_error(f"LOGIN - Qualys did not work for user: {username}")
            self.logger_error(f"LOGIN - Response:  {login_status['response_status_code']}")
            self.logger_error(f"LOGIN - Message:   {login_status['message']}")
            self.logger_error(f"LOGIN - Exception: {login_status['Exception']}")

        return login_test_flag

    def gateway_log_message(self, response, log_level, message=""):
        if response != "":
            response_message = f", HTTP RESPONSE CODE: {response.status_code}"
        else:
            response_message = ""

        log_level(f"{message} - username={self.username}, "
                  f"api_fqdn_server={self.api_fqdn_server}, "
                  f"gateway_fqdn_server={self.gateway_fqdn_server}")

    def get_platform_url_dict(self) -> dict:
        # https://www.qualys.com/platform-identification/
        return etld_lib_qualys_platform_identification.get_platform_url_dict()
        # platform_url = {
        #     'qualysapi.qualys.com': 'gateway.qg1.apps.qualys.com',
        #     'qualysapi.qg2.apps.qualys.com': 'gateway.qg2.apps.qualys.com',
        #     'qualysapi.qg3.apps.qualys.com': 'gateway.qg3.apps.qualys.com',
        #     'qualysapi.qg4.apps.qualys.com': 'gateway.qg4.apps.qualys.com',
        #     'qualysapi.qualys.eu': 'gateway.qg1.apps.qualys.eu',
        #     'qualysapi.qg2.apps.qualys.eu': 'gateway.qg2.apps.qualys.eu',
        #     'qualysapi.qg3.apps.qualys.it': 'gateway.qg3.apps.qualys.it',
        #     'qualysapi.qg1.apps.qualys.in': 'gateway.qg1.apps.qualys.in',
        #     'qualysapi.qg1.apps.qualys.ca': 'gateway.qg1.apps.qualys.ca',
        #     'qualysapi.qg1.apps.qualys.ae': 'gateway.qg1.apps.qualys.ae',
        #     'qualysapi.qg1.apps.qualys.co.uk': 'gateway.qg1.apps.qualys.co.uk',
        #     'qualysapi.qg1.apps.qualys.com.au': 'gateway.qg1.apps.qualys.com.au',
        #     'qualysapi.qg1.apps.qualysksa.com': 'gateway.qg1.apps.qualysksa.com',
        # }
        # return platform_url

    def get_gateway_platform_fqdn(self, api_fqdn_server) -> str:
        platform_identification = \
            etld_lib_qualys_platform_identification.get_platform_identification_with_fqdn(api_fqdn_server)
        if platform_identification:
           gateway_fqdn_server = platform_identification['gateway']
        else:
            gateway_fqdn_server = ""
        # platform_url = self.get_platform_url_dict()
        # gateway_fqdn_server = ""
        # if api_fqdn_server in platform_url.keys():
        #     gateway_fqdn_server = platform_url[api_fqdn_server]
        return gateway_fqdn_server

    def get_credentials_dict(self) -> dict:
        cred = {}
        cred['username'] = self.username
        cred['password'] = self.password
        cred['api_fqdn_server'] = self.api_fqdn_server
        cred['gateway_fqdn_server'] = self.gateway_fqdn_server
        cred['authorization'] = self.get_authorization()
        cred['bearer'] = self.bearer
        return cred


def main(**qualys_authentication_obj_arguments):
    global qualys_authentication_obj
    qualys_authentication_obj = QualysAuthenticationObj(
        logger_info=etld_lib_functions.logger.info,
        logger_error=etld_lib_functions.logger.error,
        logger_warning=etld_lib_functions.logger.warning,
        **qualys_authentication_obj_arguments
    )


def main_no_logger_for_qetl_manage_user(**qualys_authentication_obj_arguments):
    global qualys_authentication_obj
    qualys_authentication_obj = QualysAuthenticationObj(**qualys_authentication_obj_arguments)


def test_qualys_authentication_obj(**main_arguments):
    main(**main_arguments)
    qualys_authentication_obj.test_qualys_login_logout_basic_auth()
    bearer_token_test = []
    jwt_token_previous = qualys_authentication_obj.get_current_bearer_token()
    for time_in_seconds in [2, 3, 4, 6, 5, 7]:
        jwt_token = qualys_authentication_obj.get_current_bearer_token()
        if jwt_token == jwt_token_previous:
            pass
        else:
            bearer_token_test.append(jwt_token)
            jwt_token_previous = jwt_token
        time.sleep(time_in_seconds)

    count = 0
    for jwt_token in bearer_token_test:
        etld_lib_functions.logger.info(f"TOKEN {count} - JWT = {str(jwt_token)[-50:]}")
        count = count + 1

    if len(bearer_token_test) == 3:
        etld_lib_functions.logger.info(f"Pass JWT Token Test, token updated 3 times at 0, 6 and 7")
    else:
        etld_lib_functions.logger.error(f"Invalid JWT Token Updates.  Should be updated only 3 times at 0, 6 and 7")

if __name__ == '__main__':
    etld_lib_functions.main()
    etld_lib_config.main()
    test_qualys_authentication_obj(max_bearer_token_age=5)
