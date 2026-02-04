import csv
import json
from pathlib import Path
from encord import EncordUserClient
from encord.client import DatasetAccessSettings
from encord.objects import Classification
from schema import PlayEvent
from builders import time_to_frame, clean_field, parse_list_field

# CONFIG
PROJECT_HASH = "4cf4e3a8-d509-498d-8510-bffc79aa3a17"
DATASET_HASH = "c11fda6e-40cd-4e6d-9eeb-d327bf3d7b30"
FPS = 59.94
CSV_PATH = "/home/uswe/Downloads/data-intern-repo/homework/Event Data Listified/punt attempt.csv"
VIDEO_TITLE = "training-films-highschool-PLAYON-VerificationVideos-2024-Blue-Cross-Bowl-Football-Championship-_-TSSAA-Div-II-Class-AAA-Baylor-vs-McCallie-KeyPoints-Frames_11.mp4"

# CLIENT SETUP
user_client = EncordUserClient.create_with_ssh_private_key(
    ssh_private_key_path="/home/uswe/Downloads/data-intern-repo/encord/encord-yaman_key-private-key.ed25519"
)
dataset = user_client.get_dataset(DATASET_HASH)
dataset.set_access_settings(DatasetAccessSettings(fetch_client_metadata=True))

project = user_client.get_project(PROJECT_HASH)
label_rows = project.list_label_rows_v2()

# FUNCTION TO GET CLASSIFICATION OBJECT
def create_classification_obj(title: str, type_) -> Classification:
    return project.ontology_structure.get_child_by_title(title=title, type_=type_)

# CREATE CLASSIFICATION OBJECTS
eventType_cls = create_classification_obj("eventType", Classification)
# start_time_cls = create_classification_obj("startTime", Classification)
# end_time_cls = create_classification_obj("endTime", Classification)

# READ CSV AND CREATE EVENTS
play_rows = []

with open(CSV_PATH, "r", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        events = []

        # Convert stringified lists to Python lists
        event_types = parse_list_field(row.get("eventType", ""))
        start_times = parse_list_field(row.get("startTime", ""))
        end_times = parse_list_field(row.get("endTime", ""))
        punt_results = parse_list_field(row.get("puntResult", ""))
        punt_directions = parse_list_field(row.get("puntDirection", ""))


        for i in range(len(event_types)):
            events.append(
                PlayEvent(
                    eventType=event_types[i],
                    startTime=start_times[i],
                    endTime=end_times[i],
                    puntResult=punt_results[i] if i < len(punt_results) else None,
                    puntDirection=punt_directions[i] if i < len(punt_directions) else None
                )
            )

        play_rows.append({
            "videoTitle": VIDEO_TITLE,
            "events": events
        })

# PROCESS EACH VIDEO ROW
for play_row in play_rows:
    video_title = play_row["videoTitle"]
    events_metadata = []

    for event in play_row["events"]:
        start_frame = time_to_frame(event.startTime, FPS)
        end_frame = time_to_frame(event.endTime, FPS)

        events_metadata.append({
            "eventType": event.eventType,
            "startTime": event.startTime,
            "endTime": event.endTime,
            "startFrame": start_frame,
            "endFrame": end_frame,
            "puntResult": event.puntResult,
            "puntDirection": event.puntDirection
        })

    # SAVE CLIENT METADATA TO DATASET ROW
    for data_row in dataset.data_rows:
        if data_row.title == video_title:
            data_row.client_metadata = {
                "events": events_metadata,
                "source": "DataOps",
                "fps": FPS
            }
            data_row.save()
            break

    # SAVE CLASSIFICATIONS PER EVENT
    for label_row in label_rows:
        if label_row.data_type != "video":
            continue
        if label_row.data_title != video_title:
            continue

        labels = label_row.initialise_labels()

        for meta in events_metadata:
            option = eventType_cls.get_child_by_title(meta["eventType"])
            inst = eventType_cls.create_instance()
            inst.set_answer(option)
            inst.set_for_frames(
                frames=list(range(meta["startFrame"], meta["endFrame"] + 1)),
                manual_annotation=True,
                confidence=1.0
            )
            label_row.add_classification_instance(inst)

        label_row.save()

print("Frame-level classifications and client metadata completed")
