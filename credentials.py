#!/usr/bin/env python
import os
 
def get_keystone_creds():
    d = {}
    d['username'] = 'admin'
    d['password'] = 'password'
    d['auth_url'] = 'http://10.214.1.16:5000/v2.0'
    d['tenant_name'] = 'Cloudify'
    return d
 
def get_nova_creds():
    d = {}
    d['username'] = 'admin'
    d['api_key'] = 'password'
    d['auth_url'] = 'http://10.214.1.16:5000/v2.0'
    d['project_id'] = 'Cloudify'
    return d

def get_nova_credentials_v2():
    d = {}
    d['version'] = '2'
    d['username'] = 'admin'
    d['api_key'] = 'password'
    d['auth_url'] = 'http://10.214.1.16:5000/v2.0'
    d['project_id'] = 'Cloudify'
    return d

OS_USERNAME="admin" 
OS_PASSWORD="password" 
OS_TENANT_NAME="Cloudify" 
OS_AUTH_URL="http://localhost:5000/v2.0/" 
CEILOMETER_ENDPOINT="http://localhost:8777"
OS_PROJECT_NAME="Cloudify"
