JalRakshak AI — Sample Simulation Data
========================================

IMPORTANT:
- Every record in this package is fictional and created for a hackathon prototype.
- It is NOT live flood data, a real map, a rescue recommendation, or validated operational guidance.
- Coordinates x/y are arbitrary simulation coordinates, not latitude/longitude.
- Distances, travel times, capacities, urgency labels and confidence scores are illustrative.
- Do not use this dataset to make real-world emergency decisions.

Files:
1. incidents.csv — mock rescue requests and report reliability fields.
2. boats.csv — mock rescue resources, capacities and availability.
3. shelters.csv — mock shelter capacity and occupancy.
4. road_network.csv — mock graph edges with travel time, status and uncertainty.
5. scenario_events.csv — injected events for dynamic re-planning tests.
6. duplicate_test_labels.csv — tiny illustrative labelled set for duplicate detection.

Suggested prototype flow:
- Load these files into a backend or browser simulation.
- Represent road_network.csv as a graph.
- Filter out closed edges when computing routes.
- Treat unverified incidents as review-needed; don't automatically discard them.
- Prevent assignments exceeding boat capacity or shelter remaining capacity.
- On each scenario event, update state and recalculate affected assignments.
- Compare a simple centralized greedy baseline with your multi-agent negotiation method.
- Report time-to-service, unserved requests, idle resource time, route violations and fairness.
