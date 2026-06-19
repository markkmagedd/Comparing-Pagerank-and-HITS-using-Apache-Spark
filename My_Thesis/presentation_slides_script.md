# Thesis Defense Presentation Script & Slides Outline (Canva Template Mapped)

**Title:** Comparing PageRank and HITS using Apache Spark: A Network Analysis of the Global Football Transfer Market  
**Presenter:** Mark Maged Samir  
**Supervisor:** Dr. Islam A. El-Maddah  
**Target Duration:** 30 Minutes (23 Slides)  
**Theme:** Dark-mode tech theme (Background: `#0B0E14`, Accent: `#4361EE`, Secondary Panels: `#1A1D27`, Text: `#FFFFFF` / `#9CA3AF`)

---

## Slide 1: Title Slide (0:00 - 1:00)
* **Canva Template Page:** **Page 1 (Title Slide)**
* **Visual Setup:** 
  * Background: Deep Dark Navy (`#0B0E14`)
  * Left: Large title text. A purple/indigo capsule reading "A Network Analysis of the Global Football Transfer Market".
  * Right: Glowing network node Spark logo.
  * Bottom Right: Presenter and Supervisor details.
* **Slide Content:**
  * **Title:** Comparing PageRank and HITS using Apache Spark
  * **Presenter:** Presented by: Mark Maged Samir
  * **Supervisor:** Supervised by: Dr. Islam A. El-Maddah
* **Speaker Script:**
  > "Good afternoon, members of the committee, Dr. Islam, and colleagues. Welcome to my bachelor's thesis defense presentation: 'Comparing PageRank and HITS using Apache Spark: A Network Analysis of the Global Football Transfer Market'. 
  > Today, I will walk you through the theoretical background of PageRank and HITS, my distributed PySpark implementation, the interactive Transfer Analyzer application I built, and the empirical results of my comparative analysis."
* **Timing:** 1.0 minute

---

### Slide 2: Introduction & Motivation (1:00 - 2:00)
* **Canva Template Page:** **Page 3 (Introduction & Motivation)**
* **Visual Setup:**
  * Left: Title and bullet points.
  * Right: Glowing network sphere graphic.
* **Slide Content (Bullet Points on Slide):**
  * The web is a graph. Hyperlinks are votes. PageRank and HITS turn those votes into rankings.
  * These algorithms power Google Search, recommendation systems, and fraud detection.
  * Can they also reveal hidden structure in a completely different domain — professional football?
  * This thesis uses the global transfer market as a testbed to compare them at scale using Apache Spark.
* **Speaker Script:**
  > "When Larry Page and Jon Kleinberg introduced PageRank and HITS in the late 1990s, they changed how we understand networks. Instead of looking at content alone, they looked at connections — who links to whom, and what that says about importance.
  >
  > These algorithms are everywhere today. Google Search, YouTube recommendations, even fraud detection. But they've mostly been studied on web data.
  >
  > So the question I asked was: can these same algorithms reveal something meaningful about a completely different kind of network — the global football transfer market? And how do they compare when running on the same data, at the same time, under identical conditions? That's exactly what this thesis explores."
* **Timing:** 1.0 minute

---

## Slide 3: Gaps & Problem Statement (2:00 - 3:15)
* **Canva Template Page:** **Page 4 (The Global Football Transfer Market Layout - Page 4 of your PDF)**
* **Visual Setup:**
  * Left: Title ("Problem Statement") and bullet points.
  * Right: Global transfer connection map graphic.
* **Slide Content:**
  * **Algorithmic Isolation:** Existing comparative literature evaluates PageRank and HITS on disjoint datasets, preventing direct side-by-side behavioral control.
  * **Web-Graph Bias:** Research is heavily biased toward web graphs or synthetic networks, leaving weighted financial networks under-explored.
  * **Lack of Multi-Modal Interaction:** Scarcity of unified tools combining execution with multiple visualizations (ranked lists, network topologies, chord flows).
