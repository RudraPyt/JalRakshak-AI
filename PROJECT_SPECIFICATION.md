# MASTER PROJECT PROMPT: JALRAKSHAK AI
## Adaptive Flood Rescue Coordination System — Official Problem Statement 27

You are acting as a senior software architect, AI/ML engineer, multi-agent systems researcher, disaster-response simulation specialist, UI/UX designer, and hackathon technical mentor.

Your task is to understand, design, and help build a complete, polished, demonstrable software solution for the hackathon problem statement described below.

Do not treat this as a generic flood-monitoring dashboard, a weather prediction application, a chatbot, or a basic rescue-request management website. The core purpose of this project is to solve the difficult coordination problem that occurs when roads become inaccessible, rescue boats fail, shelters reach capacity, and emergency reports are incomplete, delayed, uncertain, or contradictory.

The project must be technically meaningful, practical to demonstrate, well-structured, measurable, explainable, and realistic about its limitations.

Read this entire specification carefully before proposing an implementation. Do not omit, silently simplify, or replace any mandatory requirement.

---

# 1. OFFICIAL PROBLEM STATEMENT

**PS 27: Flood Rescue Dispatch — Where Boats, Shelters and Roads Negotiate in Real Time**

The official problem statement describes the following challenge:

“Flood response plans become stale as routes close, shelters fill and reports conflict. Coordinate rescue teams, boats, shelters and incident reports as autonomous agents with partial information, resource contention and different urgency levels.”

The implementation challenge is to:

- Implement dynamic replanning over a changing road/water graph.
- Handle reports tagged with uncertainty.
- Respect resource and shelter capacity constraints.
- Apply explicit safety invariants.
- Compare decentralised negotiation with a centralised baseline.

The evaluation must measure:

- Time to service.
- Unmet requests.
- Resource idle time.
- Route violations.
- Fairness across neighbourhoods.
- Recovery after contradictory updates.

The proposed stretch challenge is to trigger a bridge closure, a boat failure, and a shelter overflow simultaneously, then demonstrate which commitments are cancelled, which resources or requests are reassigned, and why.

The minimum acceptable prototype should include:

- A time-stepped simulation.
- Injected events.
- An assignment log.
- Rerouting explanations.
- After-action replay.

Use synthetic locations and scenarios instead of live operational feeds.

**Important:** Keep the project aligned with this problem statement. Do not make flood prediction the primary objective. The central problem is adaptive coordination of rescue resources under changing conditions.

---

# 2. PROJECT IDENTITY AND CORE IDEA

Project name: **JalRakshak AI**

Full name: Adaptive Flood Rescue Coordination System.

One-line description:

JalRakshak AI is a simulation-based, AI-assisted flood rescue coordination platform that continuously coordinates rescue requests, boats, routes, shelters, and uncertain incident reports, adapting its assignments as conditions change while explaining its decisions and evaluating its performance.

## What problem does it solve?

During a flood, an initially reasonable rescue plan can become invalid within minutes.

For example:

- A rescue team is travelling toward a stranded group.
- The bridge on its planned route becomes inaccessible.
- The assigned boat becomes unavailable.
- The shelter where the rescued people were expected to go becomes full.
- A new emergency report arrives from another neighbourhood.
- Two reports disagree about whether a road is open.
- Several urgent incidents compete for the same limited rescue resource.

A static plan cannot adequately handle all these changes.

JalRakshak AI maintains a simulated view of the current situation, coordinates available resources, checks whether assignments remain feasible, replans when conditions change, and records the reasoning behind each decision.

## What is the central innovation?

The project combines five ideas:

1. **Dynamic rescue dispatch:** Rescue assignments are updated when the situation changes.
2. **Multi-agent coordination:** Separate agents represent incidents, boats, routes, shelters, and coordination responsibilities.
3. **Uncertainty-aware decisions:** The system distinguishes confirmed information from uncertain, stale, or contradictory reports.
4. **Explainable replanning:** Every important assignment, cancellation, reroute, or reassignment has a recorded explanation.
5. **Measurable comparison:** The multi-agent approach is evaluated against a centralised baseline using the same scenarios and resource constraints.

The project should demonstrate that rescue coordination is an evolving decision-making problem, not simply a mapping problem.

---

# 3. PROJECT SCOPE AND SAFETY BOUNDARIES

Build a working software simulation for a hackathon demonstration.

The application must use fictional locations, synthetic incident records, simulated resources, and manually injected events. It must not depend on live emergency feeds.

The system must not claim to predict real floods, guarantee rescue outcomes, or provide operational rescue instructions.

It is a research and decision-support prototype. It is not a replacement for emergency services or authorised disaster-management professionals.

Every demonstration view should make the simulated nature of the environment clear.

Do not invent claims such as “government-ready,” “field-tested,” or “proven to save lives.” Explain potential real-world usefulness without claiming that the prototype is ready for real deployments.

---

# 4. PRIMARY USERS AND THEIR RESPONSIBILITIES

Design the application around the following roles.

## 4.1 Simulation Operator

The operator runs and controls the simulation.

The operator should be able to:

- Start, pause, resume, and reset a simulation.
- Select a predefined scenario.
- Inspect current incidents, boats, shelters, and routes.
- Inject new events.
- Advance the simulation clock.
- Inspect current assignments.
- Compare dispatch strategies.
- View system explanations and performance metrics.
- Replay a completed simulation.

## 4.2 Incident Agent

Represents a reported emergency.

Its responsibilities include:

- Maintaining incident details.
- Tracking reported urgency and the number of people requiring assistance.
- Tracking location and incident status.
- Recording the source and confidence of reports.
- Identifying duplicate or conflicting information for review.
- Indicating when an incident needs attention.
- Updating its state when new information arrives.

## 4.3 Boat or Rescue-Resource Agent

Represents a rescue boat or other explicitly modelled rescue resource.

Its responsibilities include:

- Maintaining its location and availability.
- Tracking capacity.
- Tracking operational status.
- Maintaining its current assignment.
- Estimating whether it can reach a proposed incident.
- Reporting a failure or becoming unavailable when a simulated event requires it.
- Participating in reassignment when its current commitment is no longer feasible.

Do not introduce unmodelled rescue equipment as though it exists in the simulation. Boats are the primary rescue resources unless another resource type is deliberately added and fully implemented.

## 4.4 Route Agent

Represents the simulated road/water network and route conditions.

Its responsibilities include:

- Maintaining the graph of locations and connections.
- Tracking route travel costs and accessibility.
- Marking routes open, closed, or uncertain.
- Detecting when a planned route becomes invalid.
- Finding alternative feasible routes.
- Reporting when no valid route exists.
- Recalculating routes after injected events.

