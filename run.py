import time
from encord import EncordUserClient
from encord.storage import FoldersSortBy
from encord.objects import Classification
from encord.client import DatasetAccessSettings
from helper import time_to_frame, load_json_schema
from encord.objects.attributes import ChecklistAttribute
from encord.orm.dataset import LongPollingStatus, StorageLocation

#CONFIG
BUNDLE_SIZE = 100
INTEGRATION_ID="5631cdf7-34df-4174-9fa2-9d537e186717"
JSON_PATH = "/home/uswe/Downloads/data-intern-repo/encord/pipeline/artifacts/video_info.json"
ONTOLOGY_HASH = "2e2fd297-b593-4af0-b600-f27eaa6e21b5"
SSH_KEY_PATH = "/home/uswe/Downloads/data-intern-repo/encord/pipeline/encord-yaman_key-private-key.ed25519"

#LOAD JSON
videos = load_json_schema(JSON_PATH)

if not videos:
    raise ValueError("No videos found in JSON")

project_title = videos[0].projectTitle
dataset_title = videos[0].datasetTitle

#INITIALIZE CLIENT
user_client = EncordUserClient.create_with_ssh_private_key(
    ssh_private_key_path=SSH_KEY_PATH
)

#CREATE OR FIND STORAGE FOLDER
folders = list(
    user_client.find_storage_folders(
        search=dataset_title,
        dataset_synced=None,
        order=FoldersSortBy.NAME,
        desc=False,
        page_size=100,
    )
)

if folders:
    storage_folder = folders[0]
else:
    storage_folder = user_client.create_storage_folder(
        name=dataset_title,
        description="A folder to store s3 clips",
        client_metadata={"dataset": dataset_title},
    )

#UPLOAD VIDEOS (OBJECT URL)
upload_job_id=storage_folder.add_private_data_to_folder_start(
integration_id=INTEGRATION_ID,
private_files=JSON_PATH,
ignore_errors=True
)

while True:
    result = storage_folder.add_private_data_to_folder_get_result(
        upload_job_id,
        timeout_seconds=5,
    )

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


print(f"All videos Uploaded to folder {storage_folder.name}")

# FIND OR CREATE DATASET
existing = user_client.get_datasets(title_eq=dataset_title)
if existing:
    dataset_hash = existing[0]["dataset"].dataset_hash
    dataset = user_client.get_dataset(dataset_hash)
    print(f"Using existing dataset: {dataset.title} ({dataset_hash})")
else:
    dataset_response = user_client.create_dataset(
        dataset_title=dataset_title,
        dataset_type=StorageLocation.AWS,
        create_backing_folder=False,
    )
    dataset = user_client.get_dataset(dataset_response.dataset_hash)
    print(f"Created new dataset: {dataset.title} ({dataset.dataset_hash})")

# LINK FOLDER ITEMS TO DATASET
items = list(storage_folder.list_items())
item_uuids = [item.uuid for item in items]

if item_uuids:
    dataset.link_items(item_uuids)

dataset.set_access_settings(
    DatasetAccessSettings(fetch_client_metadata=True)
)

# FIND OR CREATE PROJECT
existing_project = list(user_client.list_projects(title_eq=project_title))

if existing_project:
    project = existing_project[0]
    project_hash = project.project_hash
    print(f"Using existing project: {project.title} ({project_hash})")
else:
    project_hash = user_client.create_project(
        project_title=project_title,
        ontology_hash=ONTOLOGY_HASH,
        dataset_hashes=[dataset.dataset_hash],
    )

    project = user_client.get_project(project_hash)
    print(f"Created new project: {project.title} ({project_hash})")

label_rows = project.list_label_rows_v2()

#Create Classification Object for eventType
eventType_cls = project.ontology_structure.get_child_by_title(
    title="eventType",
    type_=Classification,
)

#Get eventType classification attribute
eventType_attr: ChecklistAttribute = eventType_cls.get_child_by_title(title="eventType", type_=ChecklistAttribute)

#Get the option children of that attribute
valid_event_types = {
    opt.title
    for opt in eventType_attr.children
}

#METADATA + CLASSIFICATION
for video in videos:

    matching_label_rows = [
        lr for lr in label_rows
        if lr.data_type == "video" and lr.data_title == video.title
    ]

    if not matching_label_rows:
        print("No label row found for:", video.title)
        continue

    events_metadata = []

    for event in video.events:
        if event.eventType not in valid_event_types:
            raise ValueError(
                f"Invalid eventType '{event.eventType}'. "
                f"Must be one of {valid_event_types}"
            )   

        start_frame = time_to_frame(event.startTime, video.videoMetadata.fps)
        end_frame = time_to_frame(event.endTime, video.videoMetadata.fps)

        events_metadata.append({
            "eventType": event.eventType,
            "startTime": event.startTime,
            "endTime": event.endTime,
            "startFrame": start_frame,
            "endFrame": end_frame,
        })

    #SAVE  VideoMetaData
    for data_row in dataset.data_rows:
        if data_row.title == video.title:
            data_row.client_metadata = {"videoMetadata":{
                "fps": video.videoMetadata.fps,
                "duration": video.videoMetadata.duration,
                "width": video.videoMetadata.width,
                "height": video.videoMetadata.height,
                "file_size": video.videoMetadata.file_size,
                "mime_type": video.videoMetadata.mime_type
                } }
            data_row.save()
            break

    #INITIALISE LABELS
    with project.create_bundle(bundle_size=BUNDLE_SIZE) as bundle:
        for lr in matching_label_rows:
            lr.initialise_labels(
                include_object_feature_hashes=set(),
                include_classification_feature_hashes=set(),
                bundle=bundle,
            )

    #ADD CLASSIFICATIONS
    for lr in matching_label_rows:
        for meta in events_metadata:

            option = eventType_cls.get_child_by_title(
                meta["eventType"]
            )
            if option is None:
                print(f"Warning: ontology option not found: {meta['eventType']}")
                continue

            cls_inst = eventType_cls.create_instance()
            cls_inst.set_answer([option])

            cls_inst.set_for_frames(
                frames=list(range(meta["startFrame"], meta["endFrame"] + 1)),
                manual_annotation=True,
                confidence=1.0,
            )

            lr.add_classification_instance(cls_inst)

    #SAVE LABELS
    with project.create_bundle(bundle_size=BUNDLE_SIZE) as bundle:
        for lr in matching_label_rows:
            lr.save(bundle=bundle)

    print("Ingestion complete for:", video.title)

print("Pipeline Completed Successfully")