* **Speaker Script:**
  > "This brings us to the core problem statement. Despite the extensive individual study of both PageRank and HITS, three major gaps persist in the literature. 
  > 
  > First, there is a lack of unified comparative environments where both algorithms can be executed on the same dataset under identical parameter constraints. Second, existing comparative studies are heavily biased toward web-crawls or synthetic scale-free networks. We do not fully understand how global, query-independent rankings and local, dual-score decompositions differ on non-web, weighted networks like the transfer market. Finally, there is a lack of interactive systems that allow researchers to adjust parameters in real-time and observe the immediate effects on both ranked tables and network visualizations. My thesis addresses these three limitations."
* **Timing:** 1.25 minutes

---

## Slide 4: Research Questions (3:15 - 4:30)
* **Canva Template Page:** **Page 4 (What is a Data Analyst? Checklist Layout)**
* **Visual Setup:**
  * Left: Title and introduction of Research Questions.
  * Right: Checklist clipboard with clock graphic.
* **Slide Content:**
  * **[x] RQ1 (Theoretical):** What are the mathematical, computational, and security distinctions between PageRank and HITS?
  * **[x] RQ2 (Computational):** How can both algorithms be implemented within a single PySpark pipeline for weighted directed graphs?
  * **[x] RQ3 (Domain-Specific):** What structural insights do they reveal about the transfer network, and how do filters and weight settings alter output rankings?
* **Speaker Script:**
  > "My work is guided by three research questions. 
  > RQ1 covers the theoretical and mathematical differences in convergence, complexity, and spam vulnerability. 
  > RQ2 addresses the distributed implementation: how to model transfers as a graph and execute the algorithms in parallel using PySpark. 
  > And RQ3 focuses on the sports economics domain: what structural insights do we obtain, and how do variables like transfer fees versus transfer count alter the resulting ranks?"
* **Timing:** 1.25 minutes

---

## Slide 5: Thesis Objectives (4:30 - 5:30)
* **Canva Template Page:** **Page 5 (Required Skills Pill Layout)**
* **Visual Setup:**
  * Title: "Thesis Objectives"
  * 5 rounded purple pills containing the 5 main objectives:
    1. Theoretical Synthesis
    2. Comparative Analysis
    3. PySpark Implementation
    4. Transfer Analyzer App
    5. Case Studies
* **Slide Content:**
  * **1. Theoretical:** Exposition of eigenvectors, Markov chains, SVD, and convergence limits.
  * **2. Comparative:** Contrasting scope (global vs. local) and score semantics.
  * **3. Parallelization:** Constructing distributed RDD graph representations.
  * **4. Full-Stack:** Delivering interactive visualizations (D3.js, Cytoscape.js).
  * **5. Application:** Performing a longitudinal case study on FC Barcelona.
* **Speaker Script:**
  > "To answer my research questions, I set five key objectives. 
  > First, provide a clean theoretical synthesis of the algorithms' mathematics. 
  > Second, design a comparative framework. 
  > Third, build the PySpark distributed pipeline. 
  > Fourth, wrap the pipeline in a full-stack interactive web application, the Transfer Analyzer. 
  > And fifth, validate the system using an empirical case study on FC Barcelona's historical transfer behavior."
* **Timing:** 1.0 minute

---

## Slide 6: Theoretical Background: The Web Graph (5:30 - 6:45)
* **Canva Template Page:** **Page 7 (Work Process Layout)**
* **Visual Setup:**
  * Left: Two overlapping gears graphic (representing graph structure and links).
  * Right: Graph notations and equations.
* **Slide Content:**
  * **Graph Representation:** Directed Graph $G = (V, E)$
    * $V = \{v_1, v_2, \dots, v_N\}$ (Nodes / Webpages / Clubs)
    * $E \subseteq V \times V$ (Directed Edges / Hyperlinks / Transfers)
  * **In-degree and Out-degree:**
    * In-degree: $\deg^{-}(v) = |B(v)|$ where $B(v) = \{u \in V : (u,v) \in E\}$ (Predecessors)
    * Out-degree: $\deg^{+}(v) = |F(v)|$ where $F(v) = \{w \in V : (v,w) \in E\}$ (Successors)
  * **Link Semantics:** Directional endorsement conveying structural status.
* **Speaker Script:**
  > "Before looking at the transfer graph, let's outline the theoretical foundations of graph theory. The web is modeled as a directed graph $G = (V,E)$ where pages are nodes and hyperlinks are directed edges. 
  > We define the predecessors, $B(v)$, which determine the node's in-degree, and the successors, $F(v)$, which determine its out-degree. In link analysis, an edge from node $u$ to node $v$ represents an endorsement, transferring structural prestige or importance to the destination page."
