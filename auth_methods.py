import base64
import requests
import json
from enum import Enum


def extract_basic_header(df):
    print("Extracting basic auth credentials from digital footprint object...")
    auth_header = "Basic " + base64.b64encode((df.auth_data['username'] + ":" + df.auth_data['password']).encode("utf-8"))\
        .decode("utf-8")
    return auth_header


def extract_oauth_header(df):
    print("Performing client credentials grant type flow for getting access token...")
    response = requests.post(df.auth_data.link,
                             data=get_oauth_body(df),
                             headers={"Content-type": "application/x-www-form-urlencoded"})
    response_body = json.loads(response.text)
    if 'access_token' not in response_body:
        raise 'Could not get access token'
    return "Bearer " + response_body['access_token']

def get_oauth_body(df):
    result = "grant_type=client_credentials"
    if 'client_id' in df.auth_data:
        result = result + "&client_id=" + df.auth_data['client_id']
    if 'client_secret' in df.auth_data:
        result = result + "&client_secret=" + df.auth_data['client_secret']
    if 'scope' in df.auth_data:
        result = result + "&scope=" + df.auth_data['scope']
    return result

def extract_token_header(df):
    print("Extracting token from digital footprint object...")
    return df.auth_data['token_type'] + " " + df.auth_data['token']

class AuthMethods(Enum):
    BASIC = {
        "name": "BASIC",
        "extract_auth_header": extract_basic_header
    }
    OAUTH = {
        "name": "OAUTH",
        "extract_auth_header": extract_oauth_header
    }
    TOKEN = {
        "name": "TOKEN",
        "extract_auth_header": extract_token_header
    }

    @staticmethod
    def from_str(method):
        if method.upper() == AuthMethods.BASIC.name:
            return AuthMethods.BASIC
        elif method.upper() == AuthMethods.OAUTH.name:
            return AuthMethods.OAUTH
        elif method.upper() == AuthMethods.TOKEN.name:
            return AuthMethods.TOKEN
        else:
            raise f"Authentication or authorization method '{method}' is unknown."