## 4.5 Shelter Agent

Represents an evacuation shelter.

Its responsibilities include:

- Tracking total capacity and occupied capacity.
- Calculating remaining capacity.
- Checking whether an incoming assignment can be accommodated.
- Reporting overflow or changed availability.
- Suggesting alternative shelters when appropriate.
- Participating in reassignment when the original destination is no longer feasible.

## 4.6 Coordinator Agent

Acts as the coordination layer of the decentralised strategy.

Its responsibilities include:

- Receiving proposals from relevant agents.
- Resolving competing resource requests.
- Considering urgency, travel cost, capacity, uncertainty, and fairness.
- Detecting invalidated commitments.
- Triggering replanning.
- Recording assignment and cancellation decisions.
- Providing a clear explanation of the final outcome.

Do not merely create five agent classes with different names. Each agent must have meaningful responsibilities, state, inputs, outputs, and interactions.

---

# 5. MANDATORY FUNCTIONAL FEATURES

All features in this section are part of the required solution.

## 5.1 Interactive Flood-Response Simulation Dashboard

Build a polished web dashboard that acts as the central interface for the simulation.

It should display:

- Current simulation time.
- Number of active incidents.
- Number of incidents awaiting assignment.
- Number of assigned incidents.
- Number of served incidents.
- Number of unmet or unserved incidents.
- Number of available, assigned, and failed boats.
- Shelter occupancy and remaining capacity.
- Active route closures.
- Pending or unresolved uncertain reports.
- Current dispatch strategy.
- Most recent replanning event.

Include clear status indicators and useful filters.

The dashboard must display actual state from the simulation engine. Do not use decorative cards with hardcoded numbers that never update.

The user must be able to distinguish between the current situation, completed events, and future or injected events.

## 5.2 Synthetic Geographic Map

Create a simulated geographic environment using fictional locations.

The map can use a lightweight mapping library or a custom graph-based map if that better supports the demonstration.

It should display:

- Incident locations.
- Boat locations.
- Shelter locations.
- Open routes.
- Closed routes.
- Uncertain routes.
- Current planned routes.
- Reassigned or rerouted resources.
- The location of newly injected incidents.

Provide a legend and clear visual distinctions between incident priorities and resource states.

When a route closes, the displayed map and the underlying route graph must both update. When a boat is reassigned, its displayed assignment must change accordingly.

The map must reflect the simulation engine's real state. Do not build a visually impressive map disconnected from the dispatch logic.

All coordinates and location names should be fictional. A geographic basemap is optional; it must not imply that the simulated conditions describe a real flood.

## 5.3 Incident Management

Provide an incident management interface where the operator can inspect all reported emergencies.

Each incident should support the following fields where relevant:

- Unique incident ID.
- Fictional location or graph node.
- Number of people requiring assistance.
- Reported urgency.
- Report timestamp or simulation time.
- Report source.
- Confidence level.
- Incident status.
- Assigned boat, if any.
- Planned route, if available.
- Intended shelter, if assigned.
- Estimated service time, if calculable.
- Explanation of its current status.

Use a clear incident lifecycle, for example:

Reported → Awaiting Assessment → Awaiting Assignment → Assigned → In Progress → Served.

Additional states may include:

- On Hold.
- Replanning Required.
- Unreachable.
- Cancelled.
- Unmet at Simulation End.

Define the lifecycle carefully so that an incident is not counted twice or marked served before the simulation conditions justify it.

The application should support creating incidents manually and loading incidents from synthetic CSV data.

If the operator edits urgency, location, or incident information, validate the input and ensure that the change affects the simulation correctly.

## 5.4 Resource and Boat Management

Provide a dedicated view of all boats and other explicitly modelled resources.

For each boat, display:

- Boat ID.
- Current location.
- Rescue capacity.
- Operational status.
- Current assignment.
- Current destination.
- Estimated route or travel cost.
- Current availability.
- Failure status, where applicable.

The operator should be able to inspect which incidents a boat can serve and why another assignment may be infeasible.

The assignment engine must respect boat availability and capacity. A failed boat must not continue to serve new requests.

If a boat fails while assigned, the simulation must identify its affected commitment, cancel or suspend the invalid assignment, and consider reassignment of the incident.

If a boat is already committed to another incident, the system must not silently assign it to multiple incompatible tasks. Any preemption or reassignment must be governed by explicit rules and logged.

## 5.5 Shelter Capacity Management

Every shelter must have:

- A unique shelter ID.
- A fictional location.
- Total capacity.
- Occupied capacity.
- Remaining capacity.
- Operational status.
- Current or planned incoming assignments, where relevant.

Remaining capacity must be calculated consistently:

Remaining capacity = Total capacity − Occupied capacity.

The system must never assign a group to a shelter if doing so would exceed the modelled capacity.

If the shelter overflows because of an injected event or an update to its available capacity, the system must identify affected assignments and evaluate feasible alternatives.

Do not assume that every incident requires a shelter assignment if the simulation's model explicitly represents an incident that does not involve evacuation. Define the incident types and shelter requirements consistently.

## 5.6 Dynamic Road and Water Network

Represent the simulated environment as a graph.

Depending on the scenario, nodes may represent:

- Incident locations.
- Boat starting locations.
- Junctions or transfer points.
- Shelters.
- Other explicitly modelled locations.

Edges represent traversable connections.

Each edge should contain the relevant attributes, such as:

- Source node.
- Destination node.
- Travel cost or estimated travel time.
- Accessibility state.
- Optional uncertainty information.
- Optional reason for a closure.

The graph must support changes while the simulation is running.

Examples:

- A bridge becomes closed.
- A water route becomes unavailable.
- A previously uncertain route is confirmed open.
- A route is reopened.
- A route's estimated travel cost changes.

Use a graph-search algorithm such as Dijkstra's algorithm or A* for route calculation. Select the algorithm that fits the data model and explain the choice.

The route planner must not use closed edges as valid travel paths. If a route becomes inaccessible after an assignment has been made, the system must re-evaluate the commitment and attempt to find a valid alternative.

If no valid alternative exists, it must record that fact instead of fabricating a route.

A route's status must affect the actual dispatch decisions, not only its colour on the map.

## 5.7 Uncertainty-Aware and Contradictory Reports

This is a central requirement, not an optional AI decoration.

The system must handle information that is incomplete, uncertain, stale, or contradictory.

For example:

- One report says a bridge is open.
- Another report says the same bridge is closed.
- An older report says a shelter has capacity.
- A newer report says the shelter is full.
- An incident location is reported with low confidence.
- A report arrives after the simulation has already assigned a resource.

Every report should carry appropriate metadata, such as:

- Report ID.
- Reported entity.
- Reported condition.
- Source.
- Timestamp.
- Confidence value or uncertainty category.
- Status, such as pending, accepted, superseded, or unresolved.

Define a transparent policy for handling conflicts.

The policy may consider source reliability, freshness, confidence, and the consequence of an incorrect decision. Do not simply accept whichever report arrives last without explaining why that policy is appropriate.

For safety-critical route decisions, the system should behave conservatively when uncertainty cannot be resolved. For example, an unresolved route conflict can cause the route to be treated as unavailable until the simulation's configured policy permits a different decision.

The system should record:

- The conflicting reports.
- The rule used to resolve or preserve the conflict.
- The resulting graph or entity state.
- Any assignments affected by the update.
- Any replanning triggered by the update.

Do not claim to have built an advanced AI verification model if the implementation uses a deterministic rule-based policy. Describe the implementation accurately.

A lightweight machine-learning model for report classification or duplicate detection is optional. The core simulation must work even if no machine-learning model is used.

## 5.8 Priority and Urgency Assessment

Incidents have different urgency levels and may compete for limited resources.

Create an explicit, configurable prioritisation policy.

Possible inputs include:

- Reported urgency.
- Number of people needing assistance.
- Time waiting.
- Feasibility of reaching the incident.
- Boat capacity.
- Travel time.
- Shelter availability.
- Confidence in the relevant information.
- Fairness considerations across neighbourhoods.

Do not combine these factors arbitrarily. Define the scoring or decision rules and explain their purpose.

A transparent weighted score or lexicographic prioritisation policy is acceptable for the MVP. For example, the policy may first exclude infeasible assignments, then prioritise urgency, then compare travel cost and fairness.

If a numeric score is used, document its weights, scale, interpretation, and limitations.

The system must distinguish between:

1. A high-priority incident that is feasible to serve.
2. A high-priority incident that currently has no feasible route.
3. A lower-priority incident that can be served by an available boat.
4. An incident that remains unserved because resources or capacity are insufficient.

The system must not claim that a score guarantees the morally or operationally correct rescue decision.

## 5.9 Dynamic Assignment Engine

Implement the core assignment engine that connects incidents, boats, routes, and shelters.

For each proposed assignment, evaluate:

- Is the boat operational?
- Is it available under the current commitment policy?
- Can it reach the incident through a valid route?
- Is the boat's capacity sufficient for the proposed task?
- Can the incident be served under the simulation's service rules?
- Is a suitable shelter available if evacuation is required?
- Does the assignment violate any resource or capacity constraint?
- How does the assignment affect urgency and fairness?

The engine must produce a feasible assignment or a clear reason why no feasible assignment exists.

When several incidents compete for the same boat, the system must resolve the competition through a defined policy.

When several boats can serve the same incident, the system should compare their feasibility and estimated costs rather than selecting randomly.

When no feasible assignment exists, the incident should remain pending, unreachable, or unmet as appropriate. It must not be falsely marked as served.

The engine must update the simulation state consistently and record its decisions.

## 5.10 Multi-Agent Negotiation

The decentralised multi-agent approach is one of the most important elements of PS 27.

Implement meaningful interaction between the incident, boat, route, shelter, and coordinator agents.

A possible negotiation cycle is:

1. An incident agent announces or updates a request.
2. Relevant boat agents determine whether they can feasibly respond.
3. The route agent supplies valid routes and travel estimates.
4. The shelter agent checks capacity when evacuation is required.
5. Candidate assignments or proposals are generated.
6. The coordinator evaluates competing proposals using the documented policy.
7. A feasible assignment is committed.
8. Agents update their state.
9. The assignment is monitored for invalidation.
10. A new event triggers renegotiation when necessary.

The design can use proposal-and-acceptance negotiation, bidding based on estimated cost, or another suitable lightweight multi-agent mechanism.

Choose a mechanism that can be implemented and demonstrated within the hackathon. Explain why it is appropriate.

The system must resolve contention. Two boats or two incident requests must not create contradictory commitments merely because their agents act independently.

Define a consistent commitment protocol. For example, the coordinator may validate and commit proposals after checking current resource reservations and capacity.

The application must log meaningful agent interactions, such as:

- Proposal generated.
- Candidate rejected because of capacity.
- Route rejected because it is closed.
- Assignment delayed because a boat is unavailable.
- Commitment invalidated by an event.
- Alternative proposal accepted.
- Incident left unassigned because no feasible option exists.

Do not present a normal centralised assignment function with agent-themed labels as a genuine decentralised strategy. Explain which decisions are local to agents, which information they receive, and how conflicts are resolved.

## 5.11 Centralised Baseline

Implement a centralised baseline so that the multi-agent strategy can be compared with a simpler alternative.

The baseline should have access to the same simulated world state, incidents, boats, shelters, route graph, and injected events.

It should obey the same safety and capacity constraints.

A reasonable MVP baseline is a centralised greedy dispatcher that:

1. Evaluates currently feasible incident-resource combinations.
2. Orders them using a documented urgency and cost policy.
3. Assigns available resources while preserving constraints.
4. Recomputes assignments when a relevant event occurs.

Do not intentionally weaken the baseline to make the multi-agent approach look better.

The centralised baseline and multi-agent approach must be tested under comparable conditions, including the same initial state and event schedule.

The baseline may use a different assignment mechanism, but the evaluation must explain any differences in information access, computational assumptions, and replanning behaviour.

## 5.12 Event Injection and Simulation Controls

The simulation must evolve through discrete time steps.

At each step, the system should update relevant state, process due events, validate commitments, run necessary replanning, and record outcomes.

Provide controls to:

- Start a scenario.
- Pause and resume.
- Advance by one simulation step.
- Reset to the initial state.
- Trigger a predefined event.
- Inspect the event history.

Support at least these injected events:

**Event A — Bridge Closure**

Close an edge currently used by an active route. The system must detect that the route is no longer feasible and attempt a valid reroute. If no alternative exists, it must explain the resulting status.

**Event B — Boat Failure**

Make an assigned boat unavailable. Identify the affected incident, invalidate or suspend the commitment, and attempt reassignment with another feasible boat.

**Event C — Shelter Overflow**

Reduce shelter availability or increase its simulated occupancy. Detect any assignment that is no longer feasible and consider alternative shelters or a revised incident status.