* **Timing:** 1.25 minutes

---

## Slide 7: PageRank: Random Surfer & Google Matrix (6:45 - 8:15)
* **Canva Template Page:** **Page 2 (What is a Data Analyst? Layout)**
* **Visual Setup:**
  * Left: Damped PageRank equation and matrix notation.
  * Right: Bar chart with magnifying glass graphic (representing PageRank scoring).
* **Slide Content:**
  * **Damped PageRank Equation:**
    $$PR(v) = \frac{1-d}{N} + d \sum_{u \in B(v)} \frac{PR(u)}{L(u)}$$
    * $d$: Damping factor (typically 0.85).
    * $L(u)$: Out-degree of node $u$.
  * **Matrix Notation & Google Matrix:**
    $$\mathbf{G} = d\,\mathbf{M} + \frac{1-d}{N}\,\mathbf{1}\mathbf{1}^{T}$$
    * $\mathbf{M}$: Transition probability matrix ($M_{ij} = 1/L(j)$).
    * $\boldsymbol{\pi} = \mathbf{G}\boldsymbol{\pi}$ (Principal eigenvector corresponding to eigenvalue $\lambda = 1$).
  * **Guaranteed Convergence:** By Perron-Frobenius theorem, $\mathbf{G}$ is positive, primitive, and irreducible, ensuring a unique stationary distribution.
* **Speaker Script:**
  > "PageRank, introduced by Sergey Brin and Larry Page, simulates a user randomly browsing the web. 
  > As shown in the equation on the left, it combines two behaviors. With probability $d$, the surfer follows out-links, sharing the node's rank divided by its out-degree $L(u)$. With probability $1-d$, the surfer teleports to a random page. 
  > In matrix notation, this gives us the Google Matrix $\mathbf{G}$. The teleportation component ensures the matrix is positive, primitive, and irreducible, which by the Perron-Frobenius theorem guarantees that the power iteration method will converge to a unique principal eigenvector."
* **Timing:** 1.5 minutes

---

## Slide 8: PageRank: Convergence & Limitations (8:15 - 9:30)
* **Canva Template Page:** **Page 8 (Data Collection Quad Layout)**
* **Visual Setup:**
  * Top Center: Title.
  * Four blocks representing the four main limitations of PageRank:
    * Top Left: Uniform Teleportation (ignores personalized interest)
    * Bottom Left: Equal Link Weighting (ignores edge strength)
    * Top Right: Vulnerability to Manipulation (link farms)
    * Bottom Right: Bias Against New Nodes (accumulated age advantage)
* **Slide Content:**
  * **Power Iteration Complexity:** $O(k \times (N + E))$ where $k$ is the number of iterations.
  * **Empirical Convergence:** Stable stationary distribution within $10$--$15$ iterations on our transfer graph ($L_2$-norm difference $\|\boldsymbol{\pi}^{(k)} - \boldsymbol{\pi}^{(k-1)}\|_2 \rightarrow 0$).
  * **Key Limitations:** Uniform teleportation, equal link division, spam vulnerability, and age bias.
* **Speaker Script:**
  > "Computationally, PageRank is highly scalable. The time complexity is linear with respect to nodes and edges. On our professional football transfer network, we observe strong convergence within 10 to 15 iterations. 
  > However, classical PageRank has four core limitations. It assumes teleportation is uniform, it divides rank equally across out-links, it is vulnerable to link farms, and it biases against new nodes. For our football domain, the equal link-weighting is especially problematic because transfer relationships are financially unequal."
* **Timing:** 1.25 minutes

---

## Slide 9: HITS: Hubs & Authorities Duality (9:30 - 10:45)
* **Canva Template Page:** **Page 3 (The Role of a Data Analyst Layout)**
* **Visual Setup:**
  * Left: Vertical bar chart and gear graphic (representing SVD/eigenvector calculations).
  * Right: Definitions of Hubs and Authorities.
