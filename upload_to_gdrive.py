import os
import json
import argparse
import shutil
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. Setup Argparse
parser = argparse.ArgumentParser()
parser.add_argument("--run_id", type=str, required=True)
args = parser.parse_args()

# 2. Load Credentials
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

# 3. Fungsi Upload File Tunggal
def upload_file(file_path, name, parent_id):
    file_meta = {'name': name, 'parents': [parent_id]}
    media = MediaFileUpload(file_path, resumable=True)
    return service.files().create(
        body=file_meta, 
        media_body=media, 
        fields='id',
        supportsAllDrives=True
    ).execute()

# 4. Pencarian Path & Eksekusi ZIP
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
    zip_name = f"{args.run_id}.zip"
    # Membuat file ZIP dari folder source
    shutil.make_archive(args.run_id, 'zip', found_source)
    
    print(f"=== Uploading ZIP: {zip_name} to Drive ===")
    try:
        upload_file(zip_name, zip_name, SHARED_DRIVE_ID)
        print("=== Upload Sukses! ===")
    except Exception as e:
        print(f"Gagal upload: {e}")
else:
    print(f"Source tidak ditemukan. Struktur folder:")
    os.system("ls -R")

print("=== Selesai ===")