**Event D — Contradictory Report**

Introduce conflicting reports about the state of a route, shelter, or other relevant entity. Demonstrate how the uncertainty policy handles the conflict and how it affects planning.

**Event E — Route Reopening**

Reopen a previously closed route. Determine whether the new information improves any pending or active plan.

The simulation must support combining events. Events should be applied in a controlled and reproducible way so the team can repeat the same demonstration.

## 5.13 Simultaneous Failure and Recovery Scenario

This is the required stretch challenge and should be implemented if time permits after the core features are working.

Trigger the following together or within a deliberately short sequence:

- A bridge closes.
- A boat fails.
- A shelter overflows.

Show the system's response from start to finish.

It must:

1. Identify affected commitments.
2. Mark invalid routes and unavailable resources.
3. Re-evaluate current assignments.
4. Cancel, suspend, or modify commitments according to explicit rules.
5. Find feasible alternative boats, routes, and shelters where possible.
6. Reassign incidents without double-booking resources.
7. Leave infeasible incidents in a truthful unresolved state.
8. Record every major decision and its reason.
9. Show how the system recovers as the simulation continues.

The operator must be able to see which commitments were cancelled, who or what was reassigned, and why.

Do not simply replace all assignments with a newly calculated list without showing how the old commitments were invalidated and resolved.

## 5.14 Explainable Decisions and Assignment Log

Every significant dispatch decision must be auditable.

Store events such as:

- Incident received.
- Incident priority assessed.
- Assignment proposed.
- Proposal accepted or rejected.
- Route selected.
- Shelter selected.
- Assignment committed.
- Route invalidated.
- Boat failed.
- Shelter capacity changed.
- Report conflict detected.
- Commitment cancelled or suspended.
- Incident reassigned.
- Incident served.
- Incident left unresolved at simulation end.

Each log entry should contain, where relevant:

- Simulation timestamp.
- Event type.
- Affected incident.
- Affected boat.
- Affected route or shelter.
- Previous state.
- New state.
- Decision or rule applied.
- Explanation.
- Outcome.

For example, an explanation could say:

“Boat B-02 was reassigned from Incident I-04 to Incident I-07 because I-07 had higher configured urgency, B-02 had a feasible route to I-07, and another operational boat remained capable of serving I-04.”

This is an illustrative explanation, not a hardcoded output. Actual explanations must reflect the real state and rules.

The application must not invent explanations that contradict what the assignment engine actually did.

## 5.15 After-Action Replay

Provide a replay interface that allows the operator to understand a completed scenario.

It should show:

- The sequence of injected events.
- How the graph changed.
- Which incidents were pending or active.
- Which boats were assigned or failed.
- How shelter capacity changed.
- When commitments were invalidated.
- Which reassignment decisions were made.
- Why some incidents remained unserved.
- The final simulation metrics.

Provide timeline controls or an equivalent way to move through recorded simulation steps.

Replay should use saved simulation events and state transitions, not simply rerun the simulation with potentially different outcomes.

The operator must be able to review the decision sequence after the scenario has finished.

---

# 6. ALGORITHMS AND AI DESIGN

Use algorithms that solve real parts of the problem. Do not add AI merely for marketing.

## 6.1 Route Finding

Use Dijkstra's algorithm or A* on the road/water graph.

The route calculation must account for:

- Edge travel cost.
- Edge accessibility.
- Current route state.
- Any defined restrictions.

The algorithm must not traverse closed edges.

Explain the selected algorithm and its computational implications in the technical documentation.

## 6.2 Assignment and Prioritisation

Implement a clearly documented heuristic or constrained assignment procedure.

It should evaluate feasible incident-boat combinations and respect capacity, availability, route accessibility, and shelter requirements.

A simple, transparent method is preferable to an unverified claim of global optimality.

Do not claim the system produces a mathematically optimal assignment unless an appropriate optimisation formulation and solver are implemented and verified.

## 6.3 Multi-Agent Coordination

Implement the agent interaction protocol described earlier.

Specify:

- Agent responsibilities.
- Information available to each agent.
- Proposal format.
- Proposal evaluation.
- Conflict resolution.
- Commitment rules.
- Replanning triggers.
- Decision logging.

## 6.4 Uncertainty Handling

Use a documented policy to process confidence, source, freshness, and contradictory reports.

The policy should distinguish uncertainty from certainty and preserve unresolved conflicts in the logs.

A deterministic rule-based approach is acceptable for the MVP.

## 6.5 Optional Machine Learning

If time permits, consider lightweight ML for one well-defined task, such as:

- Classifying synthetic incident descriptions into predefined categories.
- Detecting likely duplicate reports.
- Suggesting urgency categories from synthetic labelled data.

This is optional, not the foundation of the project.

If implemented, use a reproducible dataset and a clear train/test procedure. Report meaningful evaluation metrics and limitations.

Do not use an LLM call as a substitute for route validation, capacity enforcement, or resource commitment logic.

The simulation and dispatch engine must work if an external AI service is unavailable.

## 6.6 Do Not Overengineer

Do not introduce deep learning, reinforcement learning, complex distributed infrastructure, or multiple external AI APIs unless there is a clear and demonstrable reason.

The hackathon objective is a working, explainable, evaluated system—not the largest possible technology stack.

---

# 7. EXPLICIT SAFETY INVARIANTS

Safety invariants are conditions that must remain true throughout every simulation run.

Implement these as actual validation checks, not just statements in the documentation.

At minimum:

**Invariant 1 — No traversal through closed routes**

A committed or newly calculated route must not use an edge that is currently closed.

**Invariant 2 — No unavailable boat assignment**

A failed or otherwise unavailable boat cannot receive a new assignment.

**Invariant 3 — No incompatible double-booking**

A boat cannot hold incompatible simultaneous commitments under the defined resource model.

**Invariant 4 — No shelter overcapacity**

Committed incoming groups must not cause shelter occupancy to exceed the configured capacity.

**Invariant 5 — No false completion**

An incident cannot be marked served unless the simulated service conditions have actually been satisfied.

**Invariant 6 — No fabricated feasibility**

If there is no feasible route, boat, or shelter for a required task, the system must report the constraint instead of inventing a feasible assignment.

**Invariant 7 — Explicit commitment invalidation**

If an event makes an active commitment invalid, the system must detect and record the invalidation and determine its next state.

**Invariant 8 — Consistent resource reservations**

Concurrent agent proposals must not cause contradictory resource or shelter reservations.

**Invariant 9 — Traceable decisions**

Major assignments, cancellations, and reassignments must have a corresponding decision record.

