import os
from pathlib import Path
from pydantic import BaseModel, Field


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

    # Google Gemini AI Emergency Situation Analyst settings
    GEMINI_API_KEY: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    GEMINI_MODEL: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    GEMINI_TIMEOUT_SECONDS: float = Field(default_factory=lambda: float(os.getenv("GEMINI_TIMEOUT_SECONDS", "30.0")))

    @property
    def effective_gemini_api_key(self) -> str:
        """Dynamically fetch the current GEMINI_API_KEY from environment."""
        return os.getenv("GEMINI_API_KEY", self.GEMINI_API_KEY)

    @property
    def effective_gemini_model(self) -> str:
        """Dynamically fetch the current GEMINI_MODEL from environment."""
        return os.getenv("GEMINI_MODEL", self.GEMINI_MODEL)

    @property
    def effective_gemini_timeout(self) -> float:
        """Dynamically fetch the current GEMINI_TIMEOUT_SECONDS from environment."""
        val = os.getenv("GEMINI_TIMEOUT_SECONDS")
        if val:
            try:
                return float(val)
            except ValueError:
                pass
        return self.GEMINI_TIMEOUT_SECONDS


settings = Settings()
