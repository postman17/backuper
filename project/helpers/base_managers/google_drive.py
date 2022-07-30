"""
http://datalytics.ru/all/rabotaem-s-api-google-drive-s-pomoschyu-python/
https://github.com/googleapis/google-api-python-client/tree/main/docs
https://qna.habr.com/q/720509

HOW CREATE OAUTH APP
Instruction - https://developers.google.com/identity/protocols/oauth2/
Open in browser https://console.developers.google.com/
Press enable app
Select Google Drive API and Press enable
In page Drive API press create credentials
Select user data and press next
Fill app fields, add auth/drive scope
Select client as web application
Fill redirect uri http://localhost/backup/oauth-code/
Add self account email to users
Download config file and fill config field by file data
Public oauth app

For reset access by oauth app, remove here https://myaccount.google.com/u/0/permissions
and auth again
"""
import logging

from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from helpers.base_managers.base import BaseManager


base_manager_logger = logging.getLogger(__name__)


class GoogleDriveBaseManager(BaseManager):
    """Google Drive base manager."""

    # Scope for create, edit, delete files in google drive
    SCOPE = "https://www.googleapis.com/auth/drive"

    def get_oauth_code_url(self, client_id: str, state: str, redirect_url: str) -> str:
        base_manager_logger.info(f"Google drive base manager: get oauth code url started")

        url = f"""https://accounts.google.com/o/oauth2/auth?scope={self.SCOPE}
        &redirect_uri={redirect_url}&response_type=code&client_id={client_id}&state={state}"""

        base_manager_logger.info(f"Google drive base manager: get oauth code url finished - {url}")
        return url

    def get_tokens(self, config: dict, code: str) -> dict:
        """Google doesnt return refresh token((. """
        base_manager_logger.info(f"Google drive base manager: get tokens started")

        flow = Flow.from_client_config(
            {"web": config},
            scopes=[self.SCOPE],
            redirect_uri=config.get("redirect_url"),
        )
        tokens = flow.fetch_token(code=code)

        base_manager_logger.info("Google drive base manager: get tokens finished")
        return tokens

    def upload_file(self, access_token: str, source_path: str, target_path: str, **kwargs) -> bool:
        logger = kwargs.get("logger", base_manager_logger)
        logger.info("Google drive base manager: upload file started")

        credentials = Credentials(access_token)
        service = build('drive', 'v3', credentials=credentials)

        parent_folder_name = target_path.split("/")[0]
        folder_id = self.get_target_folder_id(access_token, parent_folder_name, logger=logger)
        name = source_path.split("/")[-1]
        file_metadata = {
                        'name': name,
                        'parents': [folder_id]
                    }
        media = MediaFileUpload(source_path, resumable=True)

        response = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        logger.info(f"Google drive base manager: upload file finished - {response}")
        return True

    def create_folder(self, access_token: str, folder_name: str, **kwargs) -> str:
        logger = kwargs.get("logger", base_manager_logger)
        logger.info("Google drive base manager: create folder started")

        credentials = Credentials(access_token)
        service = build('drive', 'v3', credentials=credentials)
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': []
        }
        response = service.files().create(
            body=file_metadata, fields='id'
        ).execute()

        logger.info(f"Google drive base manager: create folder finished - {response}")
        return response["id"]

    def get_target_folder_id(
            self, access_token: str, folder_name: str, need_create_folder=True, **kwargs
    ) -> str:
        logger = kwargs.get("logger", base_manager_logger)
        logger.info("Google drive base manager: get target folder id started")

        credentials = Credentials(access_token)
        service = build('drive', 'v3', credentials=credentials)
        results = service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields='nextPageToken, files(id, name)',
            spaces='drive',
        ).execute()

        for folder in results.get("files", []):
            if folder.get("name", "") == folder_name:
                logger.info("Google drive base manager: get target folder id finished, folder found")
                return folder["id"]

        logger.info("Google drive base manager: get target folder id finished, folder not found")
        if need_create_folder:
            return self.create_folder(access_token, folder_name, logger=logger)

        return ""

    def check_access_token(self, access_token: str, **kwargs) -> bool:
        try:
            self.get_target_folder_id(access_token, "asdfghjkl", need_create_folder=False)
        except Exception as exc:
            return False

        return True

    def refresh_token(self, config, **kwargs) -> dict:  # TODO: check if my app approve
        logger = kwargs.get("logger", base_manager_logger)
        logger.info(f"Google drive base manager: refresh token started")

        flow = Flow.from_client_config(
            {"web": config},
            scopes=[self.SCOPE],
            redirect_uri=config.get("redirect_url"),
        )
        tokens = flow.oauth2session.refresh_token(
            flow.client_config['token_uri'],
            refresh_token=flow.client_config["refresh_token"],
            client_id=flow.client_config["client_id"],
            client_secret=flow.client_config['client_secret']
        )

        logger.info("Google drive base manager: refresh token finished")
        return tokens

    def get_file_id(
            self, access_token: str, file_name: str, **kwargs
    ) -> str:
        logger = kwargs.get("logger", base_manager_logger)
        logger.info("Google drive base manager: get target file id started")

        credentials = Credentials(access_token)
        service = build('drive', 'v3', credentials=credentials)
        results = service.files().list(
            fields="nextPageToken, files(id, name, mimeType, size, parents, modifiedTime)"
        ).execute()

        for folder in results.get("files", []):
            if folder.get("name", "") == file_name:
                logger.info("Google drive base manager: get target file id finished, file found")
                return folder["id"]

        logger.info("Google drive base manager: get target file id finished, file not found")

        return ""

    def delete_file(self, access_token: str, target_path: str, **kwargs):
        logger = kwargs.get("logger", base_manager_logger)
        logger.info(f"Google drive base manager: delete file started, filename - {target_path}")

        file_name = target_path.split("/")[-1]
        file_id = self.get_file_id(access_token, file_name)

        try:
            credentials = Credentials(access_token)
            service = build('drive', 'v3', credentials=credentials)
            service.files().delete(file_id=file_id).execute()
        except Exception:
            logger.error("Google drive base manager: delete file error", exc_info=True)

            return False

        logger.info("Google drive base manager: delete file finished")
        return True

