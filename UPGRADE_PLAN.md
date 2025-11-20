## Mobilise Upgrade Plan

### Goals
- Transform Mobilise into a comprehensive testing platform covering UI, API, and hybrid flows.
- Add manual recording to complement auto-generated suites.
- Improve execution reliability, reporting depth, and collaboration readiness.

### Workstreams

#### 1. Recording & Script Editing
- Add a recording controller that launches Chrome via CDP in “record” mode.
- Stream captured interactions (clicks, inputs, navigation) to Flask using WebSocket/REST.
- Store steps in a structured format (action, locator, value, assertions, waits).
- Frontend additions:
  - Start/stop recording buttons, live step list, editable fields, reorder/delete options.
  - Code preview (Python/Playwright) with copy/download.
- Persist recordings as reusable test cases that hook into the existing executor.

#### 2. API Testing Module
- Introduce `SmartApiEngine` for test generation:
  - Manual endpoint definitions and OpenAPI imports.
  - Auto-generate positive/negative/security/performance checks.
- Build `ApiTestExecutor` to run cases via `httpx/requests`, validate schemas, timing, headers.
- Extend REST API and UI with API-specific tabs, report cards, and downloads.

#### 3. Expanded UI Test Generation
- Refactor detectors into modular analyzers (forms, tables, navigation graph).
- Add constraint-based data generation (patterns, min/max, types).
- Support multi-step journeys, role variations, accessibility checks, and malicious payload coverage.
- Introduce prioritization metadata (smoke/regression/exhaustive) and grouping.

#### 4. Execution Pipeline Enhancements
- Parallelize runs per category using worker pools.
- Implement smart retries, adaptive waits, and resilience hooks (network throttle, screenshot on each failure).
- Enrich artifacts (console logs, HAR files, DOM snapshots).
- Add CLI flags and scheduler hooks for batch execution.

#### 5. Reporting & Observability
- Persist run history (SQLite/Postgres) for dashboards and trend charts.
- Create report viewer with filters, failure clustering, flaky detection.
- Provide export formats (JSON, Excel, PDF) and integrations (Slack/webhooks).
- Track API + UI metrics in unified summaries.

#### 6. Collaboration Foundations
- User/project management, environment configs, secrets vault.
- Plugin API for custom assertions and data sources.
- Notification channels and CI-friendly REST endpoints.

### Next Steps
1. Implement recording backend/frontend flow.
2. Build API testing engine + executor.
3. Expand UI generation heuristics.
4. Upgrade executor robustness and artifact capture.
5. Deliver run history UI and notification hooks.