* **Slide Content:**
  * **Hyperlink-Induced Topic Search (HITS):** Developed by Jon Kleinberg (1999).
  * **Dual Node Roles:**
    * **Authority ($a$):** Node containing high-quality, primary information. A good authority is linked to by many good hubs.
    * **Hub ($h$):** Node pointing to high-quality directories. A good hub links to many good authorities.
  * **Mutually Reinforcing Relationship:** Authority scores depend on incoming hubs, and hub scores depend on outgoing authorities.
* **Speaker Script:**
  > "In 1999, Jon Kleinberg proposed HITS, taking a different approach. HITS recognizes that web pages serve two distinct semantic functions. 
  > Authorities contain primary information, and Hubs serve as high-quality index directories pointing to authorities. 
  > This creates a mutually reinforcing relationship: a node's authority score is high if it is linked to by nodes with high hub scores, and its hub score is high if it points to nodes with high authority scores. This results in a dual-score model."
* **Timing:** 1.25 minutes

---

## Slide 10: HITS: Mathematical & Matrix Formulation (10:45 - 12:15)
* **Canva Template Page:** **Page 8 (Data Collection Quad Layout)**
* **Visual Setup:**
  * Four blocks representing the four elements of HITS math:
    * Top Left: Update Equations ($a(v) = \sum h(u)$ and $h(v) = \sum a(w)$)
    * Bottom Left: Normalization Rule (prevents scores from growing to infinity)
    * Top Right: Authority Matrix Eigenvector ($\mathbf{A}^T\mathbf{A}$)
    * Bottom Right: Hub Matrix Eigenvector ($\mathbf{A}\mathbf{A}^T$)
* **Slide Content:**
  * **Iterative Update Rules:**
    $$a(v) = \sum_{u \in B(v)} h(u) \qquad h(v) = \sum_{w \in F(v)} a(w)$$
  * **Matrix Eigenvectors:**
    $$\mathbf{a}^{(k+1)} = \mathbf{A}^{T}\mathbf{A}\,\mathbf{a}^{(k)} \qquad \mathbf{h}^{(k+1)} = \mathbf{A}\mathbf{A}^{T}\,\mathbf{h}^{(k)}$$
    * $\mathbf{a}$ converges to the principal eigenvector of $\mathbf{A}^{T}\mathbf{A}$.
    * $\mathbf{h}$ converges to the principal eigenvector of $\mathbf{A}\mathbf{A}^{T}$.
* **Speaker Script:**
  > "Slide 10 details the mathematics. The iterative authority update is the sum of incoming hub scores, and the hub update is the sum of outgoing authority scores. 
  > In matrix notation, this means that the authority vector converges to the principal eigenvector of $\mathbf{A}^T\mathbf{A}$, while the hub vector converges to the principal eigenvector of $\mathbf{A}\mathbf{A}^T$. 
  > This mathematically links HITS to Singular Value Decomposition, representing the left and right singular vectors. Since scores add up continuously, a normalization step is performed at the end of each iteration to keep values stable."
* **Timing:** 1.5 minutes

---

## Slide 11: Algorithmic Comparison: PageRank vs. HITS (12:15 - 13:30)
* **Canva Template Page:** **Page 6 (Tools Used 3-Card Layout)**
* **Visual Setup:**
  * Three vertical slate cards with white borders comparing PageRank and HITS on:
    * Card 1: Execution & Scope (Global offline vs. local query-dependent)
    * Card 2: Score Semantics (Single global rank vs. dual hub-authority scores)
    * Card 3: Math Engine (Markov Chain/Google Matrix vs. SVD/Eigenvector)
* **Slide Content:**
  * **Execution:** PageRank operates globally on the entire graph. HITS operates locally on a query-induced subgraph.
  * **Scores:** PageRank assigns one score. HITS assigns two separate scores.
  * **Math:** PageRank uses random walks with teleportation. HITS uses SVD matrix factorization.
* **Speaker Script:**
  > "Before showing my implementation, let's contrast the two models. 
  > Card 1 shows execution differences: PageRank runs offline on the global graph, whereas HITS typically runs online on a query-specific subgraph. 
  > Card 2 shows score semantics: PageRank computes one importance score, while HITS computes two. 
  > Card 3 shows the mathematical engines: PageRank solves a Markov chain stationary distribution, while HITS uses SVD on the adjacency matrix. This comparison guides how we apply them to football transfers."
* **Timing:** 1.25 minutes

