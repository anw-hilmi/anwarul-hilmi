import os
import json
import argparse
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

# 4. Pencarian Path & Eksekusi Upload Model Langsung
potential_sources = [
    f"./mlruns/1/{args.run_id}/artifacts/model/data/model.keras",
    f"./mlruns/0/{args.run_id}/artifacts/model/data/model.keras",
    f"./mlartifacts/0/{args.run_id}/artifacts/model/data/model.keras"
]

found_file = None
for ps in potential_sources:
    if os.path.exists(ps):
        found_file = ps
        break

if found_file:
    # Nama file di Drive akan tetap model.keras agar sesuai dengan app.py
    file_display_name = "model.keras"
    
    print(f"=== Uploading File: {found_file} to Drive ===")
    try:
        response = upload_file(found_file, file_display_name, SHARED_DRIVE_ID)
        print(f"=== Upload Sukses! File ID: {response.get('id')} ===")
    except Exception as e:
        print(f"Gagal upload: {e}")
else:
    print(f"File model.keras tidak ditemukan di path artifacts. Struktur folder:")
    os.system("ls -R")

print("=== Selesai ===")