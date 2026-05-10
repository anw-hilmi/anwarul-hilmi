import os
import json
import argparse
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. Load credential
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

# 3. Konfigurasi ID
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
                supportsAllDrives=True # PENTING untuk Shared Drive
            ).execute()
            upload_directory(item_path, created_folder["id"])
        else:
            file_meta = {
                'name': item_name,
                'parents': [parent_drive_id]
            }
            media = MediaFileUpload(item_path, resumable=True)
            service.files().create(
                body=file_meta,
                media_body=media,
                fields='id',
                supportsAllDrives=True # PENTING agar tidak kena error kuota
            ).execute()

def main():
    # Ambil Run ID dari argumen agar lebih akurat
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_id", type=str, required=True)
    args = parser.parse_args()
    
    # MLflow dengan SQLite biasanya menyimpan di mlartifacts/0/ atau mlartifacts/1/
    # Kita cek kedua kemungkinan folder tersebut
    found_path = None
    for exp_id in ["0", "1"]:
        temp_path = f"./mlartifacts/{exp_id}/{args.run_id}"
        if os.path.exists(temp_path):
            found_path = temp_path
            break
    
    if found_path:
        print(f"=== Memulai Upload Artifact dari: {found_path} ===")
        run_id_folder_meta = {
            'name': f"Run_{args.run_id}",
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [SHARED_DRIVE_ID]
        }
        root_folder = service.files().create(
            body=run_id_folder_meta,
            fields='id',
            supportsAllDrives=True
        ).execute()
        
        upload_directory(found_path, root_folder["id"])
        print("=== Upload Complete! ===")
    else:
        print(f"Error: Folder artifact untuk Run ID {args.run_id} tidak ditemukan!")

if __name__ == "__main__":
    main()
