import requests
import json

HEADERS = {
    'Accept': 'application/vnd.github.v3+json'
}
USERNAME = 'matveykortsev'
URL = f'https://api.github.com/users/{USERNAME}/repos'

req = requests.get(URL, headers=HEADERS)

if req.ok:
    print(f'Request finished with code {req.status_code}')
    path = 'output.json'
    with open(path, 'w') as f:
        json.dump(req.json(), f)
    print(f'Response successfully saved to file {path}')
else:
    print(f'`Requset finished with code {req.status_code}')