---

## Slide 12: Methodology: Graph & Transfer Market Formulation (13:30 - 14:45)
* **Canva Template Page:** **Page 7 (Work Process Layout)**
* **Visual Setup:**
  * Left: Gears graphic representing the transfer network modeling.
  * Right: Graph equations and transfer mappings.
* **Slide Content:**
  * **Graph Model:** $G = (V, E, W)$
    * $V$: Football Clubs (Nodes)
    * $E$: Directed edges pointing from Seller to Buyer.
    * $W$: Edge Weight (monetary fee or transaction count).
  * **Edge Direction Rationale:** **Selling Club $\rightarrow$ Buying Club**
    * Retains the economic flow: talent and financial assets move from source to destination.
  * **Weighting Modes ($W$):**
    * *Fee-weighted:* $W(u,v) = \sum f_k$ (Sum of transfer fees)
    * *Count-weighted:* $W(u,v) = m$ (Total count of transfers)
* **Speaker Script:**
  > "Now, how do we model the professional football transfer market as a graph? 
  > We define a weighted directed graph $G=(V,E,W)$, where clubs are nodes. 
  > I set the edge direction from the Selling Club to the Buying Club, preserving the economic flow of talent and asset value. 
  > I implemented two weighting modes: Fee-weighted mode, aggregating all transfer fees between two clubs, and Count-weighted mode, counting the number of transfers. This isolates a club's financial market power from its sheer transactional frequency."
* **Timing:** 1.25 minutes

---

## Slide 13: Methodology: PySpark Processing Pipeline (14:45 - 15:45)
* **Canva Template Page:** **Page 4 (What is a Data Analyst? Checklist Layout)**
* **Visual Setup:**
  * Left: Title and description of PySpark's role.
  * Right: Clipboard checklist showing the 5 pipeline stages.
* **Slide Content:**
  * **[x] Stage 1: Data Ingestion:** Caching raw player transfers from CSV into Spark memory.
  * **[x] Stage 2: Preprocessing:** Normalizing names and mapping missing values to fallbacks.
  * **[x] Stage 3: Subgraph Filtering:** Dynamic filtering by league and season.
  * **[x] Stage 4: Algorithmic Execution:** Iterative RDD execution (PageRank and HITS).
  * **[x] Stage 5: Delivery & REST API:** Extracting top-$N$ rankings for the web interface.
* **Speaker Script:**
  > "To compute these metrics, I built a distributed pipeline in PySpark. 
  > As shown on the clipboard, it has five stages. First, ingestion, loading the CSV. Next, preprocessing, cleaning club names and converting transfer fees. 
  > Third, filtering the dataset dynamically to construct a specific subgraph. 
  > Fourth, execution, running the iterative algorithm on Spark RDDs. Because both algorithms are highly iterative, keeping graph structures in Spark's memory prevents repeated read-write overhead. Finally, delivery, exposing results via FastAPI."
* **Timing:** 1.0 minute

---

## Slide 14: System Architecture: The Transfer Analyzer (15:45 - 17:00)
* **Canva Template Page:** **Page 6 (Tools Used 3-Card Layout)**
* **Visual Setup:**
  * Three vertical cards with white borders showing the layered system design:
    * Card 1: Data Layer (cached CSV records)
    * Card 2: Processing Layer (PySpark distributed RDD execution engine)
    * Card 3: Service & Presentation Layers (FastAPI backend, browser dashboard)
* **Slide Content:**
  * **Data Layer:** Raw player transfers cached in memory.
  * **Processing Layer:** PySpark RDD transformations and broadcast variables for optimized graph traversals.
  * **Service & Presentation:** FastAPI REST endpoints delivering structured JSON to Chart.js, Cytoscape.js, and D3.js frontend components.
* **Speaker Script:**
  > "The Transfer Analyzer system uses a layered architecture, shown across these cards. 
  > Card 1 is the Data Layer. Card 2 is the Processing Layer, where the PySpark engine runs. 
  > Card 3 represents the Service and Presentation Layers, utilizing FastAPI for the API and rendering interactive views in the browser. This modular design isolates the PySpark graph engine from the user interface."
* **Timing:** 1.25 minutes

---

