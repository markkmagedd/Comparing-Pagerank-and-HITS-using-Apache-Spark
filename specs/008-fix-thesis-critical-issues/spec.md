# Feature Specification: fix-thesis-critical-issues

**Feature Branch**: `008-fix-thesis-critical-issues`  
**Created**: 2026-06-06  
**Status**: Draft  
**Input**: User description: "context Critical Issues Must Fix Zero figures screenshots in the entire thesis the Figures folder only has the GUC logo. No application screenshots no architecture diagrams no result tables. Results chapter is entirely narrative no actual ranking data tables or computed metrics. The FC Barcelona case study has good numbers but they are buried in prose instead of tables. Placeholder text left in Figure references may be added later in Methodology and DAY MONTH 2019 in the submission info."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Replace placeholder images with actual UI screenshots (Priority: P1)

As a reviewer, I want to see actual application screenshots in the Figures folder rather than placeholders, so that I can evaluate the Transfer Analyzer interface.

**Why this priority**: Without real screenshots, the thesis lacks visual evidence of the implemented system, which is a critical missing component.

**Independent Test**: Can be tested by checking the Figures directory and ensuring ui_barchart.png, ui_compare.png, ui_flow.png, ui_historical.png, and ui_network.png display real application mockups instead of the GUC logo.

**Acceptance Scenarios**:

1. **Given** the thesis latex files, **When** the document is compiled, **Then** actual UI screenshots appear in the visualization chapter.

---

### User Story 2 - Convert narrative results to formatted tables (Priority: P1)

As a reviewer, I want to see ranking data and metrics formatted as tables in the Results chapter, so that I can easily compare PageRank and HITS scores.

**Why this priority**: Narrative results are difficult to parse and reduce the academic quality of the presentation.

**Independent Test**: Can be tested by reviewing the Results chapter to ensure Top-10 lists and the FC Barcelona case study are presented in properly formatted LaTeX tables.

**Acceptance Scenarios**:

1. **Given** the Results chapter, **When** reviewing the FC Barcelona case study, **Then** a table summarizes the ranking across seasons.

---

### User Story 3 - Remove placeholder text (Priority: P2)

As a reader, I want to see finalized submission dates and correct figure references, so that the thesis appears polished and complete.

**Why this priority**: Placeholder text makes the document look unfinished.

**Independent Test**: Can be tested by searching the codebase for "DAY/MONTH/2019" and "Figure references may be added later" and ensuring they yield no results.

**Acceptance Scenarios**:

1. **Given** the Methodology chapter, **When** reading the text, **Then** all figure references are complete.
2. **Given** the submission info, **When** checking the title/authors page, **Then** the submission date is correctly populated.

### Edge Cases

- What happens if the actual UI is not available to screenshot? System should use high-fidelity UI mockups generated to match the descriptions.
- How does the system handle table formatting for long club names? Tables must use standard width constraints or proper column alignment.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide high-quality UI mockups for barchart, network, flow, compare, and historical views.
- **FR-002**: System MUST structure ranking outputs and case study metrics into formal LaTeX tables in results.tex.
- **FR-003**: System MUST remove any instance of placeholder text (e.g., "Figure references may be added later").
- **FR-004**: System MUST update the submission date placeholder to a final date.

### Key Entities

- **UI Mockups**: Visual representations of the Transfer Analyzer application views.
- **LaTeX Tables**: Structured data formats for presenting PageRank and HITS scores.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of placeholder images in the Figures directory (excluding actual logos) are replaced with application mockups.
- **SC-002**: 100% of narrative ranking lists in the Results chapter are converted to LaTeX tables.
- **SC-003**: 0 instances of placeholder text remain in the source files.
