# 🏈 Encord Video Annotation Pipeline (JSON Ingestion)

A Python-based pipeline for uploading sports video clips to **Encord**, validating structured **JSON schemas**, attaching **client metadata**, and programmatically creating **frame-level classification annotations** using the Encord SDK.

This version replaces the previous CSV ingestion system with a robust, schema-validated **JSON ingestion pipeline**, designed for scalable and reliable sports video annotation workflows.

---

## ✨ What This Project Does

- ✔ Uploads video clips securely using Encord Cloud Integrations  
- ✔ Parses structured event data from validated JSON schema  
- ✔ Performs strict schema validation using **Pydantic**  
- ✔ Converts timestamps → exact frame ranges  
- ✔ Attaches structured video metadata to dataset rows  
- ✔ Automatically applies classification annotations  
- ✔ Uses Encord **bundles** for efficient and safe ingestion  
- ✔ Prevents ingestion failures via early validation  

---

## 🧠 High-Level Workflow

```text
JSON Schema (videos + metadata + events)
        ↓
Schema Validation (Pydantic models)
        ↓
Time (HH:MM:SS) → Seconds → Frame conversion
        ↓
Upload videos via Encord Integration
        ↓
Create Dataset + Project
        ↓
Attach client metadata to data rows
        ↓
Apply frame-level classification annotations
        ↓
Save annotations using Encord Bundles
```

📁 Project Structure
```
pipeline/
│
├── run.py
├── schema.py
├── helper.py
├── input.json
├── .gitignore
└── README.md
```

🔹Structured input file

Example structure:
```
{
  "project_hash":"project_hash",
  "dataset_hash":"dataset_hash",
  "ontology_hash":"ontology_hash",
  "storage_folder_hash":"storage_folder_hash",
  "videos": [
    {
      "objectUrl": "https://bucket.s3.region.amazonaws.com/path/play1.mp4",
      "title": "gameid_gamename_playnumber_clipStartTime_clipEndTime.mp4",
      "videoMetadata": {
        "fps": 25.0,
        "duration": 12.5,
        "width": 1920,
        "height": 1080,
        "file_size": 12345678,
        "mime_type": "video/mp4"
      },
      "clientMetadata": {
        "events": [
            {
            "eventType": "run",
            "startTime": "00:00:05",
            "endTime": "00:00:09"
            },
            {
            "eventType": "throw",
            "startTime": "00:00:11",
            "endTime": "00:00:015"
            },
            {
            "eventType": "catch",
            "startTime": "00:00:18",
            "endTime": "00:00:25"
            }
        ]
      }
    },
{
      "objectUrl": "https://bucket.s3.region.amazonaws.com/path/play2.mp4",
      "title": "gameid_gamename_playnumber_clipStartTime_clipEndTime.mp4",
      "videoMetadata": {
          "fps": 30,
          "duration": 11,
          "width": 1920,
          "height": 1080,
          "file_size": 8021424,
          "mime_type": "video/mp4"
        },
      "clientMetadata": {
        "events":[
          {
            "eventType": "run",
            "startTime": "00:00:03",
            "endTime": "00:00:04"
          },
          {
            "eventType": "throw",
            "startTime": "00:00:05",
            "endTime": "00:00:07"
          },
          {
            "eventType": "catch",
            "startTime": "00:00:08",
            "endTime": "00:00:10"
          }
        ]
      }
    }   
  ],
  "skip_duplicate_urls": true
}
```


⚙ Requirements

Install dependencies:

```
pip install encord pydantic
```

🔐 Authentication Setup

Requires Encord SSH private key:

```
SSH_KEY_PATH="/path/to/private-key.ed25519"
```

▶ How to Run

```
python run.py
```
