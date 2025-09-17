from enum import Enum


class PhotoQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD: str = "good"
    FAIR: str = "fair"
    POOR: str = "poor"