**Invariant 10 — Reproducible scenarios**

Given the same initial state, deterministic configuration, and event schedule, the simulation should produce reproducible results. If random elements are introduced, control them with a recorded seed.

Add automated tests for these invariants.

If an invariant fails, the application should detect the violation and record or surface the failure. Do not hide invalid results from the evaluation dashboard.

---

# 8. PERFORMANCE EVALUATION AND COMPARISON

The project must demonstrate its effectiveness with measurable results rather than visual claims.

Run the multi-agent strategy and centralised baseline on equivalent initial states and event schedules.

## 8.1 Time to Service

Measure the elapsed simulation time from the incident's accepted report time to the defined service-completion time.

Report the metric for served incidents. Also report the number and proportion of incidents that remain unserved so the metric cannot be made artificially attractive by excluding difficult cases without explanation.

Clarify how incidents that never receive service are represented in the results.

## 8.2 Unmet Requests

Measure:

- Total reported incidents.
- Total served incidents.
- Total unmet or unserved incidents.
- Percentage served.
- Percentage unserved.

Define the difference between an incident that remains pending at the simulation end and one that is explicitly cancelled.

## 8.3 Resource Idle Time

Measure the time operational boats spend available but not actively serving or travelling to an assignment, using a clearly documented definition.

Report the total or average idle time.

Do not count failed or unavailable boats as ordinary idle resources.

## 8.4 Route Violations

Count attempted or committed route violations, such as using a closed edge.

The target for a correctly implemented safety-constrained system should be zero committed route violations.

If the system detects a proposed invalid route and rejects it before commitment, log it as a rejected proposal rather than falsely counting it as a committed route violation.

## 8.5 Fairness Across Neighbourhoods

Divide fictional locations into neighbourhoods or zones.

Measure whether service outcomes are disproportionately concentrated in particular zones.

Possible metrics include:

- Service rate by neighbourhood.
- Number of unmet requests by neighbourhood.
- Average service time by neighbourhood.
- Difference between the highest and lowest neighbourhood service rates.
- Jain's fairness index, if the team can explain and correctly implement it.

Document the selected fairness metric and its limitations.

Fairness should not be reduced to serving equal numbers of incidents regardless of urgency. The system must make the trade-off between urgency and equitable service explicit.

## 8.6 Recovery After Contradictory Updates

Measure how the system responds after new or conflicting information invalidates part of the current plan.

Useful measures include:

- Time steps until a feasible plan is restored.
- Number of commitments invalidated.
- Number of incidents successfully reassigned.
- Number of incidents remaining infeasible.
- Number of safety or capacity violations.
- Number of unnecessary changes to unaffected commitments, if measured.

Define precisely what counts as recovery.

## 8.7 Optional Additional Metrics

If feasible, also report:

- Number of successful reassignments.
- Number of infeasible proposals rejected.
- Number of replanning operations.
- Assignment computation time.
- Number of shelter-capacity conflicts prevented.
- Number of route conflicts resolved or left unresolved.

## 8.8 Comparison Methodology

Use the same:

- Initial incidents.
- Boat resources.
- Shelter capacities.
- Road/water graph.
- Event schedule.
- Simulation horizon.
- Incident urgency policy.
- Safety invariants.

For every comparison, document any intentional differences between the strategies.

Run more than one scenario if time permits.

Show results in tables and charts. Include the underlying numbers, not just statements such as “multi-agent is better.”

Do not assume the multi-agent strategy must outperform the baseline on every metric. Discuss trade-offs honestly, including computational overhead, additional coordination, or situations where centralised dispatch performs just as well.

---

# 9. USER INTERFACE AND DASHBOARD DESIGN

Create a professional, modern emergency-coordination interface.

The design should feel like a serious operational simulation and analytical tool, not a generic admin template.

## 9.1 Suggested Main Navigation

Include the following sections:

1. **Overview** — live simulation summary and major status indicators.
2. **Simulation Map** — incidents, boats, shelters, and routes.
3. **Incidents** — incident table, details, priorities, and status.
4. **Resources** — boat availability, capacities, and assignments.
5. **Shelters** — occupancy and capacity.
6. **Dispatch Centre** — assignment decisions and competing proposals.
7. **Events and Reports** — event injection, report conflicts, and uncertainty.
8. **Decision Log** — explanations and state transitions.
9. **Replay** — after-action timeline.
10. **Evaluation** — metrics and strategy comparison.

These are suggested navigation sections, not a requirement to create ten disconnected pages. Related functionality may be combined where that improves usability, provided every mandatory capability remains accessible.

## 9.2 Visual Behaviour

Use clear visual hierarchy, readable typography, consistent spacing, accessible colour contrast, and meaningful status labels.

Provide:

- Useful empty states.
- Loading and error states.
- Confirmation for destructive actions such as resetting a scenario.
- Input validation.
- Filters and sorting where useful.
- Responsive layouts.
- Clear distinction between simulated data and actual operational data.

The interface should make the most important questions easy to answer:

- What is happening now?
- Which incidents are most urgent?
- Which resources are available?
- Which commitments are no longer feasible?
- What changed?
- What is the system doing about it?
- Why did it make that decision?
- How well did the strategy perform?

Avoid adding decorative charts that do not communicate meaningful information.

---

# 10. TECHNICAL ARCHITECTURE

Propose and implement a clean architecture appropriate for a team of three or four people with web-development skills and basic AI/ML knowledge.

A recommended stack is:

### Frontend

- React.
- TypeScript, if practical.
- A clean component-based architecture.
- A mapping library such as Leaflet, or a custom graph visualisation.
- Recharts or Chart.js for metrics and comparisons.
- A consistent styling system such as Tailwind CSS, if appropriate.

### Backend

- Python.
- FastAPI for API endpoints.
- Pydantic for request and response validation.
- A dedicated simulation engine that is separate from HTTP route handlers.

### Simulation and Algorithms

- Python graph algorithms, using NetworkX or a well-tested custom implementation.
- Pandas for synthetic data loading and analysis.
- Explicit agent classes or modules.
- A deterministic simulation clock and event scheduler.
- A centralised baseline implementation.
- A separate multi-agent coordination implementation.
- A metrics calculation module.

### Persistence

SQLite is sufficient for an MVP if persistence is required.

Persist the data necessary to inspect completed simulations, including scenario configuration, event history, state transitions, assignments, and evaluation results.

Do not introduce a complex database or distributed system unless a specific requirement justifies it.

### API and State Synchronisation

Define a clean boundary between the frontend and simulation engine.

