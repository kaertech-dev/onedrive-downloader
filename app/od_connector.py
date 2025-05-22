import requests
import threading
import os
import pycurl
from sys import stderr as STREAM
import auth_callback

class OneDriveConnector:

    MSGRAPH_SCOPE = "User.Read offline_access"
    MSGRAPH_ME = "https://graph.microsoft.com/v1.0/me"
    KB = 1024

    def __init__(self, client, tenant, secret, tokens) -> None:
        self.auth_endpoint = f"https://login.microsoftonline.com/{tenant}/oauth2/authorize"
        self.token_endpoint = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
        self.client = client
        self.access_token = tokens.get('access_token')
        self.refresh_token = tokens.get('refresh_token')
        self.secret = secret

    def check_tokens(self):
        return self.access_token and self.refresh_token

    def check_access_token(self):
        response = requests.get(self.MSGRAPH_ME, headers={"Authorization": f"Bearer {self.access_token}"})
        return True if response.status_code == 200 else False

    def get_tokens(self) -> dict:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token
        }

    def update_access_token(self):
        data = {
            "client_id": self.client,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
            "scope": self.MSGRAPH_SCOPE,
            "client_secret": self.secret
        }
        response = requests.post(self.token_endpoint, data=data).json()
        self.access_token = response.get('access_token')


    # callback function for c.XFERINFOFUNCTION
    def __curl_status(self, download_t, download_d, upload_t, upload_d):
        STREAM.write('Downloading: {}/{} kiB ({}%)\r'.format(
            str(int(download_d/self.KB)),
            str(int(download_t/self.KB)),
            str(int(download_d/download_t*100) if download_t > 0 else 0)
        ))
        STREAM.flush()

    def __download(self, url, file_path):
        with open(file_path, "wb") as f:
            curl = pycurl.Curl()
            # curl.setopt(pycurl.CAINFO, '/etc/ssl/certs/ca-certificates.crt')
            curl.setopt(pycurl.XOAUTH2_BEARER, self.access_token)
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEDATA, f)
            curl.setopt(pycurl.NOPROGRESS, False)
            curl.setopt(pycurl.XFERINFOFUNCTION, self.__curl_status)
            curl.perform()
            curl.close()

    def download_items(self, items, output_dir):
        for i in items:
            response = requests.get(i, headers={"Authorization": f"Bearer {self.access_token}"}).json()
            url = response["@microsoft.graph.downloadUrl"]
            print(f"Downloading of {i.split('/')[-1]} from {url}")
            fpath = os.path.join(output_dir, i.split('/')[-1])
            self.__download(url, fpath)

    def __request_authorization_code(self):
        data = {
            "client_id": self.client,
            "response_type": "code",
            "redirect_uri": auth_callback.get_auth_callback_url(),
            "scope": self.MSGRAPH_SCOPE,
            "state": "good"
        }
        auth_url = self.auth_endpoint + "?"
        for key in data.keys():
            auth_url += f"&{key}={data[key]}"
        # Follow the link to sign in and get auth code
        print(auth_url)
        # Start web-server to get authorization code
        flask_thread = threading.Thread(target=auth_callback.auth_callback_task)
        flask_thread.start()
        # Wait for the auth code to be redirected
        return auth_callback.auth_callback_event.wait(timeout=60)

    def get_new_tokens(self):
        if not self.__request_authorization_code():
            print("Authorization code timeout")

        data = {
            "client_id": self.client,
            "response_type": "token",
            "scope": self.MSGRAPH_SCOPE,
            "grant_type": "authorization_code",
            "redirect_uri": auth_callback.get_auth_callback_url(),
            "client_secret": self.secret,
            "code": auth_callback.web_app_auth_data.get('code')
        }
        response = requests.post(self.token_endpoint, data=data).json()
        self.access_token = response.get('access_token')
        self.refresh_token = response.get('refresh_token')