## Slide 15: App Demo: Interactive Visualizations (17:00 - 18:30)
* **Canva Template Page:** **Page 11 (Data Visualization Layout)**
* **Visual Setup:**
  * Left: Column bar chart graphic representing visual analytics.
  * Right: Description of the D3.js and Cytoscape.js visual components.
* **Slide Content:**
  * **Network Graph View (Cytoscape.js):**
    * Force-directed link layouts displaying player flows.
    * Nodes dynamically sized by calculated PageRank or HITS scores.
  * **League Flow Chord Diagram (D3.js):**
    * Circular visualization showing macro-level transfers between leagues.
    * Ribbons encode financial volume; interactive hovers isolate corridors.
* **Speaker Script:**
  > "Now, we begin the app walkthrough, highlighting the visualization modules. 
  > First, the network graph view uses Cytoscape.js to show actual transfer links between clubs. We size nodes based on their scores, highlighting central market attractors. 
  > For macro-level patterns, the system renders an interactive D3.js Chord Diagram. This aggregates transfers at the league level. The width of each ribbon represents the financial volume. Hovering over a league highlights its import-export corridors with other leagues."
* **Timing:** 1.5 minutes (App Demo Part 1)

---

## Slide 16: App Demo: Compare Mode & Details Panel (18:30 - 20:00)
* **Canva Template Page:** **Page 10 (Data Analysis Layout)**
* **Visual Setup:**
  * Left: Description of comparing algorithms and drilling down.
  * Right: Database cylinder with magnifying glass graphic (representing data validation).
* **Slide Content:**
  * **Compare Mode:**
    * Side-by-side bar charts displaying PageRank and HITS under identical filters.
    * Allows direct inspection of rank overlap and structural divergence.
  * **Transfer Details Popup:**
    * Click-to-expand panel on any ranking bar.
    * Exposes the raw player transfers making up the score, ensuring transparency.
* **Speaker Script:**
  > "To compare the algorithms directly, the system features a side-by-side Compare Mode. 
  > It runs both models under identical filters and displays parallel bar charts, making it easy to identify which clubs rank highly under both approaches and which diverge. 
  > Additionally, to validate the scores, users can click on any club to open the Transfer Details Panel. This displays the underlying transfer records, showing exactly which players and fees contributed to the club's score, linking macro metrics with micro raw data."
* **Timing:** 1.5 minutes (App Demo Part 2)

---

## Slide 17: App Demo: Dynamic Historical View (20:00 - 21:30)
* **Canva Template Page:** **Page 13 (Career Opportunities Pill Layout)**
* **Visual Setup:**
  * Centered Title: "Dynamic Historical View"
  * 4 pills representing the dynamic interface features:
    * Racing Bar Chart (D3.js)
    * Season-by-Season playback
    * Real-time algorithm toggle
    * Smooth graphical transitions
* **Slide Content:**
  * **Racing Bar Chart:** Tracks and re-orders club ranks across a 20-year span.
  * **Dynamic Controls:** Pause playback and toggle between PageRank and HITS.
  * **Smooth Transitions:** Instantly re-animates bars to show alternate scoring.
* **Speaker Script:**
  > "The final part of the demo is the Historical Animated Bar Chart, a racing bar chart showing rank changes season-by-season. 
  > It uses D3.js transitions to animate rank swaps over twenty years, showing how club influence rises or falls. 
  > A key feature is the real-time toggle: users can pause the timeline at any season and switch between PageRank and HITS. The visual interface immediately re-orders the bars to reflect the alternative mathematical ranking for that exact year, supporting granular analysis."
* **Timing:** 1.5 minutes (App Demo Part 3)

---

## Slide 18: Results: Buyer-Oriented Analysis (21:30 - 22:45)
* **Canva Template Page:** **Page 11 (Data Visualization Layout)**
* **Visual Setup:**
  * Left: Parallel ranking tables showing Top 10 Buyers (PageRank vs. HITS Authority) in Fee-Weighted mode.
  * Right: Analysis of the rankings.
* **Slide Content:**

