#for printing metadata of data rows
from encord import EncordUserClient
from encord.client import DatasetAccessSettings

DatasetHASH="29ecc840-4873-49a6-a5be-6f70f590d550"

user_client = EncordUserClient.create_with_ssh_private_key(
    ssh_private_key_path="/home/uswe/Downloads/data-intern-repo/encord/pipeline/encord-yaman_key-private-key.ed25519"
)
dataset = user_client.get_dataset(DatasetHASH)
dataset.set_access_settings(
    DatasetAccessSettings(fetch_client_metadata=True)
)

for data_unit, data_row in enumerate(dataset.data_rows):
    print(f"{data_row.client_metadata} - Data Unit: {data_unit}")