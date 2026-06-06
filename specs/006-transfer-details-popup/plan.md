# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a dynamic UI pop-up in the web application displaying the top N transfers (Player Name, Fee, Associated Club) for any selected node or bar, powered by a new FastAPI endpoint and PySpark backend RDD extraction.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12, HTML/JS/CSS
**Primary Dependencies**: FastAPI, PySpark, D3.js
**Storage**: N/A (In-memory PySpark RDD from `transfers.csv`)
**Testing**: Local script testing
**Target Platform**: Web application (browser + local server)
**Project Type**: Data visualization web application
**Performance Goals**: <500ms response time for API pop-up fetches
**Constraints**: Must strictly leverage PySpark for processing, minimal frontend logic
**Scale/Scope**: Top 10 transfers dynamically queried per click

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[x] Does this rely on MapReduce pattern via PySpark? (Yes, backend PySpark method will be used to generate Top 10 transfers)
[x] Are new endpoints securely returning deterministic artifacts? (Yes)

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
├── app.py
├── core/
│   └── processing.py
├── static/
│   ├── js/
│   │   └── graph.js
│   └── css/
│       └── style.css
└── templates/
    └── index.html
```

**Structure Decision**: Integrated directly into existing source structure. Backend changes in `core/loading` and API routing in `app.py`. Frontend DOM additions in `index.html` with interaction logic inside `js/graph.js`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
