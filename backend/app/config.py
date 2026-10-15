"""Configuration and path settings for JalRakshak AI backend."""

from pathlib import Path
from pydantic import BaseModel


class Settings(BaseModel):
    """Application and simulation settings."""

    # Project paths: CSV files live in the workspace root
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent

    # CSV File paths directly in the project root
    BOATS_CSV: Path = PROJECT_ROOT / "boats.csv"
    INCIDENTS_CSV: Path = PROJECT_ROOT / "incidents.csv"
    SHELTERS_CSV: Path = PROJECT_ROOT / "shelters.csv"
    ROAD_NETWORK_CSV: Path = PROJECT_ROOT / "road_network.csv"
    SCENARIO_EVENTS_CSV: Path = PROJECT_ROOT / "scenario_events.csv"
    DUPLICATE_TEST_LABELS_CSV: Path = PROJECT_ROOT / "duplicate_test_labels.csv"

    # Simulation defaults
    SIMULATION_TIME_STEP_MIN: int = 1
    DEFAULT_UNCERTAINTY_LAMBDA: float = 0.5  # Weight penalty for edge uncertainty
    DUPLICATE_DISTANCE_THRESHOLD: float = 0.15  # Coordinate proximity for duplicate detection

    # Bidirectional routing default
    DEFAULT_BIDIRECTIONAL_EDGES: bool = True


settings = Settings()
