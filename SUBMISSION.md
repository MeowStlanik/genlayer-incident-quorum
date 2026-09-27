# IncidentQuorum — standalone Intelligent Contract

**Category:** Intelligent Contracts

**Purpose:** A closed-day service incident attestation oracle using three fixed evidence sources. It derives corroborated full minutes from overlapping reports and preserves uncertainty instead of inventing uptime.

**Why consensus matters:** Every participant independently GETs all three sources and uses one inference per source. Each finding is OUTAGE, HEALTHY or UNKNOWN. An outage requires a resolved interval, identifiable service, date and timezone. Only one continuous interval per source/day is supported. Leader and validator must match source content hashes, statuses and exact integer minute boundaries; they may use different true quotes. The contract then counts each minute covered by at least two OUTAGE intervals exactly once. A proved threshold gives OUTAGE; less evidence gives UNKNOWN. Two full-day HEALTHY attestations with no OUTAGE give NO_OUTAGE. Any HEALTHY/OUTAGE contradiction gives DISPUTED.

**State design:** The deployer registers immutable service definitions with three exact HTTPS URLs on different hostnames, a description and a 1–1,440 minute threshold. `attempts[service:UTC-day]` caps observations at three. `receipts[service:UTC-day:attempt]` preserves findings, URL list, exact page content hashes, threshold and corroborated minutes. No configuration mutation or payout exists.

**Reusable beyond a demo:** Conventional SLA/parametric contracts often rely on a single structured feed. Incident reports are frequently unstructured prose with different service names and time descriptions. GenLayer validators can independently fetch and interpret those reports while deterministic interval logic controls the eventual attestation.

**Source:** `contract.py` (self-contained; zero-argument constructor).

**Review materials:** project README, ABI schema, `tests/test_contract.py` and `VALIDATION.md`.

**Deployment evidence:** after publication, use this repository’s `deployment.json`. It proves an observed matching transaction, not final success. Add the actual repository URL, successful deployment address and live invocation transaction IDs when submitting. Those values are intentionally not fabricated in this draft.

**Current verification scope:** local logic tests and Bradbury schema loading. Live AI consensus and production audit remain outstanding. Use small archived plain-text reports: pages larger than 12,000 characters are rejected, not truncated. Exact page-hash equivalence deliberately rejects content drift; dynamic dashboards may never reach agreement. A green current status or missing incident is not full-day health evidence. Different hostnames do not guarantee organizational independence; source selection remains a trust boundary. Redirect/DNS handling follows GenVM’s web implementation. No recurring scheduler is embedded; anyone may submit observations. For new report URLs or corrected determinate findings, use a separately identified service policy and make the change visible. Arbitrarily fragmented incidents require a future interval-list version.
