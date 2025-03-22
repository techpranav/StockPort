import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive2.auth import ServiceAccountCredentials
from constants.Constants import *

def authenticate_drive():
    """Authenticate with Google Drive using a service account."""
    scope = ['https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(f'{input_dir}\\Service Account.json', scope)
    gauth = GoogleAuth()
    gauth.credentials = creds
    return GoogleDrive(gauth)


def create_drive_folder(drive, folder_name, parent_folder_id=None):
    """
    Creates a folder in Google Drive.

    :param drive: GoogleDrive instance.
    :param folder_name: Name of the folder to create.
    :param parent_folder_id: (Optional) Parent folder ID to create the folder inside.
    :return: Google Drive Folder ID.
    """
    query = f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"

    folder_list = drive.ListFile({'q': query}).GetList()

    if folder_list:
        print(f"Folder '{folder_name}' already exists.")
        return folder_list[0]['id']  # Return existing folder ID

    folder_metadata = {
        'title': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_folder_id:
        folder_metadata['parents'] = [{'id': parent_folder_id}]

    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    print(f"Created folder: {folder_name} (ID: {folder['id']})")
    return folder['id']


def upload_folder_to_drive(drive, local_folder_path, drive_folder_id):
    """
    Uploads an entire folder to Google Drive.

    :param drive: GoogleDrive instance.
    :param local_folder_path: Path of the folder to upload.
    :param drive_folder_id: Google Drive folder ID where files will be uploaded.
    """
    if not os.path.exists(local_folder_path):
        print(f"Folder '{local_folder_path}' does not exist.")
        return

    for root, _, files in os.walk(local_folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            print(f"Uploading {file_name}...")

            gfile = drive.CreateFile(
                {'title': file_name, 'parents': [{'id': drive_folder_id}]}
            )
            gfile.SetContentFile(file_path)
            gfile.Upload()
            print(f"Uploaded {file_name} to Google Drive.")

def uploadFilesToDrive(local_folder):
    # Example usage
    drive = authenticate_drive()

    # Step 1: Create a new folder in Google Drive
    drive_folder_name = "StockAnalyzer_Financials_V3"
    drive_parent_folder_id = "1RBTpETzZ-xgNH1zop6kUgfrf4nBgOKi2"  # If you want to create inside another folder, put the parent folder ID here.
    drive_folder_id = create_drive_folder(drive, drive_folder_name, drive_parent_folder_id)
    last_folder = os.path.basename(local_folder)

    drive_folder_id = create_drive_folder(drive, last_folder, drive_folder_id)

    # Step 2: Upload files from local folder to Google Drive
    upload_folder_to_drive(drive, local_folder, drive_folder_id)
