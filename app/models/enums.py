from enum import Enum


class DataSource(str, Enum):
    """Enum for data source types"""

    IPHONE = "iphone"
    APPLE_WATCH = "apple_watch"
    WITHINGS = "withings"
    OURA_RING = "oura_ring"
    FITBIT = "fitbit"
    GARMIN = "garmin"
    SAMSUNG = "samsung"
    GOOGLE_FIT = "google_fit"
    STRAVA = "strava"
    MANUAL = "manual"
    OTHER = "other"
