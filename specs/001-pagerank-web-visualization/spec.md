# Feature Specification: PageRank Web Visualization

**Feature Branch**: `001-pagerank-web-visualization`  
**Created**: 2026-03-19  
**Status**: Draft  
**Input**: User description: "I want to create a web page that we will use to run the pagerank algorithm on the dataset and see the graph on the web page I want to have options for filters on the web page to filter wether I want to show the buyers graph or the sellers graph"

## Clarifications

### Session 2026-03-19
- Q: Do you want to simply display the static PNG bar charts or render an interactive node-link network graph via JavaScript? → A: Render an interactive network graph (nodes/links)
- Q: Should the interactive graph display all historical connections or only the top algorithmic results? → A: Limit nodes to the Top "N" clubs and their major transfer connections
- Q: Should algorithm mathematical variables (e.g. Iterations, Damping Factor) be hardcoded or adjustable? → A: Expose algorithm parameters as adjustable UI inputs.
- Q: What should happen when a user clicks on a bar in the new Bar Chart view? → A: Show the same detailed overlay as the network graph.
- Q: Which visualization type should be selected as the default when the page first loads? → A: Bar Chart.


## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Buyer/Seller PageRank (Priority: P1)

As a user, I want to access a web interface where I can trigger the PageRank algorithm and view the resulting graph focusing on either buyers or sellers, so that I can easily analyze the top transfer nodes without needing to run scripts manually.

**Why this priority**: It fulfills the primary goal of providing a user-friendly graphical interface for algorithm analysis.

**Independent Test**: Can be fully tested by launching the web page, selecting the "Buyers" filter, clicking run, and verifying that the buyers graph visualization appears on the screen.

**Acceptance Scenarios**:

1. **Given** I am on the web application dashboard, **When** I trigger the PageRank algorithm with the "Buyers" filter selected, **Then** the application processes the dataset and displays the Attractors (Buyers) visualization graph.
2. **Given** the visualization result is displayed, **When** I toggle the filter to "Sellers" and click run, **Then** the application processes the dataset and displays the Suppliers (Sellers) visualization graph.
3. **Given** a generated graph, **When** I toggle the visualization type from "Network Graph" to "Bar Chart", **Then** the application displays the rank data as a bar chart instead of a node-link graph.
4. **Given** the Network Graph visualization is displayed, **Then** I must see the computed rank explicitly written beneath each team's name, and the nodes must be large enough to easily read.

### Edge Cases

- What happens when the dataset `transfers.csv` is missing or corrupted when triggering the algorithm?
- How does the system handle concurrent users triggering heavy algorithm computations simultaneously?
- What happens if the visualization graph generation fails?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a web user interface accessible via a browser.
- **FR-002**: System MUST include a control section with filter options for "Buyers Graph" (Attractors) and "Sellers Graph" (Suppliers).
- **FR-003**: System MUST provide a mechanism (e.g., a "Run" button) to trigger the PageRank calculation based on the selected filter.
- **FR-004**: System MUST render an interactive node-link network graph visualization dynamically on the web page leveraging the post-processing datasets rather than displaying static images.
- **FR-005**: System MUST display a loading state or indicator while the algorithm is running.
- **FR-006**: System MUST filter and limit the interactive graph visualization to only the top-ranked nodes (e.g., Top 10 or Top 20) and their prominent transfer edges to ensure browser performance and legibility.
- **FR-007**: System MUST provide input controls allowing users to adjust core PageRank parameters (such as Iterations and Damping Factor) dynamically before running the computation.
- **FR-008**: System MUST explicitly display the node's computed rank directly beneath the team name (node label) within the network graph visualization.
- **FR-009**: System MUST provide a visualization type toggle allowing the user to switch between rendering the data as a "Node-Link Network Graph" and a "Bar Chart". The bar chart must be fully interactive, where clicking a bar displays the same detailed dataset overlay as clicking a node in the network graph. The system MUST render the Bar Chart as the default visualization when the page first loads or a computation runs.
- **FR-010**: System MUST render network graph nodes at a deliberately larger base size to ensure that team names and their accompanying rank labels are clearly legible without requiring excessive zooming.

### Key Entities *(include if feature involves data)*

- **Algorithm Computation Request**: Represents the user's selected parameters (filter: Buyer or Seller, plus runtime algorithm configurations like iterative duration and variables) to process the dataset.
- **Visualization Result**: Represents the output generated by the calculation, which is rendered graphically on the page.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully view and interact with either the buyers or sellers network graph within the web interface after selecting the filter.
- **SC-002**: The application clearly indicates processing status while waiting for the algorithm to complete.
- **SC-003**: A user can complete the entire process of running the algorithm and seeing results without interacting with a CLI or code.
- **SC-004**: Time to trigger and visualize is strictly dependent on algorithm duration without web overhead delays.
