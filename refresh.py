import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()
rtoken = os.getenv('RTOKEN')
base64 = os.getenv('BASE64')

class Refresh:

    def __init__(self):
        self.refresh_token = rtoken
        self.base_64 = base64

    def refresh(self):

        query = "https://accounts.spotify.com/api/token"

        response = requests.post(query,
                                 data={"grant_type": "refresh_token",
                                       "refresh_token": rtoken},
                                 headers={"Authorization": "Basic " + base64})

        response_json = response.json()
        print(response_json)

        return response_json["access_token"]

a = Refresh()
a.refresh()
