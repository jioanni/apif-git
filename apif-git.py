#!/usr/bin/env python

import subprocess
import yaml
import fileinput
import requests
import sys
import json

#Set your config file route here:

config = "/route/to/your/config/goes/here/config.yml"

#This is the subdirectory that your tests live in amongst the code in your git repository. 

test_subdirectory = "subdir/"


def post_receive(from_commit, to_commit, branch_name):
    print('APIF: Checking for modified')

    p = subprocess.Popen("git rev-parse --symbolic --abbrev-ref " + branch_name, stdout=subprocess.PIPE, shell=True)
    branch_name = p.stdout.read().strip()
    p = subprocess.Popen('git show ' + branch_name +  ' --pretty= --name-status', stdout=subprocess.PIPE, shell=True)
    files = p.stdout.read()
    files = files.strip().split('\n')
    body = {'resources':[]}

    for f in files:
        items = f.split('\t')
        if (items[0] in ['A','M']) and items[1].startswith(test_subdirectory):
            fn = items[1]
            fn = fn[len(test_subdirectory):len(items[1])]
            string_item = ['git show ' +branch_name+':' + '"'+items[1]+'"']
            p = subprocess.Popen(string_item, stdout=subprocess.PIPE, shell=True)
            content = p.stdout.read().strip()
            resource = {'path':fn,'branch':branch_name,'revision':"to_commit",'content':content}
            body['resources'].append(resource)

    print("APIF: Updating "+str(len(body['resources']))+' remote test files')

    if len(body['resources']) > 0:
        chosen_hook = choose_hook(branch_name)
        params = json.dumps(body).encode('utf-8')
        webhook = chosen_hook['hook']
        user_credentials = chosen_hook['creds']
        auth_token = get_token(user_credentials, webhook)
        push_request_executor(webhook, auth_token, params)



def get_token(credentials, hook):
    username = credentials['username']
    password = credentials['password']
    auth_req = requests.get(hook + '/login', auth=(username, password))
    access_token = auth_req.content
    parsed_token = json.loads(access_token.decode("utf-8"))
    if not "access_token" in parsed_token:
        print("Invalid credentials!")
        sys.exit(1)
        return None
    else:
        auth_token = parsed_token['access_token']
        return auth_token



def push_request_executor(webhook, auth_token, payload):
    headers = {}
    if auth_token:
        headers = {'Authorization': 'Bearer ' + auth_token}
    req = requests.post(webhook + '/tests/push', headers=headers, data=payload)
    if req.status_code==200:
        print("APIF: OK")
    else:
        print("APIF: " + str(req.status_code) + " error")

        

def choose_hook(branch):
    with open(config) as stream:
            try:
                config_yaml = (yaml.load(stream))
            except yaml.YAMLError as exc:
                print(exc)
    for hook in config_yaml['hooks']:
        if "branch" in hook and branch == hook['branch']:
            return {"hook": hook['url'], "creds": hook['credentials']}

fc,tc,bn = fileinput.input()[0].split()

post_receive(fc, tc, bn)