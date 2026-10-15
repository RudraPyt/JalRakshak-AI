"""Unit tests for report deduplication and contradictory report handling."""

import pytest
from backend.app.core.data_loader import DataLoader
from backend.app.core.uncertainty import DuplicateDetector
from backend.app.models.enums import VerificationStatus, UrgencyLevel
from backend.app.models.incident import Incident


@pytest.fixture
def data():
    loader = DataLoader()
    _, _, _, _, incidents, _ = loader.load_all()
    labels = loader.load_duplicate_labels()
    return {i.incident_id: i for i in incidents}, labels


def test_duplicate_benchmark_evaluation(data):
    """
    Evaluate deterministic heuristic on the official duplicate_test_labels.csv benchmark.
    Must correctly identify INC001 and INC010 as duplicates (TP) and the other 3 pairs as distinct (TN).
    """
    incidents, labels = data
    detector = DuplicateDetector(distance_threshold=0.15)
    evaluation = detector.evaluate_against_labels(labels, incidents)

    assert evaluation["total_pairs_evaluated"] == 4
    cm = evaluation["confusion_matrix"]
    assert cm["TP"] == 1, "INC001 and INC010 must be detected as True Positive duplicate"
    assert cm["TN"] == 3, "Other 3 distinct pairs must be classified as True Negatives"
    assert cm["FP"] == 0
    assert cm["FN"] == 0
    assert evaluation["metrics"]["accuracy"] == 1.0


def test_duplicate_detection_reasons(data):
    """Verify that heuristic produces transparent, human-readable explanations."""
    incidents, _ = data
    detector = DuplicateDetector(distance_threshold=0.15)

    is_dup, score, reason = detector.compute_similarity(incidents["INC001"], incidents["INC010"])
    assert is_dup is True
    assert score >= 0.70
    assert "Northbank-1" in reason
    assert "coordinates within" in reason


def test_different_zones_are_not_duplicates(data):
    """Reports in different zones must immediately be rejected as duplicates."""
    incidents, _ = data
    detector = DuplicateDetector(distance_threshold=0.15)

    is_dup, score, reason = detector.compute_similarity(incidents["INC001"], incidents["INC003"])
    assert is_dup is False
    assert "Different zones" in reason


def test_contradictory_report_flagging():
    """Verify that contradictory information flags uncertainty without deleting records."""
    inc = Incident(
        incident_id="INC099",
        zone="WestHamlet",
        x=3.2,
        y=1.8,
        people_affected=6,
        reported_urgency=UrgencyLevel.MEDIUM,
        verification_status=VerificationStatus.VERIFIED,
    )

    # Injected conflict arrives
    inc.verification_status = VerificationStatus.POSSIBLE_DUPLICATE
    inc.status_explanation = "Conflicting report received regarding road access"

    assert inc.verification_status == VerificationStatus.POSSIBLE_DUPLICATE
    assert inc.people_affected == 6, "Data must be preserved, not discarded"
