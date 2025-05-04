"""Zone state schema."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator


class NowPlaying(BaseModel):
    """Now playing schema."""

    name: str = Field(description="The name of the track", default="UNKNOWN")
    artist_name: str = Field(description="The artist name of the track", default="UNKNOWN")
    album_name: str = Field(description="The album name of the track", default="UNKNOWN")


SessionId = Annotated[
    int,
    Field(
        description="The session id of the pushed playlist. It's generated as a timestamp value of the current time."
    ),
]
BucketId = Annotated[
    int | None,
    Field(
        description="The bucket id of the pushed playlist. It's calculated in set_bucket_track as the timestamp value of the timeslot."
    ),
]


class ZoneState(BaseModel):
    """Zone state schema."""

    player_mode: Literal["scheduled", "pushplaylist"] = Field(
        default="scheduled",
        description="The mode of the player",
    )
    player_state: Literal["playing", "paused", "stopped", "ready"] = Field(
        default="ready",
        description="The state of the player",
    )
    now_playing: NowPlaying | None = Field(
        default=None,
        description="The currently playing track",
    )
    push_playlist_details: dict[SessionId, BucketId] | None = Field(
        default_factory=dict,
        description="The details of the pushed playlist",
    )

    @field_validator("push_playlist_details", mode="before")
    @classmethod
    def default_empty_dict_if_none(cls, v):
        """Override none value to empty dict."""
        return v or {}


__all__ = ["ZoneState", "NowPlaying", "SessionId", "BucketId"]