The frontend should request operations and render authoritative backend state.

Useful endpoint categories include:

- Scenario loading and creation.
- Simulation start, pause, resume, step, and reset.
- Current simulation state.
- Incident management.
- Resource and shelter inspection.
- Event injection.
- Assignment inspection.
- Decision log retrieval.
- Replay state retrieval.
- Evaluation results.

Choose appropriate HTTP methods and response models.

WebSockets or server-sent events are optional. Use polling if that is more reliable and easier to complete within the hackathon.

Do not allow the frontend and backend to maintain conflicting independent versions of the simulation state.

## 10.1 Separation of Concerns

Separate at least these modules:

- Data models and validation.
- Scenario loader.
- Simulation clock and event scheduler.
- Road/water graph and route planner.
- Incident manager.
- Resource manager.
- Shelter manager.
- Uncertainty and report-conflict resolver.
- Priority and feasibility evaluator.
- Multi-agent coordination engine.
- Centralised baseline dispatcher.
- Safety-invariant validator.
- Assignment and decision logger.
- Metrics and evaluation engine.
- API layer.
- Frontend presentation layer.

You may adjust module boundaries if you explain why, but do not place all application logic in one large file.

## 10.2 Data Integrity

Use consistent identifiers and relationships between incidents, boats, shelters, graph nodes, routes, and events.

Validate all imported data.

Reject malformed inputs with useful error messages.

Ensure that event processing, resource reservations, shelter reservations, and assignment changes occur in a consistent order.

If a simulation step fails, do not silently continue with a partially corrupted state.

---

# 11. SYNTHETIC DATASET AND INITIAL SCENARIO

Use a fictional dataset that is small enough to understand and large enough to demonstrate resource contention and dynamic replanning.

A sample dataset may include:

- Approximately 12 initial incidents.
- Approximately 4 rescue boats.
- Approximately 4 shelters.
- Approximately 12 or more graph edges.
- Several predefined events.
- Synthetic report-conflict examples.

These are suggested starting values, not rigid limits. Expand the dataset if necessary to demonstrate meaningful competition and recovery.

If a sample dataset ZIP is attached, inspect and reuse its actual schema and records. Do not silently replace it with a different dataset. If a field or file is missing, explain what needs to be added.

The data should include meaningful edge cases:

- More incidents than available boats.
- Incidents with different urgency levels.
- A boat with insufficient capacity for a particular task.
- A shelter with little remaining capacity.
- A route closure that affects an active assignment.
- A failed boat.
- A shelter overflow.
- Contradictory reports.
- A reopened route.
- At least one incident that cannot initially be served.
- At least one incident that becomes feasible after an event.
- At least one case where a reasonable reassignment is possible.
- At least one case where no feasible alternative exists.

Use reproducible initial states and event schedules.

Clearly label all data as synthetic.

If a file named `duplicate_test_labels.csv` is included, inspect its contents and decide whether it is sufficient for a small duplicate-detection experiment. Do not assume that a tiny dataset is sufficient to train a reliable general-purpose model.

Do not fabricate real-world incident statistics or present fictional coordinates as real flood locations.

---

# 12. REQUIRED DEMONSTRATION SCENARIO

Prepare a reliable, repeatable demonstration for judges.

The demo should tell a clear story rather than showing unrelated features.

## Stage 1 — Initial Situation

Load the synthetic scenario.

Show:

- Multiple active incidents.
- Limited available boats.
- Several shelters with different remaining capacities.
- An initially feasible route network.
- Incidents competing for resources.
- Different urgency levels.

Run the dispatch process and display the initial assignments.

Explain why each assignment was selected and why other candidate assignments were rejected.

## Stage 2 — Change the Environment

Inject a bridge closure affecting an active route.

Show:

- The route state changing.
- The current assignment becoming invalid or requiring re-evaluation.
- Alternative route calculation.
- Reassignment or a clear explanation of why no alternative is feasible.
- Corresponding decision-log entries.

## Stage 3 — Resource Failure

Trigger a boat failure while an incident is assigned to that boat.

Show:

- The boat becoming unavailable.
- The affected commitment being invalidated.
- The incident being considered for reassignment.
- Other resource commitments remaining consistent.
- The outcome being recorded.

## Stage 4 — Shelter Overflow

Trigger a shelter overflow.

Show:

- The shelter's remaining capacity changing.
- Affected incoming assignments being checked.
- Alternative shelters being evaluated.
- Any infeasible assignment being rejected.
- The resulting state and explanation.

## Stage 5 — Contradictory Reports

Introduce conflicting information about a route or shelter.

Show:

- Both reports and their metadata.
- The configured uncertainty policy.
- The resulting accepted, unresolved, or superseded state.
- Any affected route or assignment.
- The reason for the decision.

## Stage 6 — Simultaneous Failure

Trigger the bridge closure, boat failure, and shelter overflow together or in a controlled near-simultaneous sequence.

Demonstrate the complete recovery process.

Make it clear which commitments were cancelled, which were retained, which were reassigned, and why.

## Stage 7 — Strategy Comparison

Run the same scenario using:

1. The centralised baseline.
2. The multi-agent coordination strategy.

Compare their metrics.

Do not claim that one approach is superior unless the measured results support that conclusion.

## Stage 8 — After-Action Replay

Open the replay view.

Walk through the timeline and explain how the system moved from the initial state to the final state.

Finish with the performance dashboard, including both successful outcomes and unresolved incidents.

The demonstration must be achievable using the application's actual working features. Do not rely on manually edited screenshots or hardcoded final results.

---

# 13. TESTING REQUIREMENTS

Create automated tests for the critical logic before polishing the interface.

At minimum, test the following.

## Route Tests

- A valid route is found when one exists.
- Closed edges are excluded.
- A route is recalculated after a closure.
- No route is fabricated when no path exists.
- Reopening an edge can make a previously infeasible route feasible.

## Resource Tests

- An available boat can receive a feasible assignment.
- An unavailable boat cannot receive a new assignment.
- A boat cannot be double-booked incompatibly.
- A failed assigned boat triggers the appropriate commitment update.

## Shelter Tests

- A feasible group can be assigned within capacity.
- An assignment that exceeds capacity is rejected.
- Shelter overflow invalidates affected assignments where necessary.
- Alternative shelter selection respects capacity.

## Incident Tests

- Incidents move through valid lifecycle transitions.
- Served incidents are not counted twice.
- Unserved incidents are not falsely marked as served.
- Pending and cancelled incidents are distinguished.

## Uncertainty Tests

