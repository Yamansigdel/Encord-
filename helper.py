from schema import VideoMetadata, VideoUnit, PlayEvent 
import json
from typing import List

def time_str_to_seconds(t: str) -> float:
    t = t.strip().strip("[]")
    parts = [float(p) for p in t.split(":")]

    if len(parts) == 3:
        h, m, s = parts
        return h * 3600 + m * 60 + s
    elif len(parts) == 2:
        m, s = parts
        return m * 60 + s
    else:
        return parts[0]


def time_to_frame(time_seconds: float, fps: float) -> int:
    return int(time_seconds * fps)


def clean_field(s: str) -> str:
    return s.strip().strip("[]").strip('"').strip("'")

def parse_list_field(s: str):
    cleaned = clean_field(s)
    if not cleaned:
        return []
    # split by comma, remove extra spaces
    return [item.strip() for item in cleaned.split(",")]

def normalize_bbox(x, y, w, h, frame_w, frame_h):
    return {
        "x": x / frame_w,
        "y": y / frame_h,
        "w": w / frame_w,
        "h": h / frame_h,
    }

def parse_bbox_field(s: str):
    cleaned = clean_field(s)
    if not cleaned:
        return None

    parts = [p.strip() for p in cleaned.split(",")]
    if len(parts) != 4:
        return None

    return tuple(map(float, parts))


def load_json_schema(json_path: str):
    with open(json_path, "r") as f:
        raw_data = json.load(f)

    project_hash = raw_data.get("project_hash")
    dataset_hash = raw_data.get("dataset_hash")
    ontology_hash = raw_data.get("ontology_hash")
    storage_folder_hash = raw_data.get("storage_folder_hash")

    videos = []

    for item in raw_data.get("videos", []):
        metadata = item.get("videoMetadata", {})
        client_meta = item.get("clientMetadata", {})

        events = []
        for ev in client_meta.get("events", []):
            events.append(
                PlayEvent(
                    eventType=ev["eventType"],
                    startTime=time_str_to_seconds(ev["startTime"]),
                    endTime=time_str_to_seconds(ev["endTime"]),
                )
            )

        video_unit = VideoUnit(
            objectUrl=item["objectUrl"],
            title=item["title"],
            videoMetadata=VideoMetadata(
                fps=float(metadata["fps"]),
                duration=float(metadata["duration"]),
                width=int(metadata["width"]),
                height=int(metadata["height"]),
                file_size=metadata.get("file_size", 0),
                mime_type=metadata.get("mime_type", "video/mp4"),
            ),
            events=events,
        )

        videos.append(video_unit)

    return project_hash, dataset_hash, ontology_hash, storage_folder_hash, videos
