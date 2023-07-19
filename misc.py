import json
import os

import requests
from dateutil import tz


def utc_to_local(dt,
                 tz_from='UTC',
                 tz_to='UTC+3'):
    tz_from = tz.gettz(tz_from)
    tz_to = tz.gettz(tz_to)
    utc_dt = dt.replace(tzinfo=tz_from)
    local_dt = utc_dt.astimezone(tz_to)
    return local_dt


def get_auth_token(cfg):
    # TODO: it's thread-unsafe
    headers = {'Content-Type': 'application/json'}
    data = {
        "username": os.environ.get('API_USERNAME'),
        "password": os.environ.get('API_PASSWORD')
    }
    endpoint = f'{cfg["be_protocol"]}://{cfg["be_server"]}:{cfg["be_port"]}/api/v1/token/'
    response = requests.post(endpoint, headers=headers, data=json.dumps(data))
    print(f'auth: response {response.status_code}')
    token = f'Bearer {response.json()["access"]}'
    return token
