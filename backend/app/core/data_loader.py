"""Data loading and schema validation module for JalRakshak AI.

Loads raw CSV files directly from the project root, performs schema and referential
integrity validation, calculates zone centroids, and maps shelters to their nearest
graph zone.
"""

import math
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd

from ..config import settings
from ..models.enums import UrgencyLevel, VerificationStatus, IncidentLifecycleStatus, BoatStatus, ShelterStatus, EdgeStatus, EventType
from ..models.graph import ZoneNode, NetworkEdge
from ..models.incident import Incident
from ..models.boat import Boat
from ..models.shelter import Shelter
from ..models.event import ScenarioEvent


class DataLoaderError(Exception):
    """Raised when data parsing, schema validation, or referential integrity fails."""
    pass


class DataLoader:
    """Loads and validates simulation CSV datasets from the project root."""

    def __init__(self, project_root: Path = settings.PROJECT_ROOT):
        self.project_root = project_root
        self.boats_file = project_root / "boats.csv"
        self.incidents_file = project_root / "incidents.csv"
        self.shelters_file = project_root / "shelters.csv"
        self.road_network_file = project_root / "road_network.csv"
        self.scenario_events_file = project_root / "scenario_events.csv"
        self.duplicate_labels_file = project_root / "duplicate_test_labels.csv"

        self._check_files_exist()

    def _check_files_exist(self) -> None:
        """Verify that all required CSV files are present in the project root."""
        required = [
            self.boats_file,
            self.incidents_file,
            self.shelters_file,
            self.road_network_file,
            self.scenario_events_file,
            self.duplicate_labels_file,
        ]
        missing = [str(f) for f in required if not f.exists()]
        if missing:
            raise DataLoaderError(f"Missing required dataset files in project root: {', '.join(missing)}")

    def load_road_network(self) -> Tuple[List[NetworkEdge], Dict[str, ZoneNode]]:
        """Load and validate road/water network edges and construct zone nodes."""
        df = pd.read_csv(self.road_network_file)
        expected_cols = {"edge_id", "from_zone", "to_zone", "distance_units", "travel_time_min", "status", "uncertainty"}
        missing_cols = expected_cols - set(df.columns)
        if missing_cols:
            raise DataLoaderError(f"road_network.csv missing columns: {missing_cols}")

        edges: List[NetworkEdge] = []
        zone_names = set()

        for idx, row in df.iterrows():
            try:
                edge = NetworkEdge(
                    edge_id=str(row["edge_id"]).strip(),
                    from_zone=str(row["from_zone"]).strip(),
                    to_zone=str(row["to_zone"]).strip(),
                    distance_units=float(row["distance_units"]),
                    travel_time_min=float(row["travel_time_min"]),
                    status=EdgeStatus(str(row["status"]).strip().lower()),
                    uncertainty=float(row["uncertainty"]),
                )
                edges.append(edge)
                zone_names.add(edge.from_zone)
                zone_names.add(edge.to_zone)
            except Exception as e:
                raise DataLoaderError(f"Error parsing road_network.csv row {idx} ({dict(row)}): {e}")

        # Construct basic ZoneNode objects (coordinates populated from incident/boat anchors)
        zones: Dict[str, ZoneNode] = {
            z: ZoneNode(zone_id=z, x=0.0, y=0.0, description=f"Sector {z}")
            for z in zone_names
        }
        return edges, zones

    def load_boats(self, valid_zones: set) -> List[Boat]:
        """Load and validate rescue boat resources, verifying zone references."""
        df = pd.read_csv(self.boats_file)
        expected_cols = {"boat_id", "current_zone", "x", "y", "capacity_people", "speed_units_per_min", "status", "safety_factor"}
        missing_cols = expected_cols - set(df.columns)
        if missing_cols:
            raise DataLoaderError(f"boats.csv missing columns: {missing_cols}")

        boats: List[Boat] = []
        for idx, row in df.iterrows():
            zone = str(row["current_zone"]).strip()
            if zone not in valid_zones:
                raise DataLoaderError(f"Boat {row['boat_id']} references unknown zone '{zone}' not in road network")

            try:
                boat = Boat(
                    boat_id=str(row["boat_id"]).strip(),
                    current_zone=zone,
                    x=float(row["x"]),
                    y=float(row["y"]),
                    capacity_people=int(row["capacity_people"]),
                    speed_units_per_min=float(row["speed_units_per_min"]),
                    status=BoatStatus(str(row["status"]).strip().lower()),
                    safety_factor=float(row["safety_factor"]),
                )
                boats.append(boat)
            except Exception as e:
                raise DataLoaderError(f"Error parsing boats.csv row {idx} ({dict(row)}): {e}")

        return boats

    def load_incidents(self, valid_zones: set) -> List[Incident]:
        """Load and validate emergency incident requests."""
        df = pd.read_csv(self.incidents_file)
        expected_cols = {
            "incident_id", "zone", "x", "y", "people_affected",
            "report_age_min", "reported_urgency", "source_confidence",
            "verification_status", "assigned_boat_id"
        }
        missing_cols = expected_cols - set(df.columns)
        if missing_cols:
            raise DataLoaderError(f"incidents.csv missing columns: {missing_cols}")

        incidents: List[Incident] = []
        for idx, row in df.iterrows():
            zone = str(row["zone"]).strip()
            if zone not in valid_zones:
                raise DataLoaderError(f"Incident {row['incident_id']} references unknown zone '{zone}'")

            # Parse assigned boat (0 or '0' means unassigned / None)
            assigned_raw = str(row["assigned_boat_id"]).strip()
            assigned_boat = assigned_raw if assigned_raw not in ("0", "", "none", "None", "nan") else None

            try:
                incident = Incident(
                    incident_id=str(row["incident_id"]).strip(),
                    zone=zone,
                    x=float(row["x"]),
                    y=float(row["y"]),
                    people_affected=int(row["people_affected"]),
                    people_rescued=0,
                    people_onboard=0,
                    report_age_min=float(row["report_age_min"]),
                    reported_urgency=UrgencyLevel(str(row["reported_urgency"]).strip().lower()),
                    source_confidence=float(row["source_confidence"]),
                    verification_status=VerificationStatus(str(row["verification_status"]).strip().lower()),
                    lifecycle_status=IncidentLifecycleStatus.PENDING_ASSIGNMENT,
                    assigned_boat_id=assigned_boat,
                )
                incidents.append(incident)
            except Exception as e:
                raise DataLoaderError(f"Error parsing incidents.csv row {idx} ({dict(row)}): {e}")

        return incidents

    def calculate_zone_centroids(
        self, zones: Dict[str, ZoneNode], boats: List[Boat], incidents: List[Incident]
    ) -> Dict[str, Tuple[float, float]]:
        """Calculate representative (x, y) coordinates for each zone based on entities."""
        zone_coords: Dict[str, List[Tuple[float, float]]] = {z: [] for z in zones.keys()}

        for b in boats:
            if b.current_zone in zone_coords:
                zone_coords[b.current_zone].append((b.x, b.y))

        for inc in incidents:
            if inc.zone in zone_coords:
                zone_coords[inc.zone].append((inc.x, inc.y))

        centroids: Dict[str, Tuple[float, float]] = {}
        for z, points in zone_coords.items():
            if points:
                avg_x = sum(p[0] for p in points) / len(points)
                avg_y = sum(p[1] for p in points) / len(points)
                centroids[z] = (round(avg_x, 3), round(avg_y, 3))
            else:
                # Fallback if zone has no initially located entities
                centroids[z] = (0.0, 0.0)

            # Update zone node coordinates
            zones[z].x = centroids[z][0]
            zones[z].y = centroids[z][1]

        return centroids

    def load_shelters(self, zone_centroids: Dict[str, Tuple[float, float]]) -> List[Shelter]:
        """
        Load shelters and map each shelter to its nearest graph zone using Euclidean distance.
        Documents and validates the mapping.
        """
        df = pd.read_csv(self.shelters_file)
        expected_cols = {"shelter_id", "name", "x", "y", "capacity_people", "current_occupancy", "remaining_capacity", "status"}
        missing_cols = expected_cols - set(df.columns)
        if missing_cols:
            raise DataLoaderError(f"shelters.csv missing columns: {missing_cols}")

        shelters: List[Shelter] = []
        for idx, row in df.iterrows():
            sx = float(row["x"])
            sy = float(row["y"])

            # Find nearest zone centroid
            best_zone = None
            min_dist = float("inf")
            for zone_id, (zx, zy) in zone_centroids.items():
                dist = math.hypot(sx - zx, sy - zy)
                if dist < min_dist:
                    min_dist = dist
                    best_zone = zone_id

            if not best_zone:
                raise DataLoaderError(f"Could not map shelter {row['shelter_id']} to any valid zone")

            try:
                shelter = Shelter(
                    shelter_id=str(row["shelter_id"]).strip(),
                    name=str(row["name"]).strip(),
                    zone_id=best_zone,
                    x=sx,
                    y=sy,
                    capacity_people=int(row["capacity_people"]),
                    current_occupancy=int(row["current_occupancy"]),
                    reserved_capacity=0,
                    status=ShelterStatus(str(row["status"]).strip().lower()),
                )
                shelters.append(shelter)
            except Exception as e:
                raise DataLoaderError(f"Error parsing shelters.csv row {idx} ({dict(row)}): {e}")

        return shelters

    def load_scenario_events(self) -> List[ScenarioEvent]:
        """Load and validate dynamic scenario events."""
        df = pd.read_csv(self.scenario_events_file)
        expected_cols = {"event_id", "simulation_minute", "event_type", "target_id", "description", "source_confidence"}
        missing_cols = expected_cols - set(df.columns)
        if missing_cols:
            raise DataLoaderError(f"scenario_events.csv missing columns: {missing_cols}")

        events: List[ScenarioEvent] = []
        for idx, row in df.iterrows():
            try:
                event = ScenarioEvent(
                    event_id=str(row["event_id"]).strip(),
                    simulation_minute=int(row["simulation_minute"]),
                    event_type=EventType(str(row["event_type"]).strip().lower()),
                    target_id=str(row["target_id"]).strip(),
                    description=str(row["description"]).strip(),
                    source_confidence=str(row["source_confidence"]).strip().lower(),
                    applied=False,
                )
                events.append(event)
            except Exception as e:
                raise DataLoaderError(f"Error parsing scenario_events.csv row {idx} ({dict(row)}): {e}")

        return events

    def load_duplicate_labels(self) -> pd.DataFrame:
        """Load duplicate test labels for model/heuristic validation."""
        df = pd.read_csv(self.duplicate_labels_file)
        expected_cols = {"incident_a", "incident_b", "is_duplicate", "label_reason"}
        missing_cols = expected_cols - set(df.columns)
        if missing_cols:
            raise DataLoaderError(f"duplicate_test_labels.csv missing columns: {missing_cols}")
        return df

    def load_all(self) -> Tuple[
        Dict[str, ZoneNode],
        List[NetworkEdge],
        List[Boat],
        List[Shelter],
        List[Incident],
        List[ScenarioEvent]
    ]:
        """Complete, validated load of the entire simulation dataset."""
        edges, zones = self.load_road_network()
        valid_zone_ids = set(zones.keys())

        boats = self.load_boats(valid_zone_ids)
        incidents = self.load_incidents(valid_zone_ids)

        zone_centroids = self.calculate_zone_centroids(zones, boats, incidents)
        shelters = self.load_shelters(zone_centroids)
        events = self.load_scenario_events()

        return zones, edges, boats, shelters, incidents, events