- Conflicting reports are detected.
- Report freshness and confidence are handled according to the documented policy.
- Unresolved uncertainty does not silently become certainty.
- A conflict affecting a route or shelter triggers the appropriate re-evaluation.

## Multi-Agent Tests

- Competing proposals are resolved.
- Rejected proposals include a reason.
- Resource reservations remain consistent.
- Commitment invalidation triggers renegotiation.
- Agent interactions are logged.

## Evaluation Tests

- Metrics are computed from simulation data rather than hardcoded.
- Centralised and multi-agent strategies use comparable scenarios.
- Repeated deterministic runs produce consistent results.
- Safety violations are counted according to the documented definitions.

Also test the simultaneous failure scenario and ensure that the system ends in a valid state even when some incidents cannot be served.

---

# 14. TEAM STRUCTURE

Assume a team of three or four members.

For four members, suggest this division:

**Member 1 — Frontend and Visualisation**
- Dashboard.
- Simulation map.
- Incident, resource, and shelter views.
- Event controls.
- Replay and evaluation interface.

**Member 2 — Backend and Data**
- FastAPI endpoints.
- Data models and validation.
- Scenario loading.
- Persistence, where needed.
- Frontend/backend integration.

**Member 3 — Simulation and Algorithms**
- Graph and route planning.
- Assignment feasibility.
- Prioritisation.
- Multi-agent negotiation.
- Centralised baseline.
- Dynamic replanning.

**Member 4 — Testing, Evaluation, and Integration**
- Safety-invariant tests.
- Failure scenarios.
- Metrics and comparison.
- Data validation.
- Integration testing.
- Demo preparation and presentation.

For a three-person team, combine related responsibilities without dropping the mandatory functionality.

Keep interfaces between team members explicit. Define the data models, API contracts, and expected outputs before parallel implementation.

---

# 15. DEVELOPMENT PRIORITIES

Build the project in a sequence that reduces integration risk.

## Phase 1 — Foundation

- Inspect the dataset.
- Define data models.
- Build the synthetic graph.
- Implement incidents, boats, shelters, and event models.
- Establish the simulation clock.
- Implement route finding and basic feasibility checks.

## Phase 2 — Working Dispatch

- Implement the centralised baseline.
- Implement capacity and commitment validation.
- Add the assignment log.
- Verify that a scenario can be run end to end.

## Phase 3 — Multi-Agent Coordination

- Implement agent responsibilities and proposal exchange.
- Resolve competing proposals.
- Add commitment validation and negotiation logs.
- Compare outcomes with the centralised baseline.

## Phase 4 — Dynamic Events

- Implement bridge closure.
- Implement boat failure.
- Implement shelter overflow.
- Implement contradictory reports.
- Implement route reopening.
- Add automatic replanning and commitment recovery.

## Phase 5 — Evaluation and Replay

- Implement performance metrics.
- Run comparable scenarios.
- Store event and state-transition histories.
- Implement after-action replay.

## Phase 6 — Frontend and Integration

- Connect the interface to the actual simulation state.
- Implement the map and dashboard.
- Add event controls and decision explanations.
- Add the comparison charts.

## Phase 7 — Validation and Presentation

- Run automated tests.
- Test the complete simultaneous-failure scenario.
- Verify that the demo works from a clean start.
- Check all calculations and displayed results.
- Prepare the presentation and technical explanation.

Do not spend most of the available time polishing the map before the assignment engine, event processing, and safety constraints work correctly.

---

# 16. EXPECTED PROJECT DELIVERABLES

Help produce a complete, runnable hackathon prototype with the following deliverables.

1. **Working application:** Frontend and backend connected to a functional simulation engine.
2. **Synthetic dataset:** Validated, documented sample data.
3. **Centralised baseline:** A functional comparison strategy.
4. **Multi-agent strategy:** Meaningful agent interaction and conflict resolution.
5. **Dynamic replanning:** Correct handling of changing routes, failed boats, shelter overflow, and contradictory reports.
6. **Decision log:** Traceable assignments, cancellations, reroutes, and explanations.
7. **After-action replay:** Reviewable event timeline and state transitions.
8. **Evaluation dashboard:** Metrics and strategy comparison calculated from actual runs.
9. **Automated tests:** Tests for algorithms, constraints, and safety invariants.
10. **README:** Installation, configuration, startup, architecture, dataset format, and troubleshooting.
11. **API documentation:** Endpoint descriptions and request/response examples.
12. **Architecture diagram:** Frontend, backend, simulation engine, agents, graph planner, data layer, and metrics.
13. **Demo script:** A repeatable demonstration of the failure and recovery scenario.
14. **Hackathon presentation:** A concise presentation explaining the problem, solution, innovation, architecture, algorithms, results, limitations, and potential impact.

Do not mark a deliverable complete until its relevant implementation exists and has been checked.

---

# 17. HACKATHON PRESENTATION STRUCTURE

Prepare a presentation of approximately 10–12 slides.

Suggested structure:

1. Project title and team.
2. Official problem statement and real-world coordination challenge.
3. Why static flood-response plans become stale.
4. Proposed solution: JalRakshak AI.
5. System architecture and agent responsibilities.
6. Route planning, prioritisation, constraints, and uncertainty handling.
7. Multi-agent negotiation versus centralised baseline.
8. Dynamic failure scenario and replanning.
9. Demonstration screenshots or actual application views.
10. Evaluation metrics and measured results.
11. Limitations, safety boundaries, and deployment requirements.
12. Expected impact and future development.

Do not invent experimental results to fill a slide. If evaluation has not been completed, label results as pending or use a clearly identified illustrative example.

---

# 18. WHAT MAKES THIS PROJECT DIFFERENT

The project must communicate the following distinction clearly.

A basic flood dashboard displays information.

A basic rescue-management application records requests.

A route-finding application finds paths.

JalRakshak AI combines these functions into a coordinated simulation in which:

- Requests compete for scarce resources.
- Routes and destinations can become infeasible.
- Reports may be uncertain or contradictory.
- Agents propose and negotiate assignments.
- Resource and shelter constraints are enforced.
- New events invalidate previous commitments.
- The system replans and explains the consequences.
- The result is evaluated against a centralised baseline.
- The complete decision history can be replayed and audited.

The central innovation is **constraint-aware, uncertainty-aware, explainable, dynamic coordination under changing conditions**, supported by a measurable comparison of decentralised and centralised dispatch.

Do not describe the project as innovative solely because it uses AI, agents, or a map. Explain the specific coordination problem it addresses and demonstrate how the implementation handles it.

---

# 19. LIMITATIONS AND FUTURE SCOPE

