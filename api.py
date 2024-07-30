import requests

URL_STUB = 'https://app.americansocceranalysis.com/api/v1/'

def make_api_call(endpoint):
    request_url = '{}{}'.format(URL_STUB, endpoint)
    response = requests.get(request_url)

    if response.status_code == 200:
        print('API Call Successful.')
    else:
        print('There was an error during the API call.')
        print('Response:', response.status_code)
    print('Endpoint:', endpoint)
    print('Request url:', request_url)
    return [response.status_code, response.json()]
