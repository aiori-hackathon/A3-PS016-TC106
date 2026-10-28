# RFC-2330, security, and privacy

## What RFC 2330 says

[RFC 2330](https://www.rfc-editor.org/rfc/rfc2330.html) provides an IP Performance Metrics framework. It says active measurement traffic can be abused as denial-of-service traffic disguised as measurement, passive observation can reveal traffic contents, and each metric/methodology definition should discuss its security considerations. RFC 2330 is an Informational framework and has later updates (RFCs 7312, 8468, and 9198); this project is not an implementation of the IPPM protocol suite.

[RFC 7679](https://www.rfc-editor.org/rfc/rfc7679.html), a one-way delay metric specification, gives more concrete measurement security considerations: carefully bound added traffic so it is trivial, consider harm to the measurement (including differentiated treatment and injected measurement-like traffic), protect results and measurement controls from reconnaissance, and consider privacy. Its metric reporting guidance also stresses context such as packet type and loss threshold.

## What this simulator does today

This project runs ns-3/5G-LENA simulations and replays generated CSV measurements. The configured UDP traffic and handover activity are simulated inside ns-3; the checked-in flow records capture counters and radio/mobility measurements, not user payload contents. In the project code, the four handover policies and DDQN choose serving gNBs from simulated signal/load/throughput state. They do not classify a live measurement flow as a DoS attack, authenticate measurement sources, encrypt files, anonymize users, or enforce network authorization and rate limits.

Therefore, A3, CHO, SBGH, ideal-SBGH, and DDQN must not be presented as protecting live users from the two threats. They evaluate handover decisions. This simulation can help explore how a handover strategy affects service metrics under configured traffic and mobility, but it does not establish active-measurement safety or passive-data confidentiality.

CSV traces include UE position, system time, RSRP, and traffic-derived metrics. Those fields can be sensitive even without payload capture. The new run reports keep source values and logs for reproducibility; users should protect the trace directory and remove or redact identifying data before sharing it.

## How RFC-oriented requirements could be applied

The current report generator is a useful documentation point for future metric definitions, not a compliance claim. For each metric added to a study, document:

1. Metric name, observed entity, direction, unit, sample interval, and aggregation rule.
2. Traffic type, packet size/rate, measurement duration, topology, mobility and scenario inputs.
3. Loss/timeout handling, unavailable values, clock/calibration assumptions, and known error sources.
4. Active-traffic risks, authorization/scope, rate limits, safe maximum load, and how monitoring distinguishes test traffic from misuse.
5. Passive-data risks, fields collected, whether payload is captured, pseudonymization, retention, access control, and disclosure policy.
6. How measurement control and result files are authenticated, protected from tampering, and restricted against reconnaissance.

For the active-traffic threat, future real-network measurement integration should require explicit target authorization, a bounded packet budget/rate and duration, safe defaults, abort controls, and auditable measurement identity. The simulator's `bitRate`, `packetSize`, and `MaxPackets` settings control simulated traffic only; they are not safeguards for live networks.

For the passive-privacy threat, keep payload collection out of the measurement path where possible, minimize retained identifiers/location precision, define access and expiry for CSV/log/PDF outputs, and protect data at rest and in transit. The current program does not implement these controls.

## Relationship to the five algorithms

| Method | What it decides in this code | Security/privacy protection provided |
|---|---|---|
| 3GPP A3 | Signal-event-based serving-cell handover | None; no threat detection or traffic authorization. |
| 3GPP Rel.16 CHO | Candidate preparation and conditional execution | None; does not mitigate active measurement abuse. |
| SBGH / ideal-SBGH | Greedy cell selection by score | None; scores radio/cell characteristics, not user-data privacy. |
| DDQN | Learned serving-cell action from the current simulation state | None; observation/reward are not security classifiers or privacy controls. |

Possible future research could compare how a selected mobility/handover policy affects service continuity under an authorized, explicitly modelled low-rate test workload, then report the metric and security assumptions. That would be an extension to study design and possibly code; it is not a feature of the current implementation.

## What this project can say in a report

It can report measured simulated throughput, latency-related values, packet loss, handover counters, score outputs, the configured traffic settings, and whether the output files were completed. It should label the results as simulation outputs. It should not claim that an algorithm prevented DoS, protected passive user contents, met an IPPM security requirement, or represents live-network reliability without additional mechanisms and an explicitly validated metric.
