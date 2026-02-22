from dataclasses import dataclass


@dataclass(frozen=True)
class CityConfig:
    slug: str
    title: str
    state: str
    default_center_lat: float
    default_center_lon: float
    default_zoom: int = 11


CITY_CONFIGS: dict[str, CityConfig] = {
    "austin": CityConfig(
        slug="austin",
        title="Austin",
        state="TX",
        default_center_lat=30.2672,
        default_center_lon=-97.7431,
    ),
    "chicago": CityConfig(
        slug="chicago",
        title="Chicago",
        state="IL",
        default_center_lat=41.8781,
        default_center_lon=-87.6298,
    ),
    "new_york": CityConfig(
        slug="new_york",
        title="New York",
        state="NY",
        default_center_lat=40.7128,
        default_center_lon=-74.0060,
    ),
    "los_angeles": CityConfig(
        slug="los_angeles",
        title="Los Angeles",
        state="CA",
        default_center_lat=34.0522,
        default_center_lon=-118.2437,
    ),
}


CITY_ORDER = ["austin", "chicago", "new_york", "los_angeles"]
