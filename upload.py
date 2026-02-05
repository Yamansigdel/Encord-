#upload videos to a new_folder/existing_folder in encord

from encord import EncordUserClient
from encord.storage import FoldersSortBy
import os

# Instantiate Encord client by substituting the path to your private key
user_client = EncordUserClient.create_with_ssh_private_key(ssh_private_key_path="/home/uswe/Downloads/data-intern-repo/encord/pipeline/encord-yaman_key-private-key.ed25519")

# Upload videos to the folder. Substitute file path
input_folder="/home/uswe/Downloads/data-intern-repo/encord/pipeline/passingAttempt_videos"
game_files = os.listdir(input_folder)

# Create a new storage folder
# folder_name = "test_upload_folder"
# folder_description = "A folder to try uploading videos"
# folder_metadata = {"my": "folder_metadata"}
# storage_folder = user_client.create_storage_folder(folder_name, folder_description,client_metadata=folder_metadata)

# Find the existing storage folder by name
folder_name = "passingAttempt"  # Replace with your folder's name
folders = list(user_client.find_storage_folders(search=folder_name, dataset_synced=None, order=FoldersSortBy.NAME, desc=False, page_size=1000))


if folders:
    storage_folder = folders[0]

    for game_file in game_files:
        file_path = os.path.join(input_folder, game_file)
        # client_metadata = {"client": "metadata"}
        video_uuid = storage_folder.upload_video(file_path, None)
        print(f"Uploaded {game_file} with UUID: {video_uuid}")
else:
    print("folder not found")