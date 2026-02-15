import json
import time
from encord import EncordUserClient
from encord.orm.dataset import LongPollingStatus

# CONFIG
SSH_KEY_PATH = "/home/uswe/Downloads/data-intern-repo/encord/pipeline/encord-yaman_key-private-key.ed25519"
DATASET_UID = "c11fda6e-40cd-4e6d-9eeb-d327bf3d7b30"
JSON_FILE_PATH = "/home/uswe/Downloads/data-intern-repo/encord/pipeline/artifacts/video_info.json"

# 1. Authenticate
print("Authenticating...")
user_client = EncordUserClient.create_with_ssh_private_key(
    ssh_private_key_path=SSH_KEY_PATH
)

# 2. Get Dataset
print("Fetching dataset...")
dataset = user_client.get_dataset(DATASET_UID)

# 3. Load JSON Spec
print("Loading JSON registration file...")
with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
    registration_spec = json.load(f)

print(f"Found {len(registration_spec.get('videos', []))} videos to register.")

# 4. Start Registration
print("Starting registration job...")
integration_id="123456789"

#To upload private cloud data into encord file storage
folder_name = "folder1"
folder_description = "A folder to store cloud data"
folder_metadata = {"my": "folder_metadata"}
storage_folder = user_client.create_storage_folder(folder_name, folder_description,client_metadata=folder_metadata)

upload_job_id=storage_folder.add_private_data_to_folder_start(
    integration_id=integration_id,
    private_files=registration_spec,
    ignore_errors=True

)

#To upload private cloud data directly to dataset
upload_job_id = dataset.add_private_data_to_dataset(
    integration_id=integration_id,
    data=registration_spec,
    ignore_errors=True
)

print(f"Upload Job ID: {upload_job_id}")

# 5. Poll Status
print("Checking upload status...")

while True:
    result = dataset.add_private_data_to_dataset_get_result(upload_job_id)

    if result.status == LongPollingStatus.PENDING:
        print("Still processing...")
        time.sleep(5)
        continue

    elif result.status == LongPollingStatus.DONE:
        print("Upload completed!")

        if result.unit_errors:
            print("\nSome files failed:")
            for err in result.unit_errors:
                print(err.object_urls)
        break

    else:
        print(f"Upload failed: {result.errors}")
        break
