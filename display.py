#for printing metadata of data rows
from encord import EncordUserClient
from encord.client import DatasetAccessSettings

user_client = EncordUserClient.create_with_ssh_private_key(
    ssh_private_key_path="/home/uswe/Downloads/data-intern-repo/encord/encord-yaman_key-private-key.ed25519"
)
dataset = user_client.get_dataset("c11fda6e-40cd-4e6d-9eeb-d327bf3d7b30")
dataset.set_access_settings(
    DatasetAccessSettings(fetch_client_metadata=True)
)

for data_unit, data_row in enumerate(dataset.data_rows):
    print(f"{data_row.client_metadata} - Data Unit: {data_unit}")