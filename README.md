# 🏈 Encord Video Annotation Pipeline

A Python-based pipeline for uploading sports video clips to **Encord**, attaching structured **client metadata**, and programmatically adding **classification and object annotations** using the Encord SDK.

This project is built for scalable **football play analysis** (Pass Attempts, Rushing Attempts, etc.) and supports batch ingestion with Encord **bundles**.

---

## ✨ What This Project Does

✔ Uploads video clips to Encord  
✔ Parses structured event data from CSV files  
✔ Converts timestamps → frame ranges  
✔ Attaches event metadata to dataset rows  
✔ Adds classification labels programmatically  
✔ Supports object-level annotations (experimental)  
✔ Uses **bundles** for safe & efficient label ingestion  

---

## 🧠 High-Level Workflow

```text
CSV (events + timestamps)
        ↓
Schema parsing (PlayRow / PlayEvent)
        ↓
Time → Frame conversion
        ↓
Dataset client metadata mapping
        ↓
Classification / Object annotations
        ↓
Bundled save to Encord

📄 File Descriptions

🔹 upload.py
Handles uploading video clips to Encord storage.

🔹 run.py
 Main production pipeline

🔹 try.py
 Experimental / sandbox script

🔹 schema.py
Defines structured data models.

🔹 builders.py
Helper utilities used across the pipeline.

🔹 display.py
Inspection & debugging helper.
