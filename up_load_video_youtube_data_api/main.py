import json
import os
import httplib2

from random import randrange
from time import sleep
from tokens import config
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build



APP_TOKEN_FILE = config.APP_TOKEN_FILE # f'../{config.APP_TOKEN_FILE}'
USER_TOKEN_FILE = config.USER_TOKEN_FILE # f'../{config.USER_TOKEN_FILE}'
API_KEY = config.API_KEY

#exception which will except
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/userinfo.profile'
    #'https://www.googleapis.com/auth/youtube.upload'
]


def get_creds_cons():
    flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES)
    return flow.run_console()


def get_creds_saved():
    # https://developers.google.com/docs/api/quickstart/python
    creds = None

    if os.path.exists(USER_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)
        creds.refresh(Request())

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES)
        creds = flow.run_local_server(port=0)

    with open(USER_TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())

    return creds


def get_services(service, version):
    creds = get_creds_saved()
    #creds = get_creds_cons()
    serveces = build(service, version, credentials=creds)
    return serveces


def video_upload(video_path, title, desc, **kwargs):
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)# определяем в объект видео для youtube
    meta = {
        'snippet': {
            'title': title,
            'description': desc,
        },
        # All videos uploaded via the videos.insert endpoint from unverified API projects created after 28 July 2020
        # will be restricted to private viewing mode. To lift this restriction,
        # each API project must undergo an audit to verify compliance
        # --- т.е. для прилки в статусе теста тут всегда приват, иначе видос будет заблокирован
        'status': {
            'privacyStatus': kwargs.get("privacy", "private")# if write public, youtube will issue a blocked video
        }
    }
    insert_request = get_services("youtube", "v3").videos().insert(
        part=','.join(meta.keys()),
        body=meta,
        media_body=media
    )

    r = resumable_upload(insert_request)
    #print(r)


class Video_upload:
    def __init__(self, path, title, desc):
        self.path = path
        self.title = title
        self.desc = desc

    def video_upload(self):
        video_upload(self.path, self.title, self.desc)


def resumable_upload(request, retries=5):
    while retries > 0:
        try:
            print('[up loading]')
            print('Please wait ...')
            status, response = request.next_chunk()
            if response is None: continue # next chunk, will be None until the resumable media is fully uploaded
            if 'id' not in response: raise Exception("no id found while video uploading")

            print('[[[[[[[[[OK! GOOD!!]]]]]]]]]' + '\n' + '='*20)
            return response # success
        except Exception as e:
            #print(e)
            retries -= 1
            sleep(randrange(5))

if __name__=='__main__':
    print(get_creds_cons())