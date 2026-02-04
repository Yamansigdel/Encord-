import csv
import json
from pathlib import Path
from encord import EncordUserClient
from encord.client import DatasetAccessSettings
from encord.objects import Classification
from schema import PlayEvent, PlayRow
from builders import time_to_frame, parse_list_field

# CONFIG
PROJECT_HASH = "ef2da450-7835-448e-9ec4-0a2193c3412c"
DATASET_HASH = "2d2c79b9-ba29-4246-9a20-6d82d04a50e7"
CSV_PATH = "/home/uswe/Downloads/data-intern-repo/encord/Event Data and Schema/Event Data Listified/pass attempt.csv"

# CLIENT SETUP
user_client = EncordUserClient.create_with_ssh_private_key(
    ssh_private_key_path="/home/uswe/Downloads/data-intern-repo/encord/pipeline/encord-yaman_key-private-key.ed25519"
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


# READ CSV/JSON AND CREATE EVENTS
play_rows = []

with open(CSV_PATH, "r", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        events = []

        # Convert stringified lists to Python lists
        event_types = parse_list_field(row.get("eventType", ""))
        start_times = parse_list_field(row.get("startTime", ""))
        end_times = parse_list_field(row.get("endTime", ""))
        passer=parse_list_field(row.get("passer", ""))
        passDirection=parse_list_field(row.get("passDirection", ""))
        passResult=parse_list_field(row.get("passResult", ""))
        receiver=parse_list_field(row.get("receiver", ""))


        for i in range(len(event_types)):
            events.append(
                PlayEvent(
                    eventType=event_types[i],
                    startTime=start_times[i],
                    endTime=end_times[i],
                    passer=passer[i] if i < len(passer) else None,
                    passDirection=passDirection[i] if i < len(passDirection) else None,
                    passResult=passResult[i] if i < len(passResult) else None,
                    receiver=receiver[i] if i < len(receiver) else None
                )
            )

        play_rows.append(
            PlayRow(
                gameName=row["gameName"],
                fps=row["fps"],
                events=events,
            )
        )

# PROCESS EACH VIDEO ROW
for play_row in play_rows:
    gameName = play_row.gameName
    events_metadata = []

    for event in play_row.events:
        start_frame = time_to_frame(event.startTime, play_row.fps)
        end_frame = time_to_frame(event.endTime, play_row.fps)

        events_metadata.append({
            "eventType": event.eventType,
            "startTime": event.startTime,
            "endTime": event.endTime,
            "startFrame": start_frame,
            "endFrame": end_frame,
            "passer": event.passer,
            "passDirection": event.passDirection,
            "passResult": event.passResult,
            "receiver": event.receiver
        })

    # SAVE CLIENT METADATA TO DATASET ROW
    for data_row in dataset.data_rows:
        if data_row.title == gameName:
            data_row.client_metadata = {
                "events": events_metadata,
            }
            data_row.save()
            break

    # SAVE CLASSIFICATIONS PER EVENT
    for label_row in label_rows:
        if label_row.data_type != "video":
            continue
        if label_row.data_title != gameName:
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
