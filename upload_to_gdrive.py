import os
import json
import argparse
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Setup Argparse
parser = argparse.ArgumentParser()
parser.add_argument("--run_id", type=str, required=True)
args = parser.parse_args()

# Load Credentials
gdrive_creds_json = os.getenv('GDRIVE_CREDENTIALS')
if not gdrive_creds_json:
    raise ValueError("GDRIVE_CREDENTIALS secret is not set!")

creds_dict = json.loads(gdrive_creds_json)
credentials = Credentials.from_service_account_info(
    creds_dict,
    scopes=["https://www.googleapis.com/auth/drive"]
)

service = build('drive', 'v3', credentials=credentials)
SHARED_DRIVE_ID = os.getenv("GDRIVE_FOLDER_ID")

def upload_directory(local_dir_path, parent_drive_id):
    if not os.path.exists(local_dir_path): return
    for item_name in os.listdir(local_dir_path):
        item_path = os.path.join(local_dir_path, item_name)
        if os.path.isdir(item_path):
            folder_meta = {
                'name': item_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_drive_id]
            }
            # Tambahkan supportsAllDrives=True
            created_folder = service.files().create(
                body=folder_meta, 
                fields='id', 
                supportsAllDrives=True
            ).execute()
            upload_directory(item_path, created_folder["id"])
        else:
            print(f"Uploading: {item_name}")
            file_meta = {
                'name': item_name, 
                'parents': [parent_drive_id]
            }
            media = MediaFileUpload(item_path, resumable=True)
            # CRITICAL: Gunakan fields='id' agar upload masuk ke folder tujuan, bukan kuota Service Account
            service.files().create(
                body=file_meta, 
                media_body=media, 
                fields='id',
                supportsAllDrives=True
            ).execute()

# Pencarian Path
potential_sources = [
    f"./mlruns/1/{args.run_id}",
    f"./mlruns/0/{args.run_id}",
    f"./mlartifacts/0/{args.run_id}"
]

found_source = None
for ps in potential_sources:
    if os.path.exists(ps):
        found_source = ps
        break

if found_source:
    print(f"=== Uploading from: {found_source} ===")
    run_id_folder_meta = {
        'name': args.run_id,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [SHARED_DRIVE_ID]
    }
    run_id_folder = service.files().create(
        body=run_id_folder_meta, 
        fields='id', 
        supportsAllDrives=True
    ).execute()
    upload_directory(found_source, run_id_folder["id"])
else:
    print(f"Directory not found. Current structure:")
    os.system("ls -R")

print("=== Upload Complete! ===")