| PR Rank | Club | Score | HITS Rank | Club | Score |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **1** | Chelsea | 11.50 | **1** | FC Barcelona | 0.367 |
| **2** | Man City | 11.32 | **2** | Man City | 0.359 |
| **3** | Real Madrid | 10.63 | **3** | Real Madrid | 0.336 |
| **4** | Man Utd | 9.71 | **4** | Chelsea | 0.335 |
| **5** | FC Barcelona | 9.09 | **5** | Paris SG | 0.309 |

  * *Key Insight:* PageRank Buyers represent global attractors in player flow. HITS Authorities represent target destinations pointing to strong hubs.
* **Speaker Script:**
  > "Let's review the empirical findings. Slide 18 shows the top buyers in fee-weighted mode. 
  > In PageRank, Chelsea and Manchester City lead. They act as global attractors, buying from structurally significant sellers. 
  > In HITS, FC Barcelona ranks 1st, followed by Manchester City. 
  > Note the difference: Chelsea drops from 1st in PageRank to 4th in HITS Authority, while Barcelona rises from 5th to 1st. PageRank measures global centrality in the overall network, while HITS Authority highlights clubs that are major destinations pointing to strong hubs."
* **Timing:** 1.25 minutes

---

## Slide 19: Results: Seller-Oriented Analysis (22:45 - 24:00)
* **Canva Template Page:** **Page 11 (Data Visualization Layout)**
* **Visual Setup:**
  * Left: Parallel ranking tables showing Top 10 Sellers (PageRank Sellers vs. HITS Hubs) in Fee-Weighted mode.
  * Right: Analysis of the rankings.
* **Slide Content:**

| PR Rank | Club | Score | HITS Rank | Club | Score |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **1** | Inter | 2.25 | **1** | Monaco | 0.325 |
| **2** | FC Porto | 2.17 | **2** | Real Madrid | 0.255 |
| **3** | Parma | 1.98 | **3** | FC Barcelona | 0.254 |
| **4** | Juventus | 1.81 | **4** | Liverpool | 0.243 |
| **5** | AS Roma | 1.76 | **5** | Benfica | 0.211 |

  * *Key Insight:* PageRank Sellers are computed by reversing edge direction. HITS Hubs naturally measure feeder roles pointing to strong authorities.
* **Speaker Script:**
  > "For seller-oriented analysis, we look at the supplier side. 
  > PageRank Seller is computed by reversing edge directions, highlighting Inter, Porto, and Parma. 
  > HITS Hubs, which naturally measure feeder quality without needing edge reversal, ranks AS Monaco 1st, followed by Real Madrid, Barcelona, and Liverpool. 
  > Monaco's 1st place in HITS Hubs is structurally fascinating—it highlights them as a prime feeder club transferring players directly to strong authorities, while clubs like Real Madrid and Barcelona appear high because they frequently sell players to other high-level teams."
* **Timing:** 1.25 minutes

---

## Slide 20: Results: Weighting Mode Comparison (24:00 - 25:15)
* **Canva Template Page:** **Page 12 (Case Study Layout)**
* **Visual Setup:**
  * Left: Analysis of Fee-Weighted (Economic Centrality) versus Count-Weighted (Transactional Activity).
  * Right: Money bag and calculator graphic.
* **Slide Content:**
  * **Fee-Weighted Mode (Economic Centrality):**
    * Emphasizes financial power. Ranks dominated by Premier League and elite clubs (Chelsea, Man City, Real Madrid).
  * **Count-Weighted Mode (Transactional Frequency):**
    * Highlights clubs with high transfer volumes, regardless of financial scale.
  * **The Italian Market Case:**
    * Under count-weighted HITS, Serie A clubs dominate: Inter (1st Authority, 1st Hub), Juventus (2nd Authority), AC Milan, and Roma rise.
    * Confirms high-frequency domestic trading patterns.
* **Speaker Script:**
  > "Slide 20 contrasts our weighting modes. Fee-weighted analysis highlights financial clout, emphasizing clubs like Chelsea, Man City, and PSG. 
  > Count-weighted analysis, however, treats every transfer equally, focusing on transaction frequency. 
  > Under count-weighted HITS, we see a fascinating pattern: Italian clubs dominate the rankings. Inter ranks 1st as both Authority and Hub, and Juventus, Milan, and Roma rise significantly. 
  > This shows that Italian football has a highly active player-exchange system, with clubs continuously buying and selling among themselves and Europe, even if individual fees are relatively modest."
* **Timing:** 1.25 minutes

---

