from dataclasses import field
from pydantic import BaseModel, field_validator, model_validator, HttpUrl
from typing import List, Optional


class PlayEvent(BaseModel):

    eventType: str
    startTime: float
    endTime: float

    @model_validator(mode="after")
    def validate_times(self):
        if self.startTime < 0:
            raise ValueError("startTime must be >= 0")

        if self.endTime <= self.startTime:
            raise ValueError("endTime must be greater than startTime")

        return self


class VideoMetadata(BaseModel):

    fps: float
    duration: float
    width: int
    height: int
    file_size: int = 0
    mime_type: str = "video/mp4"

    @model_validator(mode="after")
    def validate_video_metadata(self):

        if self.fps <= 0:
            raise ValueError("fps must be > 0")

        if self.duration <= 0:
            raise ValueError("duration must be > 0")

        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be > 0")

        return self


class VideoUnit(BaseModel):

    objectUrl: HttpUrl
    title: str
    videoMetadata: VideoMetadata
    projectTitle: str
    datasetTitle: str
    events: List[PlayEvent] = field(default_factory=list)

    @field_validator("title", "projectTitle", "datasetTitle")
    def validate_non_empty(cls, value):

        if not value or value.strip() == "":
            raise ValueError("Field cannot be empty")

        return value.strip()
