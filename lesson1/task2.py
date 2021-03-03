import requests
import json

"""
API key Authentication,
Was mailed when you sign up
"""

API_KEY = '50e46ddc-ad14-4ebc-9dcc-1f1f93a14d55'
HEADERS = {
    'x-api-key': f'{API_KEY}'
}
URL = 'https://api.thecatapi.com/v1/images/search'
PARAMS = {
    'format': 'json',
    'size': 'full'
}

req = requests.get(URL, headers=HEADERS, params=PARAMS)
print(req.text)
if req.ok:
    print(f'Request finished with code {req.status_code}')
    path = 'output2.json'
    with open(path, 'w') as f:
        json.dump(req.json(), f)
    print(f'Response successfully saved to file {path}')
else:
    print(f'`Requset finished with code {req.status_code}')