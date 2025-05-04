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
from qualys_etl.etld_lib import etld_lib_oschmod as oschmod
from qualys_etl.etld_lib import etld_lib_qualys_platform_identification
import qualys_etl
from qualys_etl.etld_lib import etld_lib_authentication_objects

global cred_dir
global cookie_file
global bearer_file
global cred_file
global use_cookie
global login_failed
global login_gateway_failed
global http_return_code
global platform_url
global injected_stdin_cred
global qualys_authentication_obj


# https://www.qualys.com/platform-identification/
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

def get_qualys_headers(request=None):
    # 'X-Powered-By': 'Qualys:USPOD1:a6df6808-8c45-eb8c-e040-10ac13041e17:9e42af6e-c5a2-4d9e-825c-449440445cc8'
    # 'X-RateLimit-Limit': '2000'
    # 'X-RateLimit-Window-Sec': '3600'
    # 'X-Concurrency-Limit-Limit': '10'
    # 'X-Concurrency-Limit-Running': '0'
    # 'X-RateLimit-ToWait-Sec': '0'
    # 'X-RateLimit-Remaining': '1999'
    # 'Keep-Alive': 'timeout=300, max=250'
    # 'Connection': 'Keep-Alive'
    # 'Transfer-Encoding': 'chunked'
    # 'Content-Type': 'application/xml'
    if request is None:
        pass
    else:
        request_url = request.url
        url_fqdn = re.sub("(https://)([0-9a-zA-Z\.\_\-]+)(/.*$)", "\g<2>", request_url)
        url_end_point = re.sub("(https://[0-9a-zA-Z\.\_\-]+)/", "", request_url)
        x_ratelimit_limit = request.headers['X-RateLimit-Limit']
        x_ratelimit_window_sec = request.headers['X-RateLimit-Window-Sec']
        x_ratelimit_towait_sec = request.headers['X-RateLimit-ToWait-Sec']
        x_ratelimit_remaining = request.headers['X-RateLimit-Remaining']
        x_concurrency_limit_limit = request.headers['X-Concurrency-Limit-Limit']
        x_concurrency_limit_running = request.headers['X-Concurrency-Limit-Running']
        headers = {'url': request_url,
                   'api_fqdn_server': url_fqdn,
                   'api_end_point': url_end_point,
                   'x_ratelimit_limit': x_ratelimit_limit,
                   'x_ratelimit_window_sec': x_ratelimit_window_sec,
                   'x_ratelimit_towait_sec': x_ratelimit_towait_sec,
                   'x_ratelimit_remaining': x_ratelimit_remaining,
                   'x_concurrency_limit_limit': x_concurrency_limit_limit,
                   'x_concurrency_limit_running': x_concurrency_limit_running}
        return headers


def update_cred(new_cred):
    cred_example_file_path = Path(etld_lib_functions.qetl_code_dir, "qualys_etl", "etld_templates", ".etld_cred.yaml")
    # Get Current .etld_cred.yaml file
    with open(cred_file, 'r', encoding='utf-8') as cred_yaml_file:
        current_cred = yaml.safe_load(cred_yaml_file)
    # Get Template
    with open(str(cred_example_file_path), "r", encoding='utf-8') as cred_template_file:
        cred_template_string = cred_template_file.read()
    # Update Template # username: initialuser  password: initialpassword  api_fqdn_server: qualysapi.qualys.com
    if current_cred == new_cred:
        pass
    else:
        new_username = f"username: '{new_cred.get('username')}'"
        new_password = f"password: '{new_cred.get('password')}'"
        new_api_fqdn_server = f"api_fqdn_server: '{new_cred.get('api_fqdn_server')}'"
        # Gateway
        if new_api_fqdn_server in platform_url.keys():
            new_gateway_fqdn_server = f"gateway_fqdn_server: '{platform_url.get(new_cred.get('api_fqdn_server'))}'"
        elif 'gateway_fqdn_server' in new_cred.keys():
            new_gateway_fqdn_server = f"gateway_fqdn_server: '{new_cred.get('gateway_fqdn_server')}'"
        else:
            new_gateway_fqdn_server = "gateway.qg1.apps.qualys.com"

        local_date = etld_lib_datetime.get_local_date()
        cred_template_string = re.sub('\$DATE', local_date, cred_template_string)
        cred_template_string = re.sub('username: initialuser', new_username, cred_template_string)
        #cred_template_string = re.sub('password: initialpassword', new_password, cred_template_string)
        cred_template_string = cred_template_string.replace('password: initialpassword', new_password)
        cred_template_string = re.sub('api_fqdn_server: qualysapi.qualys.com', new_api_fqdn_server,
                                      cred_template_string)
        cred_template_string = re.sub('gateway_fqdn_server: gateway.qg1.apps.qualys.com', new_gateway_fqdn_server,
                                      cred_template_string)
        with open(str(cred_file), 'w', encoding='utf-8') as cred_file_to_update:
            cred_file_to_update.write(cred_template_string)
        oschmod.set_mode(str(cred_file), "u+rw,u-x,go-rwx")


