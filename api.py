import requests
import os
from dotenv import load_dotenv

def make_asa_api_call(endpoint):
    # Documentation: https://app.americansocceranalysis.com/api/v1/__docs__/#/
    url_stub = 'https://app.americansocceranalysis.com/api/v1/'
    request_url = '{}{}'.format(url_stub, endpoint)
    response = requests.get(request_url)

    if response.status_code == 200:
        print('API Call Successful.')
    else:
        print('There was an error during the API call.')
        print('Response:', response.status_code)
    print('Endpoint:', endpoint)
    print('Request url:', request_url)
    return [response.status_code, response.json()]
