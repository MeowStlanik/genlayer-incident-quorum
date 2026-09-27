# IncidentQuorum

A closed-day service incident attestation oracle using three fixed evidence sources. It derives corroborated full minutes from overlapping reports and preserves uncertainty instead of inventing uptime.

## Why GenLayer

Conventional SLA/parametric contracts often rely on a single structured feed. Incident reports are frequently unstructured prose with different service names and time descriptions. GenLayer validators can independently fetch and interpret those reports while deterministic interval logic controls the eventual attestation.

## State and authority

The deployer registers immutable service definitions with three exact HTTPS URLs on different hostnames, a description and a 1–1,440 minute threshold. `attempts[service:UTC-day]` caps observations at three. `receipts[service:UTC-day:attempt]` preserves findings, URL list, exact page content hashes, threshold and corroborated minutes. No configuration mutation or payout exists.

## Lifecycle

`register → observe closed UTC day → OUTAGE | NO_OUTAGE | UNKNOWN | DISPUTED`. Only UNKNOWN/DISPUTED can be observed again, at most three attempts. Determinate outcomes are immutable. HTTP/source errors and network consensus rejection commit nothing and do not consume an application attempt.

## Consensus and equivalence

Every participant independently GETs all three sources and uses one inference per source. Each finding is OUTAGE, HEALTHY or UNKNOWN. An outage requires a resolved interval, identifiable service, date and timezone. Only one continuous interval per source/day is supported. Leader and validator must match source content hashes, statuses and exact integer minute boundaries; they may use different true quotes. The contract then counts each minute covered by at least two OUTAGE intervals exactly once. A proved threshold gives OUTAGE; less evidence gives UNKNOWN. Two full-day HEALTHY attestations with no OUTAGE give NO_OUTAGE. Any HEALTHY/OUTAGE contradiction gives DISPUTED.

Malformed outputs, invented citations, incomplete arrays or disagreement are rejected. Each accepted receipt records the leader's validated evidence; independently produced validator explanations are not stored. The decision equivalence is substantive, not a JSON-format check.

## Public API

Constructor: no arguments. Source: [contract.py](contract.py). RPC-checked ABI: [schema.json](schema.json).

| Method | Caller | Meaning |
| --- | --- | --- |
| `register(service_id, description, sources_json, threshold_minutes)` | Owner | Freeze a three-source service policy |
| `observe(service_id, utc_day)` | Anyone | Fetch and attest a closed `YYYY-MM-DD` UTC day |
| `get_service(service_id)` | Read | Immutable sources/threshold |
| `get_receipt(service_id, utc_day, attempt)` | Read | Exact historical observation |
| `latest_attempt(service_id, utc_day)` | Read | Last committed observation number |

## Example walkthrough

1. Select three stable, publicly accessible archived reports on different hosts. Each report must contain the named service, exact date/timezone, resolved interval or an explicit all-day healthy statement. Use actual report URLs, not the illustrative domains below.
2. `register("merchant-api", "Merchant API production REST endpoint", sources_json, 30)` where `sources_json` is a JSON array of the three HTTPS URLs.
3. After the UTC day closes, call `observe("merchant-api", "2025-01-01")`.
4. Example evidence: source A says 01:00–02:00 UTC, source B says 01:20–02:10 UTC, source C says UNKNOWN. The contract counts 40 corroborated minutes, not 110; threshold 30 gives OUTAGE.
5. At threshold 50 the same evidence gives UNKNOWN, because the remaining outage duration is unproven. It does not claim the service satisfied its SLA.
6. If source C explicitly claims the entire day was healthy, the result is DISPUTED and can be observed again within the attempt budget.

Each write is a separate transaction. For this walkthrough, wait for the successful state needed by the next call. The batch deploy script skips AI confirmation only because these four constructors are independent.

## Tests and review

Run `python -m unittest discover -s tests -p 'test_*.py' -v` from this repository root. Tests load this exact source through a small fake GenVM adapter and exercise role checks, history/immutability, malicious model outputs and independent disagreement. They are logic tests, not live model consensus tests. See [VALIDATION.md](VALIDATION.md).

## Limitations

Use small archived plain-text reports: pages larger than 12,000 characters are rejected, not truncated. Exact page-hash equivalence deliberately rejects content drift; dynamic dashboards may never reach agreement. A green current status or missing incident is not full-day health evidence. Different hostnames do not guarantee organizational independence; source selection remains a trust boundary. Redirect/DNS handling follows GenVM’s web implementation. No recurring scheduler is embedded; anyone may submit observations. For new report URLs or corrected determinate findings, use a separately identified service policy and make the change visible. Arbitrarily fragmented incidents require a future interval-list version.

## Deployment and integration

Deploy this file independently, with zero constructor arguments and full consensus (`leaderOnly: false`). The repository contains the contract, English documentation and tests only. Deployment tooling is maintained separately. After publication, `deployment.json` records this contract's observed Bradbury transaction. Transaction existence does not prove successful execution or finality. Consumers should read finalized successful receipts and bind them to this contract address and their own business rules.

Category: **Intelligent Contracts**. Suggested submission text: [SUBMISSION.md](SUBMISSION.md). MIT license.
