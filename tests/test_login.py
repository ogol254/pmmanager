import json
import requests

def test_login():
    url = 'http://localhost:5000/auth/login'
    payload = {
        'email': 'superadmin@example.com',
        'password': 'secret123'
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print('Status Code:', response.status_code)
    print('Response:', response.json())

if __name__ == '__main__':
    test_login()
