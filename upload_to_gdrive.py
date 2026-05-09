import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. Load credential dari Environment Variable (GitHub Secrets)
gdrive_creds_json = os.getenv('GDRIVE_CREDENTIALS')
if not gdrive_creds_json:
    raise ValueError("GDRIVE_CREDENTIALS secret is not set!")

creds_dict = json.loads(gdrive_creds_json)
credentials = Credentials.from_service_account_info(
    creds_dict,
    scopes=["https://www.googleapis.com/auth/drive"]
)

# 2. Build Drive API
service = build('drive', 'v3', credentials=credentials)

# 3. Ambil Folder ID dari Environment Variable
SHARED_DRIVE_ID = os.getenv("GDRIVE_FOLDER_ID")

def upload_directory(local_dir_path, parent_drive_id):
    for item_name in os.listdir(local_dir_path):
        item_path = os.path.join(local_dir_path, item_name)
        if os.path.isdir(item_path):
            folder_meta = {
                'name': item_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_drive_id]
            }
            created_folder = service.files().create(
                body=folder_meta,
                fields='id',
                supportsAllDrives=True
            ).execute()
            new_folder_id = created_folder["id"]
            print(f"Created folder: {item_name}")
            upload_directory(item_path, new_folder_id)
        else:
            print(f"Uploading file: {item_name}")
            file_meta = {
                'name': item_name,
                'parents': [parent_drive_id]
            }
            media = MediaFileUpload(item_path, resumable=True)
            service.files().create(
                body=file_meta,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()

# 4. Jalankan Upload
local_mlruns_0 = "./mlruns/0"

if os.path.exists(local_mlruns_0):
    for run_id in os.listdir(local_mlruns_0):
        run_id_local_path = os.path.join(local_mlruns_0, run_id)
        if os.path.isdir(run_id_local_path):
            run_id_folder_meta = {
                'name': run_id,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [SHARED_DRIVE_ID]
            }
            run_id_folder = service.files().create(
                body=run_id_folder_meta,
                fields='id',
                supportsAllDrives=True
            ).execute()
            print(f"=== Uploading run_id: {run_id} ===")
            upload_directory(run_id_local_path, run_id_folder["id"])
else:
    print(f"Directory {local_mlruns_0} not found. No files to upload.")

print("=== Upload Complete! ===")