def get_authorization(username, password):
    authorization = 'Basic ' + \
                    base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
    return authorization


def get_env_cred() -> dict:
    username = ""
    password = ""
    api_fqdn_server = ""
    gateway_fqdn_server = ""
    authorization = ""
    bearer = ""

    k = os.environ.keys()
    if 'q_username' in k:
        username = os.environ.get('q_username')
    if 'q_password' in k:
        password = os.environ.get('q_password')
    if 'q_api_fqdn_server' in k:
        api_fqdn_server = os.environ.get('q_api_fqdn_server')
    if 'q_gateway_fqdn_server' in k:
        gateway_fqdn_server = os.environ.get('q_gateway_fqdn_server')
    if 'q_bearer' in k:
        bearer = os.environ.get('q_bearer')

    if username != "" and password != "" and api_fqdn_server != "":
        authorization = get_authorization(username, password)
        etld_lib_functions.logger.info(f"Not using .etld_cred.yaml. Found env credentials, "
                                       f"username: {username}, api_fqdn_server:  {api_fqdn_server}")
        if gateway_fqdn_server == "":
            if api_fqdn_server in platform_url.keys():
                gateway_fqdn_server = f"{platform_url.get(api_fqdn_server)}"

    return {'api_fqdn_server': api_fqdn_server,
            'gateway_fqdn_server': gateway_fqdn_server,
            'authorization': authorization,
            'username': username,
            'password': password,
            'bearer': bearer}


