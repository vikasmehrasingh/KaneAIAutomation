import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()
prod_tests_dict = {
    "82d4db2a-cc15-4f5a-b88a-43511b08b15b": "3b57540eba6d57fdb8100cb1f137f144"
}
stage_tests_dict = {
    "82d4db2a-cc15-4f5a-b88a-43511b08b15b": "3b57540eba6d57fdb8100cb1f137f144"
}

# env = os.getenv('ENV')
env = 'stage'

if env == 'stage':
    # bearer_token = os.getenv('STAGE_BEARER_TOKEN')
    bearer_token = 'cHJhdGVla3A6UjI1dUhxR21jeTdQY3FGNGJxc2F0VjA1YVB6SExKV2ZOQkhJQUl4Z285TE5kZ096R0I='
else:
    # bearer_token = os.getenv('BEARER_TOKEN')
    bearer_token = 'cHJhdGVla3A6ZmVmWlRMdzVoWG1BTXltVzNmSm5wd2NtMHVLM25OUHk1bTViSEw1dUZoTm4wYTNIQTg='

if env == 'stage':
    # base_url = os.getenv('STAGE_BASE_URL')
    base_url = 'https://auteur-stage-test-manager.lambdatestinternal.com'
else:
    # base_url = os.getenv('BASE_URL')
    base_url = 'https://test-manager.lambdatest.com'
if env == 'stage':
    tests_dict = stage_tests_dict
else:
    tests_dict = prod_tests_dict


test_id = ""
commit_to_test = ""
fqdn = ""
new_commit = ""
commit_id = ""


def start_test(flag=False):
    start_test_url = f"{base_url}/api/atm/v1/test/{test_id}/playground?headless=true&rerun="+str(
        flag).lower()
    payload = {}
    headers = {
        'authorization': 'Basic '+bearer_token,
        'accept': 'application/json'
    }
    response = requests.request(
        "GET", start_test_url, headers=headers, data=payload)
    resp = response.json()
    print("Start call:", start_test_url, bearer_token, headers)
    global fqdn
    fqdn = resp['fqdn']
    print(f"Start Test", response)


def poll_test():
    url = f"https://{fqdn}/web-agent/health?testId={test_id}"
    payload = {}
    headers = {
        'Authorization': 'Basic '+bearer_token
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    response.raise_for_status()
    resp = response.json()
    print(base_url, bearer_token, headers)
    if response.status_code == 200:
        global new_commit
        new_commit = resp['commit_id']
        print(f"Poll Test Response:{response}")
    return response.status_code


def get_test_execution_status():
    url = f"{base_url}/api/atm/v1/test-details/{test_id}?commit_id={new_commit}"
    payload = {}
    headers = {
        'Authorization': 'Basic '+bearer_token
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    response.raise_for_status()
    resp = response.json()
    print("Last Response", resp)
    if response.status_code == 200:
        instructions: list = resp.get('data', []).get('instructions', [])
        if instructions.__len__() > 0:
            final_status = instructions[-1].get('status', None)
        else:
            final_status = "failed"
        print(f"Test id: {test_id}")
        print(f"new commit: {new_commit}")
        print(f"fqdn: {fqdn}")
        print(f"Test execution status: {final_status}")


for test in tests_dict:

    test_id = test
    commit_id = tests_dict[test]
    start_test(flag=False)
    while True:
        try:
            poll_test()
        except Exception as e:
            print(e)
            break
        time.sleep(5)
        pass
    get_test_execution_status()

for test in tests_dict:

    test_id = test
    commit_id = tests_dict[test]
    start_test(flag=True)
    while True:
        try:
            poll_test()
        except Exception as e:
            print(e)
            break
        time.sleep(5)
        pass
    get_test_execution_status()