## Slide 21: Case Study: FC Barcelona Longitudinal Analysis (25:15 - 26:30)
* **Canva Template Page:** **Page 12 (Case Study Layout)**
* **Visual Setup:**
  * Left: Barcelona's ranking stats table across 19 seasons.
  * Right: Money bag and calculator graphic.
* **Slide Content:**

| Algorithm & Weight | Total Top-10 | Total Top-5 | Best Rank | Best Year(s) |
| :--- | :---: | :---: | :---: | :---: |
| **PageRank (Fee)** | 6 | 3 | 1st | 2014-2015 |
| **HITS Authority (Fee)** | 9 | 7 | 2nd | Multiple (e.g. 2010-11) |
| **PageRank (Count)** | 4 | 2 | 1st | 2014-2015 |
| **HITS Authority (Count)** | 8 | 4 | 2nd | 2000-01, 2009-10 |

  * *Key Finding:* Barcelona acts as a consistently strong **Authority** (stable talent destination) but is a volatile, periodically dominant **PageRank** attractor (highly dependent on high-value spending windows).
* **Speaker Script:**
  > "To see how these algorithms behave over time, I ran a case study on FC Barcelona across 19 seasons. 
  > Barcelona's PageRank is highly volatile, appearing in the Top 10 in only 6 seasons, and peaking at 1st in the treble-winning 2014-2015 season. 
  > Under HITS Authority, however, Barcelona is much more stable, appearing in the Top 10 in 9 seasons and Top 5 in 7 seasons. 
  > This shows that Barcelona's structural role is best defined as a consistent Authority—a premier destination for players from top hubs—rather than a club that is globally central in terms of total transfer volume every year."
* **Timing:** 1.25 minutes

---

## Slide 22: Discussion & Contributions (26:30 - 28:00)
* **Canva Template Page:** **Page 14 (Professional Challenges Layout)**
* **Visual Setup:**
  * Left: Text panel summarizing the thesis contributions.
  * Right: Warning triangle and gear graphic (representing structural challenges resolved).
* **Slide Content:**
  * **1. Unified Comparative Framework:** Evaluating PageRank and HITS on identical subgraphs.
  * **2. Graph-Based Transfer Modeling:** Mapping market economic structures as a weighted directed graph.
  * **3. Distributed Scale using PySpark:** Building an in-memory RDD computation pipeline.
  * **4. Transfer Analyzer Application:** Packaging analytics into an interactive browser dashboard.
  * **5. Domain Translation:** Defining clear economic roles for graph metrics (attractors, feeder hubs).
* **Speaker Script:**
  > "To conclude, this thesis delivers five main contributions. 
  > It establishes a unified comparative framework. It models the football transfer market as a weighted directed graph. It provides a distributed, scalable PySpark implementation. 
  > It packages this engine into the Transfer Analyzer web application. And finally, it translates abstract graph theory into real sports economics. 
  > Ultimately, we prove that PageRank and HITS do not produce duplicate rankings. Instead, PageRank measures global centrality, while HITS identifies localized hub-authority structures."
* **Timing:** 1.5 minutes

---

## Slide 23: Conclusion & Q&A (28:00 - 30:00)
* **Canva Template Page:** **Page 17 (Thank You Layout)**
* **Visual Setup:**
  * Left: Title: "Thank you for your attention". Large text box for Q&A and contact details.
  * Right: Staircase and climbing character graphic (representing next steps and future work).
* **Slide Content:**
  * **Future Work:**
    * Integrate SALSA, Katz Centrality, or community detection algorithms.
    * Enrich dataset with player age, position, contract terms, and team stats.
    * Move to continuous dynamic graph tracking instead of static season snapshots.
    * Benchmark PySpark engine execution on multi-node distributed clusters.
  * **Thank You!** Questions & Answers.
* **Speaker Script:**
  > "For future work, I hope to expand the algorithms to include models like SALSA or Katz centrality. 
  > We can also enrich the dataset with player age or performance metrics, move to dynamic graph modeling, and deploy the engine on a true multi-node Spark cluster to benchmark scalability. 
  > I would like to thank my supervisor, Dr. Islam, and the members of the committee for their time and guidance. I am now open to any questions you may have. Thank you."
* **Timing:** 2.0 minutes

---
