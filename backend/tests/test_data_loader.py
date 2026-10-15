"""Unit tests for dataset loading and schema validation."""

import pytest
from backend.app.core.data_loader import DataLoader, DataLoaderError
from backend.app.models.enums import UrgencyLevel, BoatStatus, ShelterStatus, EdgeStatus


def test_data_loader_file_presence():
    """Verify that all required files exist in the project root."""
    loader = DataLoader()
    assert loader.boats_file.exists()
    assert loader.incidents_file.exists()
    assert loader.shelters_file.exists()
    assert loader.road_network_file.exists()
    assert loader.scenario_events_file.exists()
    assert loader.duplicate_labels_file.exists()


def test_load_all_counts():
    """Verify entity counts parsed from the original synthetic datasets."""
    loader = DataLoader()
    zones, edges, boats, shelters, incidents, events = loader.load_all()

    assert len(zones) == 11, f"Expected 11 zones, got {len(zones)}"
    assert len(edges) == 12, f"Expected 12 edges, got {len(edges)}"
    assert len(boats) == 4, f"Expected 4 boats, got {len(boats)}"
    assert len(shelters) == 4, f"Expected 4 shelters, got {len(shelters)}"
    assert len(incidents) == 12, f"Expected 12 incidents, got {len(incidents)}"
    assert len(events) == 5, f"Expected 5 events, got {len(events)}"


def test_boat_capacities_and_speeds():
    """Verify boat properties and statuses."""
    loader = DataLoader()
    _, _, boats, _, _, _ = loader.load_all()

    boat_map = {b.boat_id: b for b in boats}
    assert "BOAT01" in boat_map
    assert boat_map["BOAT01"].capacity_people == 8
    assert boat_map["BOAT01"].status == BoatStatus.AVAILABLE
    assert boat_map["BOAT03"].capacity_people == 10


def test_shelter_mapping_and_capacities():
    """Verify shelter capacity formulas and nearest-zone mapping."""
    loader = DataLoader()
    _, _, _, shelters, _, _ = loader.load_all()

    shelter_map = {s.shelter_id: s for s in shelters}

    # Verify SH01
    sh01 = shelter_map["SH01"]
    assert sh01.capacity_people == 40
    assert sh01.current_occupancy == 22
    assert sh01.remaining_capacity == 18
    assert sh01.zone_id == "Northbank-1"

    # Verify SH04 is full
    sh04 = shelter_map["SH04"]
    assert sh04.capacity_people == 15
    assert sh04.current_occupancy == 15
    assert sh04.remaining_capacity == 0
    assert sh04.status == ShelterStatus.FULL


def test_incident_triage_and_headcounts():
    """Verify incident urgencies and affected numbers."""
    loader = DataLoader()
    _, _, _, _, incidents, _ = loader.load_all()

    inc_map = {i.incident_id: i for i in incidents}
    assert inc_map["INC001"].people_affected == 14
    assert inc_map["INC001"].reported_urgency == UrgencyLevel.HIGH
    assert inc_map["INC002"].reported_urgency == UrgencyLevel.CRITICAL
    assert inc_map["INC008"].people_affected == 20

    # Total distressed count is 115
    total_people = sum(i.people_affected for i in incidents)
    assert total_people == 115


def test_duplicate_labels_loading():
    """Verify that duplicate ground truth labels load accurately."""
    loader = DataLoader()
    df = loader.load_duplicate_labels()
    assert len(df) == 4
    # INC001 and INC010 are duplicates
    dup_row = df[(df["incident_a"] == "INC001") & (df["incident_b"] == "INC010")]
    assert len(dup_row) == 1
    assert int(dup_row.iloc[0]["is_duplicate"]) == 1
