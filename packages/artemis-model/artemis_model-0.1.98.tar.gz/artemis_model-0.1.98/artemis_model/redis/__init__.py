"""Redis models."""

from .zone_state import ZoneState, NowPlaying, SessionId, BucketId
from .device import ActiveDevice
from .bucket import RedisTrackBucketItem
from .play_history import RedisTrackPlayHistoryItem
from .keys import (
    KEY_ZONE_PLAY_HISTORY_TEMPLATE,
    KEY_ZONE_PUSH_PLAYLIST_BUCKET_TEMPLATE,
    KEY_ZONE_SCHEDULE_BUCKET_TEMPLATE,
    KEY_ZONE_STATE_TEMPLATE,
    KEY_ZONE_ACTIVE_DEVICE_TEMPLATE,
)


__all__ = [
    "ZoneState",
    "NowPlaying",
    "SessionId",
    "BucketId",
    "ActiveDevice",
    "KEY_ZONE_PLAY_HISTORY_TEMPLATE",
    "KEY_ZONE_PUSH_PLAYLIST_BUCKET_TEMPLATE",
    "KEY_ZONE_SCHEDULE_BUCKET_TEMPLATE",
    "KEY_ZONE_STATE_TEMPLATE",
    "KEY_ZONE_ACTIVE_DEVICE_TEMPLATE",
    "RedisTrackBucketItem",
    "RedisTrackPlayHistoryItem",
]
