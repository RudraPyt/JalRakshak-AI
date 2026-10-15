"""Deterministic discrete simulation clock."""

from pydantic import BaseModel, Field


class SimulationClock(BaseModel):
    """Controls the discrete simulation time step."""
    current_minute: int = Field(default=0, ge=0, description="Elapsed simulation time in minutes")
    time_step_min: int = Field(default=1, gt=0, description="Step size per tick in minutes")
    is_running: bool = False

    def tick(self) -> int:
        """Advance time by one discrete step."""
        self.current_minute += self.time_step_min
        return self.current_minute

    def reset(self) -> None:
        """Reset the clock back to minute 0."""
        self.current_minute = 0
        self.is_running = False