def get_filesystem_cred():
    try:
        with open(cred_file, 'r', encoding='utf-8') as cred_yaml_file:
            cred = yaml.safe_load(cred_yaml_file)
            api_fqdn_server = cred.get('api_fqdn_server')
            authorization = 'Basic ' + \
                            base64.b64encode(
                                f"{cred.get('username')}:{cred.get('password')}".encode('utf-8')).decode('utf-8')
            authorization_base64 = authorization.replace('Basic ', "")
            authorization_decoded_bytearray = base64.b64decode(authorization_base64)
            authorization_decoded_string = str(authorization_decoded_bytearray, 'UTF-8')
            username, password = str(authorization_decoded_string).split(':', 1)
            cred_file_mode = stat.filemode(os.stat(cred_file).st_mode)
            etld_lib_functions.logger.info(f"Found Credentials, Ensure perms are correct for your company. "
                                           f"username: {username}, api_fqdn_server:  {api_fqdn_server}, "
                                           f"permissions: {cred_file_mode} for credentials file: {cred_file}")
            if 'gateway_fqdn_server' in cred.keys():
                gateway_fqdn_server = cred.get('gateway_fqdn_server')
            elif cred.get('api_fqdn_server') in platform_url.keys():
                gateway_fqdn_server = f"{platform_url.get(cred.get('api_fqdn_server'))}"
            else:
                gateway_fqdn_server = None

            return {'api_fqdn_server': api_fqdn_server,
                    'gateway_fqdn_server': gateway_fqdn_server,
                    'authorization': authorization,
                    'username': username,
                    'password': password}

    except Exception as e:
        etld_lib_functions.logger.error(f"Please add your subscription credentials to the:  {cred_file}")
        etld_lib_functions.logger.error(
            f"   ** Warning: Ensure Credential File permissions are correct for your company.")
        etld_lib_functions.logger.error(f"   ** Warning: Credentials File: {cred_file}")
        cred_file_mode = stat.filemode(os.stat(cred_file).st_mode)
        etld_lib_functions.logger.error(f"   ** Permissions are: {cred_file_mode} for {cred_file}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)


def get_cred(cred_dict={}):
    global cred_file
    global cred_dir

    if not Path.is_file(cred_file):
        cred_example_file_path = \
            Path(etld_lib_functions.qetl_code_dir, "qualys_etl", "etld_templates", ".etld_cred.yaml")
        destination_file_path = Path(cred_file)
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
    if 'q_password' in os.environ.keys():
        cred = get_env_cred()
    else:
        cred = get_filesystem_cred()

    if 'bearer' in cred_dict.keys():
        cred['bearer'] = cred_dict['bearer']
    else:
        cred['bearer'] = ""

    cred['timer_obj'] = None

    return {'api_fqdn_server': cred['api_fqdn_server'],
            'gateway_fqdn_server': cred['gateway_fqdn_server'],
            'authorization': cred['authorization'],
            'username': cred['username'],
            'password': cred['password'],
            'bearer': cred['bearer'],
            'timer_obj': cred['timer_obj']}


def get_bearer_stored_in_env(update_bearer=True, cred=None):
    if cred is None:
        cred = {}

    max_age_of_bearer_token = 300

    timer_obj_update_bearer = False
    # if 'timer_obj' in cred.keys() and cred['timer_obj'] is not None:
    #     timer_obj: etld_lib_functions.TimerObj = cred['timer_obj']
    #     time_elapsed = timer_obj.get_time_elapsed()
    #     time_elapsed_flag = timer_obj.if_time_elapsed_past_max_time(max_time=max_age_of_bearer_token)
    #     if time_elapsed_flag:
    #         timer_obj_update_bearer = True
    #         timer_obj.reset_timer()
    #         etld_lib_functions.logger.info(f"time elapsed: {time_elapsed:,.0f} seconds")
    #     else:
    #         timer_obj_update_bearer = False
    #     cred['timer_obj'] = timer_obj
    # else:
    #     cred['timer_obj'] = etld_lib_functions.TimerObj()

    # TODO move away from file to timerobj for bearer token update.

    try:
        if update_bearer:
            cred = qualys_gateway_login_store_in_env(cred_dict=cred)
        if cred['bearer'] == "":
            cred = qualys_gateway_login_store_in_env(cred_dict=cred)
        elif Path(bearer_file).is_file():
            age_of_file = etld_lib_datetime.get_seconds_since_last_file_modification(Path(bearer_file))
            if age_of_file > max_age_of_bearer_token:
                cred = qualys_gateway_login_store_in_env(cred_dict=cred)
                etld_lib_functions.logger.info(f"Updated Bearer Token Successfully. "
                                               f"age_of_file={age_of_file}, max_age={max_age_of_bearer_token}")
        elif timer_obj_update_bearer:
            cred = qualys_gateway_login_store_in_env(cred_dict=cred)
        else:
            cred = qualys_gateway_login_store_in_env(cred_dict=cred)

    except Exception as e:
        etld_lib_functions.logger.error(f"               Credentials Dir:  {cred_dir}")
        etld_lib_functions.logger.error(f"              Credentials File:  {cred_file}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)

    return cred


def update_cred_dict(response, cred_dict) -> dict:
    with open(bearer_file, 'w', encoding='utf-8') as bearerfile:
        bearerfile.write(f"DUMMY ENTRY FOR TIME TRACKING OF BEARER AGE")
    bearer = f"Bearer {response.text}"
    cred_dict['bearer'] = bearer
    oschmod.set_mode(str(bearer_file), "u+rw,u-x,go-rwx")
    etld_lib_functions.logger.info(f"LOGIN - Qualys Gateway Login Success with user: {cred_dict['username']}")
    return cred_dict


def qualys_gateway_login_failed_message(response, cred_dict, log_level, message=""):
    if response != "":
        response_message = f", HTTP RESPONSE CODE: {response.status_code}"
    else:
        response_message = ""

    log_level(f"Qualys Gateway Login Failed with user: {cred_dict['username']} {response_message}")
    log_level(f"{message}")
    log_level(f"Credentials Env: username:{cred_dict['username']},"
              f"api_fqdn_server:{cred_dict['api_fqdn_server']},"
              f"gateway_fqdn_server:{cred_dict['gateway_fqdn_server']}")


def qualys_gateway_login_store_in_env(cred_dict={}):
    global login_gateway_failed
    global http_return_code

    login_gateway_failed = True
    if 'gateway_fqdn_server' in cred_dict:
        if cred_dict['gateway_fqdn_server'] is None:
            etld_lib_functions.logger.error(f"Please add gateway_fqdn_server credentials file or environment.")
            exit(1)

    # Login to Qualys, return bearer token.
    url = f"https://{cred_dict['gateway_fqdn_server']}/auth"  # Qualys Endpoint
    payload = {'token': 'true', 'password': cred_dict['password'], 'username': cred_dict['username'],
               'permissions': 'true'}
    payload = urlencode(payload, quote_via=quote_plus)

    headers = {'X-Requested-With': f'qualysetl_v{qualys_etl.__version__}',
               'Content-Type': 'application/x-www-form-urlencoded',
               'User-Agent': f"qualysetl_v{qualys_etl.__version__}"}
    max_retries = 15
    sleep_time_requests_module_failed = 300
    sleep_time_503 = 10
    retry_number = 0
    for retry_number in range(max_retries):
        try:
            response = requests.request("POST", url, headers=headers, data=payload,
                                        verify=etld_lib_config.requests_module_tls_verify_status)
            http_return_code = response.status_code
            if response.status_code == 503:  # 503:  # Service Temporarily Unavailable
                qualys_gateway_login_failed_message(
                    message=f"Retry number {retry_number} for HTTP Response Code: {response.status_code} ",
                    response=response,
                    cred_dict=cred_dict,
                    log_level=etld_lib_functions.logger.warning)
                time.sleep(sleep_time_503)
            elif response.status_code == 201:
                cred_dict = update_cred_dict(response, cred_dict)
                login_gateway_failed = False
                break
            else:
                qualys_gateway_login_failed_message(
                    message=f"HTTP Response Code: {response.status_code} ",
                    response=response,
                    cred_dict=cred_dict,
                    log_level=etld_lib_functions.logger.error)
                exit(1)
        except requests.exceptions.RequestException as e:
            qualys_gateway_login_failed_message(
                message=f"Requests Module Failed {e}",
                response="",
                cred_dict=cred_dict,
                log_level=etld_lib_functions.logger.warning)
            etld_lib_functions.logger.warning(f"Exception: {e}")
            time.sleep(sleep_time_requests_module_failed)
    else:
        qualys_gateway_login_failed_message(response="ALL RETRIES FAILED",
                                            message=f"Retry number {retry_number} of {max_retries}",
                                            cred_dict=cred_dict,
                                            log_level=etld_lib_functions.logger.error)
        exit(3)

    return cred_dict


def test_qualys_login_logout_basic_auth() -> dict:

    def qualys_logout_test(login_status=None):
        if login_status is not None and login_status['cookie'] != "":
            cred_dict = get_cred()
            url = f"https://{cred_dict['api_fqdn_server']}/api/2.0/fo/session/"  # Qualys Endpoint
            payload = {'action': 'logout'}
            headers = {'X-Requested-With': f'qualysetl_v{qualys_etl.__version__}',
                       'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': login_status['cookie'],
                       'User-Agent': f"qualysetl_v{qualys_etl.__version__}"}
            try:
                response = requests.request("POST", url, headers=headers, data=payload,
                                            verify=etld_lib_config.requests_module_tls_verify_status)
                if response.status_code == 200:
                    etld_lib_functions.logger.info(f"LOGOUT - Qualys Logout Success with user: {cred_dict['username']}")
                else:
                    etld_lib_functions.logger.warning(f"LOGOUT FAILED - probably stale cookie, continue with warning")
            except Exception as e:
                etld_lib_functions.logger.warning(f"LOGOUT FAILED, probably connectivity issue, continue with warning")
                etld_lib_functions.logger.warning(f"Exception: {e}")
                pass

    def qualys_login_test() -> dict:
        login_status = {}
        login_status['login_failed'] = True
        login_status['cookie'] = ""

        cred_dict = get_cred()
        url = f"https://{cred_dict['api_fqdn_server']}/api/2.0/fo/session/"  # Qualys Endpoint
        payload = {'action': 'login', 'username': cred_dict['username'], 'password': cred_dict['password']}
        payload = urlencode(payload, quote_via=quote_plus)

        headers = {'X-Requested-With': f'qualysetl_v{qualys_etl.__version__}',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'User-Agent': f"qualysetl_v{qualys_etl.__version__}"}

        try:
            response = requests.request("POST", url, headers=headers, data=payload,
                                        verify=etld_lib_config.requests_module_tls_verify_status)
            login_status['response_status_code'] = response.status_code
            if response.status_code == 200:
                cookie_dict = response.cookies.get_dict()
                cookie = f"DWRSESSIONID={cookie_dict['DWRSESSIONID']}; QualysSession={cookie_dict['QualysSession']}"
                cookie = cookie.replace('\n', '').replace('\r', '')

                etld_lib_functions.logger.info(f"LOGIN - Qualys Login Success with user: {cred_dict['username']}")

                login_status['cookie'] = cookie
                login_status['login_failed'] = False
            else:
                etld_lib_functions.logger.error(f"Fail - Qualys Login Failed with user: {cred_dict['username']}")
                etld_lib_functions.logger.error(f"       HTTP {response.status_code}")
                etld_lib_functions.logger.error(f"       Verify Qualys username, password and "
                                                f"api_fqdn_server in Credentials File")
                etld_lib_functions.logger.error(f"             Credentials File: {cred_file}")
                etld_lib_functions.logger.error(f"             username:         {cred_dict['username']}")
                etld_lib_functions.logger.error(f"             api_fqdn_server:  {cred_dict['api_fqdn_server']}")
                exit(1)
        except requests.exceptions.RequestException as e:
            etld_lib_functions.logger.error(f"Fail - Qualys Login Failed with user")
            etld_lib_functions.logger.error(
                f"       Verify Qualys username, password and api_fqdn_server in Credentials File")
            etld_lib_functions.logger.error(f"             Credentials File: {cred_file}")
            etld_lib_functions.logger.error(f"             username:         {cred_dict['username']}")
            etld_lib_functions.logger.error(f"             api_fqdn_server:  {cred_dict['api_fqdn_server']}")
            etld_lib_functions.logger.error(f"Exception: {e}")
            exit(1)

        return login_status

    login_status = qualys_login_test()
    if login_status['login_failed']:
        pass
    else:
        qualys_logout_test(login_status)

    return login_status


def main():
    global cred_dir
    global cookie_file
    global bearer_file
    global cred_file
    global use_cookie
    global qualys_authentication_obj
    global platform_url

    platform_url = etld_lib_qualys_platform_identification.get_platform_url_dict()
    cred_dir = Path(etld_lib_config.qetl_user_cred_dir)  # Credentials Directory
    cookie_file = Path(cred_dir, ".etld_cookie")   # Never Used
    bearer_file = Path(cred_dir, ".etld_bearer")   # Dummy data, used to determine age of bearer, old replace by obj
    cred_file = Path(etld_lib_config.qetl_user_cred_file)  # YAML Format Qualys Credentials
    use_cookie = False
    # qualys_authentication_obj = etld_lib_authentication_objects.get_qualys_authentication_obj()
    # qualys_authentication_obj.get_current_bearer_token()
    # qualys_authentication_obj.get_authorization()
    # print(qualys_authentication_obj.__dir__())
    # print(qualys_authentication_obj.__dict__)

if __name__ == '__main__':
    platform_url = etld_lib_qualys_platform_identification.get_platform_url_dict()
    etld_lib_functions.main()
    etld_lib_config.main()
    main()
#    test_qualys_login_logout_basic_auth()
