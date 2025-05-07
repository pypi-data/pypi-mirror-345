import os
from typing import List, Union
import requests
import json
from io import BytesIO
import typing
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from brynq_sdk_brynq import BrynQ

class GoogleDrive(BrynQ):
    def __init__(self, label: Union[str, List], debug: bool = False):
        """
        :param label: label of the Google Drive system in BrynQ
        :param debug: set to True to enable debug logging
        """
        super().__init__()
        api_version = 'v3'
        self.base_url = f'https://www.googleapis.com/drive/{api_version}/'
        credentials = self.get_system_credential(system='google-drive', label=label)
        self.debug = debug
        if self.debug:
            print(f"credentials: {credentials}")
        self.access_token = credentials['auth']['access_token']
        self.brynq_system_id = credentials['id']
        self.timeout = 3600

    def _get_google_drive_headers(self):
        access_token = self.refresh_system_credential(system='google-drive', system_id=self.brynq_system_id)['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        if self.debug:
            print(headers)
        return headers

    def list_files(self, drive_id: str = None):
        """
        Get all files from Google Drive, including shared drives or a specific drive is specified
        :param drive_id: ID of a specific drive (optional)
        """
        url = f'{self.base_url}files'
        headers = self._get_google_drive_headers()
        params = {
            'supportsAllDrives': True,
            'includeItemsFromAllDrives': True,
        }
        if drive_id:
            params['driveId'] = drive_id
            params['corpora'] = 'drive'
        response = requests.get(url=url, headers=headers, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response

    def upload_file(self, local_file_path: str, remote_file_path: str):
        """
        This method performs the actual file upload to the formerly derived site + drive.
        local_file_path: local path of the file you want to upload
        remote_file_path: remote path of the folder and filename where you want to place the file
        """
        credentials = self.refresh_system_credential(system='google-drive', system_id=self.brynq_system_id)
        service = build('drive', 'v3', credentials=credentials)

        file_metadata = {'name': os.path.basename(remote_file_path)}
        media = MediaFileUpload(local_file_path, resumable=True)

        response = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        if self.debug:
            print(f'File ID: {response.get("id")}')

        return response

    def download_file(self, file_id: str, mime_type: str, local_file_path: str):
        """
        This method downloads a file from Google Drive to the local machine.
        file_id: id of the file on Google Drive. Get it with the list_files function
        mime_type: mime type of the file. Get it with the list_files function
        local_file_path: local path where the file will be downloaded to
        """
        url = f'{self.base_url}files/{file_id}/export?mimeType={mime_type}'
        headers = self._get_google_drive_headers()
        response = requests.get(url=url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        with open(local_file_path, 'wb') as f:
            f.write(response.content)
        return response

    def download_files(self, local_folder_path: str, remote_folder_path: str):
        """
        This method downloads all files from a Directory in Google Drive to the local machine.
        local_folder_path: local folder where the files will be downloaded to
        remote_folder_path: remote path of the folder you want to get on Google Drive
        """
        credentials = self.refresh_system_credential(system='google-drive', system_id=self.brynq_system_id)
        service = build('drive', 'v3', credentials=credentials)

        # List files in the specified remote folder
        query = f"'{remote_folder_path}' in parents"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            return 'No files found.'
        else:
            for item in items:
                file_id = item['id']
                file_name = item['name']
                request = service.files().get_media(fileId=file_id)
                fh = BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    if self.debug:
                        print(f"Download {file_name} {int(status.progress() * 100)}%.")

                # Save the file to the local folder
                local_file_path = os.path.join(local_folder_path, file_name)
                with open(local_file_path, 'wb') as f:
                    f.write(fh.getvalue())

        return "Download complete"

    def remove_file(self, remote_file_path: str):
        """
        Remove a file from Google Drive
        remote_file_path: complete path including filename
        :return: response from Google Drive
        """
        credentials = self.refresh_system_credential(system='google-drive', system_id=self.brynq_system_id)
        service = build('drive', 'v3', credentials=credentials)

        # Find the file ID
        query = f"name = '{remote_file_path}'"
        results = service.files().list(q=query, fields="files(id)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return "No files found."
        else:
            file_id = items[0]['id']
            response = service.files().delete(fileId=file_id).execute()
            if self.debug:
                print(f'File {remote_file_path} deleted.')
            return response

    def remove_folder(self, folder_id: str):
        """
        Remove a folder from Google Drive
        folder: folder id that you want to delete
        """
        credentials = self.refresh_system_credential(system='google-drive', system_id=self.brynq_system_id)
        service = build('drive', 'v3', credentials=credentials)

        response = service.files().delete(fileId=folder_id).execute()
        if self.debug:
            print(f'Folder {folder_id} deleted.')
        return response