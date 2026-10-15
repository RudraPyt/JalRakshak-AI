"""Report deduplication and conflict resolution heuristics for JalRakshak AI.

Implements transparent, rule-based duplicate detection using spatial proximity,
zone alignment, urgency matching, and report metadata. Evaluates performance against
ground truth labels without claiming general ML accuracy.
"""

import math
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from ..models.incident import Incident
from ..models.enums import VerificationStatus, ActionType
from ..config import settings


class DuplicateDetector:
    """Deterministic, rule-based detector for suspected duplicate emergency incident reports."""

    def __init__(self, distance_threshold: float = settings.DUPLICATE_DISTANCE_THRESHOLD):
        self.distance_threshold = distance_threshold

    def compute_similarity(self, inc_a: Incident, inc_b: Incident) -> Tuple[bool, float, str]:
        """
        Compute similarity between two incident reports.
        Returns:
            is_duplicate (bool): True if classified as a likely duplicate.
            similarity_score (float): Score between 0.0 and 1.0.
            reason (str): Transparent, human-readable rationale.
        """
        # Rule 1: Geographical Zone match
        same_zone = inc_a.zone.strip().lower() == inc_b.zone.strip().lower()
        if not same_zone:
            return False, 0.1, f"Different zones ('{inc_a.zone}' vs '{inc_b.zone}')"

        # Rule 2: Spatial coordinate proximity
        spatial_dist = math.hypot(inc_a.x - inc_b.x, inc_a.y - inc_b.y)
        if spatial_dist > self.distance_threshold:
            return False, 0.3, f"Spatial distance ({spatial_dist:.3f}) exceeds threshold ({self.distance_threshold})"

        # Rule 3: Reported urgency consistency
        urgency_match = inc_a.reported_urgency == inc_b.reported_urgency

        # Rule 4: Headcount proximity
        max_people = max(inc_a.people_affected, inc_b.people_affected)
        headcount_diff_ratio = abs(inc_a.people_affected - inc_b.people_affected) / max_people if max_people > 0 else 0.0

        # Rule 5: Report timing proximity
        time_diff = abs(inc_a.report_age_min - inc_b.report_age_min)

        # Composite score
        spatial_score = max(0.0, 1.0 - (spatial_dist / self.distance_threshold))
        headcount_score = max(0.0, 1.0 - headcount_diff_ratio)
        urgency_score = 1.0 if urgency_match else 0.5
        time_score = max(0.0, 1.0 - min(time_diff / 30.0, 1.0))

        score = round(
            0.45 * spatial_score + 0.25 * urgency_score + 0.15 * headcount_score + 0.15 * time_score,
            3
        )

        is_dup = score >= 0.70 and spatial_dist <= self.distance_threshold
        reason = (
            f"Same zone '{inc_a.zone}', coordinates within {spatial_dist:.3f} units "
            f"(threshold {self.distance_threshold}), urgency ({inc_a.reported_urgency.value} vs {inc_b.reported_urgency.value}), "
            f"affected people ({inc_a.people_affected} vs {inc_b.people_affected})."
        )
        return is_dup, score, reason

    def evaluate_against_labels(
        self, labels_df: pd.DataFrame, incidents: Dict[str, Incident]
    ) -> Dict[str, Any]:
        """
        Evaluate the deterministic heuristic against duplicate_test_labels.csv.
        Returns a detailed evaluation dictionary with true labels, predictions, and metrics.
        """
        results = []
        tp = fp = tn = fn = 0

        for _, row in labels_df.iterrows():
            inc_a_id = str(row["incident_a"]).strip()
            inc_b_id = str(row["incident_b"]).strip()
            true_label = int(row["is_duplicate"])
            label_reason = str(row["label_reason"])

            inc_a = incidents.get(inc_a_id)
            inc_b = incidents.get(inc_b_id)

            if not inc_a or not inc_b:
                continue

            pred_dup, score, pred_reason = self.compute_similarity(inc_a, inc_b)
            pred_label = 1 if pred_dup else 0

            if true_label == 1 and pred_label == 1:
                tp += 1
                outcome = "TP"
            elif true_label == 0 and pred_label == 1:
                fp += 1
                outcome = "FP"
            elif true_label == 0 and pred_label == 0:
                tn += 1
                outcome = "TN"
            else:
                fn += 1
                outcome = "FN"

            results.append({
                "pair": f"{inc_a_id} vs {inc_b_id}",
                "true_label": true_label,
                "predicted_label": pred_label,
                "similarity_score": score,
                "outcome": outcome,
                "label_reason": label_reason,
                "heuristic_reason": pred_reason,
            })

        total = len(results)
        accuracy = (tp + tn) / total if total > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "total_pairs_evaluated": total,
            "confusion_matrix": {"TP": tp, "FP": fp, "TN": tn, "FN": fn},
            "metrics": {
                "accuracy": round(accuracy, 3),
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1_score": round(f1, 3),
            },
            "detailed_results": results,
            "disclaimer": (
                "Evaluated on small benchmark (4 pairs). Heuristic demonstrates consistent "
                "spatial-semantic filtering, not general machine-learning generalization."
            ),
        }
