import csv
from encord import EncordUserClient
from encord.client import DatasetAccessSettings
from encord.objects import Classification
from schema import PlayEvent, PlayRow
from builders import time_to_frame, parse_list_field

# CONFIG
PROJECT_HASH = "bcdef3a1-157a-4bac-813d-160d1726bd6a"
DATASET_HASH = "29ecc840-4873-49a6-a5be-6f70f590d550"
CSV_PATH = "/home/uswe/Downloads/data-intern-repo/encord/pipeline/artifacts/pass attempt .csv"
user_client = EncordUserClient.create_with_ssh_private_key(
    ssh_private_key_path="/home/uswe/Downloads/data-intern-repo/encord/pipeline/encord-yaman_key-private-key.ed25519"
)

# CLIENT SETUP
dataset = user_client.get_dataset(DATASET_HASH)
dataset.set_access_settings(DatasetAccessSettings(fetch_client_metadata=True))

project = user_client.get_project(PROJECT_HASH)
label_rows = project.list_label_rows_v2()

# ONTOLOGY HELPER
def get_ontology_obj(title: str, type_):
    return project.ontology_structure.get_child_by_title(title=title, type_=type_)

eventType_cls = get_ontology_obj("eventType", Classification)

# READ CSV,PARSE DATA AND BUILD PLAY ROWS
play_rows = []
with open(CSV_PATH, "r", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        events = []

        event_types = parse_list_field(row.get("eventType", ""))
        start_times = parse_list_field(row.get("startTime", ""))
        end_times = parse_list_field(row.get("endTime", ""))

        frame_width = int(row.get("width", "1920"))
        frame_height = int(row.get("height", "1080"))

        passer = parse_list_field(row.get("passer", ""))
        receiver = parse_list_field(row.get("receiver", ""))
        pass_direction = parse_list_field(row.get("passDirection", ""))
        pass_result = parse_list_field(row.get("passResult", ""))

        ball_carrier = parse_list_field(row.get("ballCarrier", ""))
        rush_direction = parse_list_field(row.get("rushDirection", ""))
        rushing_yards = parse_list_field(row.get("rushingYards", ""))
        rush_type = parse_list_field(row.get("rushType", ""))
        rush_scheme = parse_list_field(row.get("rushScheme", ""))
        rushing_attempt_result = parse_list_field(row.get("rushingAttemptResult", ""))

        for i in range(len(event_types)):
            event = PlayEvent(
                eventType=event_types[i],
                startTime=start_times[i],
                endTime=end_times[i],
            )

            if event.eventType == "Pass Attempt":
                event.passer = passer[i] if i < len(passer) else None
                event.receiver = receiver[i] if i < len(receiver) else None
                event.passDirection = pass_direction[i] if i < len(pass_direction) else None
                event.passResult = pass_result[i] if i < len(pass_result) else None

            if event.eventType == "Rushing Attempt":
                event.ballCarrier = ball_carrier[i] if i < len(ball_carrier) else None
                event.rushDirection = rush_direction[i] if i < len(rush_direction) else None
                event.rushingYards = rushing_yards[i] if i < len(rushing_yards) else None
                event.rushType = rush_type[i] if i < len(rush_type) else None
                event.rushScheme = rush_scheme[i] if i < len(rush_scheme) else None
                event.rushingAttemptResult = (
                    rushing_attempt_result[i]
                    if i < len(rushing_attempt_result)
                    else None
                )

            events.append(event)

        play_rows.append(
            PlayRow(
                gameName=row["gameName"],
                fps=float(row["fps"]),
                width=frame_width,
                height=frame_height,
                events=events,
            )
        )


# PROCESS EACH ROW VIDEO AND UPLOAD ITS METADATA FOR MULTIPLE EVENTS
for play_row in play_rows:
    events_metadata = []

    for event in play_row.events:
        start_frame = time_to_frame(event.startTime, play_row.fps)
        end_frame = time_to_frame(event.endTime, play_row.fps)

        meta = {
            "eventType": event.eventType,
            "startTime": event.startTime,
            "endTime": event.endTime,
            "startFrame": start_frame,
            "endFrame": end_frame,
        }

        if event.eventType == "Pass Attempt":
            meta["pass"] = {
                "passer": event.passer,
                "receiver": event.receiver,
                "passDirection": event.passDirection,
                "passResult": event.passResult,
            }

        if event.eventType == "Rushing Attempt":
            meta["rush"] = {
                "ballCarrier": event.ballCarrier,
                "rushDirection": event.rushDirection,
                "rushingYards": event.rushingYards,
            }

        events_metadata.append(meta)

    # SAVE CLIENT METADATA
    for data_row in dataset.data_rows:
        if data_row.title == play_row.gameName:
            data_row.client_metadata = {"events": events_metadata}
            data_row.save()
            break

    #Map Ojects & Classification labels
    for label_row in label_rows:
        if label_row.data_type != "video":
            continue
        if label_row.data_title != play_row.gameName:
            continue

        label_row.initialise_labels(include_object_feature_hashes=set(), include_classification_feature_hashes=set())

        for event, meta in zip(play_row.events, events_metadata):
            option = eventType_cls.get_child_by_title(meta["eventType"])
            cls_inst = eventType_cls.create_instance()
            cls_inst.set_answer(option)
            cls_inst.set_for_frames(
                frames=list(range(meta["startFrame"], meta["endFrame"] + 1)),
                manual_annotation=True,
                confidence=1.0,
            )
            label_row.add_classification_instance(cls_inst)

        label_row.save()

print("Ingest Complete")