Document limitations honestly.

Possible limitations include:

- Synthetic scenarios cannot reproduce every real flood condition.
- Travel costs and route states are simplified.
- Report confidence may be simulated rather than derived from validated real-world sources.
- The priority policy may not represent all emergency-response requirements.
- The multi-agent strategy may have coordination overhead.
- The evaluation results apply only to the scenarios and assumptions tested.

Possible future extensions include:

- Integration with verified weather, flood, road, or emergency datasets.
- More sophisticated uncertainty estimation.
- Additional rescue resources.
- Improved optimisation methods.
- Larger-scale simulation.
- Human approval for consequential decisions.
- Testing with disaster-management professionals.
- Carefully validated integration with authorised operational systems.

These are future possibilities, not implemented features unless they are actually built.

---

# 20. STRICT IMPLEMENTATION RULES

Follow these rules throughout the project:

1. Do not omit any mandatory feature described in this prompt.
2. Do not replace dynamic coordination with a static dashboard.
3. Do not replace the assignment engine with hardcoded assignments.
4. Do not simulate multi-agent behaviour merely through decorative labels.
5. Do not let the frontend become the source of truth for backend simulation state.
6. Do not use closed routes or failed boats in committed assignments.
7. Do not allow shelter overcapacity.
8. Do not falsely mark unresolved incidents as served.
9. Do not ignore contradictory reports.
10. Do not conceal cancelled commitments or failed assignments.
11. Do not hardcode performance metrics or comparison results.
12. Do not claim that the multi-agent strategy is better without evidence.
13. Do not claim that a heuristic is mathematically optimal without proof or appropriate evaluation.
14. Do not claim that synthetic data represents live flood conditions.
15. Do not make the project dependent on paid AI APIs for its core functionality.
16. Do not add optional complexity before the required simulation works.
17. Do not generate an enormous, untested codebase in a single step.
18. Do not leave critical TODOs while describing the project as complete.
19. Do not silently omit files or provide inconsistent imports, models, or endpoint contracts.
20. Keep all decision rules, assumptions, and metric definitions documented.
21. Use reproducible scenarios and automated tests.
22. Explain any deviation from this specification and obtain approval before removing a mandatory feature.

When a trade-off is necessary, preserve the official problem requirements, core simulation correctness, explicit safety invariants, dynamic replanning, decision traceability, and fair evaluation before adding optional ML or visual polish.

---

# 21. HOW I WANT YOU, CLAUDE, TO WORK

Do not start by dumping the entire codebase without a plan.

Work in controlled stages.

## First Response: Architecture and Requirements Validation

Before writing implementation code:

1. Summarise your understanding of the official problem statement.
2. Explain the proposed solution in your own words.
3. List every mandatory feature and map it to a specific module or component.
4. Explain the simulation state model.
5. Define the agent responsibilities and interaction protocol.
6. Define the centralised baseline and multi-agent comparison methodology.
7. Define the uncertainty policy.
8. Define the assignment and prioritisation policy.
9. Define the safety invariants.
10. Define all evaluation metrics precisely.
11. Propose the repository structure.
12. Define the backend API contracts and shared data models.
13. Identify technical risks, ambiguous requirements, and integration dependencies.
14. Provide a phased implementation plan with acceptance criteria for each phase.

Check that the architecture covers every mandatory feature in this prompt. If something is missing, correct the architecture before coding.

Do not ask me to decide every minor technical detail. Choose sensible, hackathon-appropriate defaults and explain them. Ask a question only when a genuinely important decision cannot be made from the specification or attached files.

## Second Stage: Core Simulation

Implement the models, graph, route planner, simulation clock, event scheduler, resource constraints, shelter constraints, centralised baseline, and decision log.

Add tests before proceeding.

## Third Stage: Multi-Agent Strategy

Implement the agent protocol, competing proposals, commitment validation, conflict resolution, and replanning triggers.

Verify that the multi-agent implementation is genuinely different from the centralised baseline.

## Fourth Stage: Failure Scenarios and Evaluation

Implement the injected events, contradictory-report handling, simultaneous-failure scenario, metrics, strategy comparison, and after-action replay.

Verify that the results come from actual simulation runs.

## Fifth Stage: Frontend and Integration

Build and connect the dashboard, map, incident/resource/shelter views, dispatch controls, decision log, replay, and evaluation interface.

Verify that displayed state updates when the backend simulation changes.

## Sixth Stage: Final Verification

Perform a requirement-by-requirement audit against this complete prompt.

Provide a checklist showing:

- Requirement.
- Implementation location.
- Test or verification method.
- Current status.
- Any remaining limitation.

Run the critical scenario from a clean start. Verify route feasibility, boat availability, shelter capacity, incident status transitions, event handling, replay consistency, and metrics.

Fix errors before calling the project complete.

---

# 22. FINAL ACCEPTANCE CRITERIA

The project is ready for the hackathon demonstration only when all of the following are true:

- The application can load a synthetic scenario and run a time-stepped simulation.
- The operator can inspect incidents, boats, shelters, and the changing graph.
- The system produces actual feasible assignments.
- The centralised baseline works.
- The multi-agent strategy performs meaningful proposal exchange and conflict resolution.
- The system handles bridge closures, boat failures, shelter overflow, contradictory reports, and route reopening.
- Invalidated commitments are identified and resolved or explicitly left infeasible.
- Safety invariants are enforced and tested.
- Every significant assignment and reassignment has a meaningful explanation.
- The operator can replay the event sequence.
- Evaluation metrics are calculated from actual simulation results.
- Both strategies can be compared on equivalent scenarios.
- The simultaneous-failure demonstration works.
- The frontend and backend remain consistent.
- The application can be installed and launched using documented steps.
- The limitations and synthetic nature of the data are clearly disclosed.
- No mandatory feature is falsely claimed as implemented.

If any criterion is not met, identify it honestly and provide the smallest concrete implementation step needed to address it.

## YOUR IMMEDIATE TASK

Begin with the architecture and requirements-validation stage.

First, explain the proposed architecture and show a complete feature-to-module mapping. Then provide the data model, agent interaction protocol, API contracts, safety invariants, evaluation definitions, repository structure, and implementation roadmap.

Do not begin with a generic introduction to AI or flood management. Focus on the specific implementation of JalRakshak AI and the official PS 27 requirements.

Be technically precise, explicit about assumptions, honest about limitations, and systematic about completeness. The objective is to build a working, defensible hackathon solution that demonstrates adaptive flood rescue coordination under uncertainty—not merely a presentation or a visually impressive mockup.
