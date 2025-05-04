#!/usr/bin/env python3
import re
import sys
import argparse

def get_platform_identifier_dict(): # Update here whenever platform identification changes.
    platform_identifier_dict = {}
    platform_identifier_dict['_'] = {'qualysapi': 'qualysapi.qualys.com', 'gateway':'gateway.qg1.apps.qualys.com', 'pod': 'US_01'}
    platform_identifier_dict['2'] = {'qualysapi': 'qualysapi.qg2.apps.qualys.com','gateway': 'gateway.qg2.apps.qualys.com', 'pod': 'US_02'}
    platform_identifier_dict['3'] = {'qualysapi': 'qualysapi.qg3.apps.qualys.com','gateway': 'gateway.qg3.apps.qualys.com', 'pod': 'US_03'}
    platform_identifier_dict['6'] = {'qualysapi': 'qualysapi.qg4.apps.qualys.com','gateway': 'gateway.qg4.apps.qualys.com', 'pod': 'US_04'}
    platform_identifier_dict['-'] = {'qualysapi': 'qualysapi.qualys.eu','gateway': 'gateway.qg1.apps.qualys.eu', 'pod': 'EU_01'}
    platform_identifier_dict['5'] = {'qualysapi': 'qualysapi.qg2.apps.qualys.eu','gateway': 'gateway.qg2.apps.qualys.eu', 'pod': 'EU_02'}
    platform_identifier_dict['!'] = {'qualysapi': 'qualysapi.qg2.apps.qualys.eu','gateway': 'gateway.qg2.apps.qualys.eu', 'pod': 'EU_02'}
    platform_identifier_dict['B'] = {'qualysapi': 'qualysapi.qg3.apps.qualys.it','gateway': 'gateway.qg3.apps.qualys.it', 'pod': 'EU_03'}
    platform_identifier_dict['8'] = {'qualysapi': 'qualysapi.qg1.apps.qualys.in','gateway': 'gateway.qg1.apps.qualys.in', 'pod': 'IN_01'}
    platform_identifier_dict['9'] = {'qualysapi': 'qualysapi.qg1.apps.qualys.ca','gateway': 'gateway.qg1.apps.qualys.ca', 'pod': 'CA_01'}
    platform_identifier_dict['7'] = {'qualysapi': 'qualysapi.qg1.apps.qualys.ae','gateway': 'gateway.qg1.apps.qualys.eu', 'pod': 'AE_01'}
    platform_identifier_dict['1'] = {'qualysapi': 'qualysapi.qg1.apps.qualys.co.uk','gateway': 'gateway.qg1.apps.qualys.co.uk', 'pod': 'UK_01'}
    platform_identifier_dict['4'] = {'qualysapi': 'qualysapi.qg1.apps.qualys.com.au','gateway': 'gateway.qg1.apps.qualys.com.au', 'pod': 'AU_01'}
    platform_identifier_dict['A'] = {'qualysapi': 'qualysapi.qg1.apps.qualysksa.com','gateway': 'gateway.qg1.apps.qualysksa.com', 'pod': 'KSA_01'}
    return platform_identifier_dict


def get_platform_identification_with_userid(qualys_userid=""):
    pattern = re.compile(r'^([a-z]+)(.)(.*)$')
    userid = qualys_userid.strip()  # Remove any leading/trailing whitespace
    match = pattern.match(userid)
    if match:
        application_id, platform_identifier, application_user = match.groups()
        platform_identifier_dict = get_platform_identifier_dict()
        if platform_identifier in platform_identifier_dict:
            return platform_identifier_dict[platform_identifier]
        else:
            return None


def get_platform_identification_with_fqdn(fqdn=""):
    qualys_fqdn = fqdn.strip()  # Remove any leading/trailing whitespace
    platform_identifier_dict = get_platform_identifier_dict()
    for key in platform_identifier_dict:
        platform_qualysapi_fqdn = platform_identifier_dict[key]['qualysapi']
        platform_gateway_fqdn = platform_identifier_dict[key]['gateway']
        if qualys_fqdn == platform_qualysapi_fqdn:
            return platform_identifier_dict[key]
        elif qualys_fqdn == platform_gateway_fqdn:
            return platform_identifier_dict[key]
    return None

def get_platform_url_dict():
    platform_identifier_dict = get_platform_identifier_dict()
    platform_url_dict = {}
    for key in platform_identifier_dict:
        platform_qualysapi_fqdn = platform_identifier_dict[key]['qualysapi']
        platform_gateway_fqdn = platform_identifier_dict[key]['gateway']
        platform_url_dict[platform_qualysapi_fqdn] = platform_gateway_fqdn

    return platform_url_dict


def test_userid_from_stdin(input_obj=sys.stdin):
        for qualys_userid in input_obj:
            qualys_userid = qualys_userid.strip()  # Remove any leading/trailing whitespace
            platform_identification_dict = get_platform_identification_with_userid(qualys_userid)
            print(f"Lookup USERID..........:{qualys_userid.strip():40} {platform_identification_dict}")


def main():
    # Test ids sent to stdin
    qualys_userid_list = ['abc_123', 'abc2123', 'abc3123', 'abc6123', 'abc-123', 'abc5123', 'abc!123', 'abcB123', 'abc8123', 'abc9123', 'abc7123', 'abc1123', 'abc4123', 'abcA123']
    gateway_fqdn_list = []
    qualysapi_fqdn_list = []
    parser = argparse.ArgumentParser()
    parser.add_argument('function', help='Name of the function to run')
    args = parser.parse_args()

    if args.function == 'test_userid_from_stdin':
        test_userid_from_stdin()
    else:
        for qualys_userid in qualys_userid_list:
            platform_identification_dict = get_platform_identification_with_userid(qualys_userid)
            gateway_fqdn_list.append(platform_identification_dict['gateway'])
            qualysapi_fqdn_list.append(platform_identification_dict['qualysapi'])
            print(f"Lookup USERID..........:{qualys_userid.strip():40} {platform_identification_dict}")

        for gateway_fqdn in gateway_fqdn_list:
            platform_identification_dict = get_platform_identification_with_fqdn(gateway_fqdn)
            print(f"Lookup gateway fqdn....:{gateway_fqdn:40} {platform_identification_dict}")

        for qualysapi_fqdn in qualysapi_fqdn_list:
            platform_identification_dict = get_platform_identification_with_fqdn(qualysapi_fqdn)
            print(f"Lookup qualysapi fqdn..:{qualysapi_fqdn:40} {platform_identification_dict}")

# Call the function
if __name__ == "__main__":
    main()
