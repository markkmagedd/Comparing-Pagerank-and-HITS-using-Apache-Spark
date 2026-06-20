# Presentation Context: Thesis Defense
**Last Updated:** 2026-06-20 (Session 3)

This document contains all context, design decisions, and slide progress for Mark's 30-minute Bachelor's thesis defense presentation:
**"Comparing PageRank and HITS using Apache Spark: A Network Analysis of the Global Football Transfer Market"**

**If you are an AI assistant reading this on a new device, read this entire file carefully before doing anything. It contains all decisions made so far and the exact state of the presentation.**

---

## 1. Presenter Information
- **Presenter:** Mark Maged Samir
- **Supervisor:** Dr. Islam A. El-Maddah
- **Institution:** German University in Cairo (GUC)
- **Year:** 2026
- **Thesis PDF:** Available in `My_Thesis/` directory — read it for academic details.
- **Full script file:** `My_Thesis/presentation_slides_script.md`

---

## 2. Template Decision (FINAL)
After trying multiple Canva templates, the final chosen template is:

**"Machine Learning dark presentation"** — a dark purple/violet themed template.

### Template Characteristics:
- **Background:** Deep dark purple/violet
- **Title accent color:** Cyan `#00D4FF` (for slide titles and key headings)
- **Keyword highlights:** Orange `#FF6B35` (for key terms like "PageRank", "HITS", "Apache Spark")
- **Body text:** White `#FFFFFF`
- **Secondary text:** Light gray
- **Network graph element:** Light blue/cyan nodes and edges (used as right-side visual on slides)

### Color Rules (apply to ALL slides):
| Element | Color |
|---|---|
| Slide titles | Cyan #00D4FF |
| Key algorithm names (PageRank, HITS) | Orange #FF6B35 |
| Body/bullet text | White #FFFFFF |
| Secondary/caption text | Light gray |
| Apache Spark mentions | Orange #FF6B35 |
| GUC Logo | Always top-left corner of every slide |

### Important design notes:
- Dark app screenshots look GREAT on this dark background — no need for white slides
- When placing app screenshots, add a subtle border or drop shadow to make them stand out
- Replace ALL cartoon/character illustrations from the template with real visuals (network graphs, app screenshots, results tables)
- Minimum bullet text size: 18-20px — audience must read from the back of the room

---

## 3. Pacing Strategy (30 Minutes)
- **Slide Count:** ~20-23 Slides
- **Pacing:** ~1 to 1.5 minutes speaking per slide
- **App Demo:** Live demo or video walkthrough = roughly 6–8 minutes

---

## 4. Presentation Flow (Confirmed Slide Order)
| Slide # | Topic | Status |
|---|---|---|
| 1 | Title Slide | DONE |
| 2 | Introduction & Motivation | DONE |
| 3 | Problem Statement | DONE |
| 4 | Research Questions | DONE |
| 5 | Thesis Objectives | DONE (missing Title on Canva slide) |
| 6 | Theoretical Background: PageRank & HITS Overview | DONE (needs photo update) |
| 7 | PageRank: Random Surfer & Google Matrix | TODO |
| 8 | PageRank: Convergence & Limitations | TODO |
| 9 | HITS: Hubs & Authorities Duality | TODO |
| 10 | HITS: Mathematical & Matrix Formulation | TODO |
| 11 | Algorithmic Comparison: PageRank vs. HITS | TODO |
| 12 | Methodology: Graph & Transfer Market Formulation | TODO |
| 13 | Methodology: PySpark Processing Pipeline | TODO |
| 14 | System Architecture: The Transfer Analyzer | TODO |
| 15 | App Demo: Interactive Visualizations | TODO |
| 16 | App Demo: Compare Mode & Details Panel | TODO |
| 17 | App Demo: Dynamic Historical View | TODO |
| 18 | Results: Buyer-Oriented Analysis | TODO |
| 19 | Results: Seller-Oriented Analysis | TODO |
| 20 | Results: Weighting Mode Comparison | TODO |
| 21 | Case Study: FC Barcelona Longitudinal Analysis | TODO |
| 22 | Discussion & Contributions | TODO |
| 23 | Conclusion & Q&A | TODO |

---

## 5. Completed Slides — Exact Content

### SLIDE 1: Title Slide — DONE
**Layout:** Dark purple bg, title left, network graph right, GUC logo top-left.
**Content:**
- Title: Comparing PageRank and HITS using Apache Spark
- Presenter: Mark Maged Samir
- Supervisor: Dr. Islam A. El-Maddah
- GUC Logo: Top left

---

### SLIDE 2: Introduction & Motivation — DONE
**Layout:** Title + 4 bullet points on left, large network graph visual on right.
**Content:**
- Title: Introduction & Motivation (Cyan `#00D4FF`)
- Bullets: The web is a graph; algorithms power Google Search; professional football transfer market testbed using Apache Spark.
- Orange Highlights: PageRank & HITS, Google Search, Apache Spark.

---

### SLIDE 3: Problem Statement — DONE
**Layout:** Clean dark purple background, person-with-question-marks icon.
**Content:**
- Title: Problem Statement (Cyan `#00D4FF`)
- Bullets: PageRank and HITS evaluated separately; research is web-centric; no interactive tool exists.
- Highlights: "PageRank and HITS" in Orange; last bullet "This thesis bridges all three gaps." in Bold Orange.

---

### SLIDE 4: Research Questions — DONE
**Layout:** Dark purple background, person-with-question-marks icon.
**Content:**
- Title: Research Questions
- Bullets: RQ1 (Theory), RQ2 (Implementation), RQ3 (Domain Insights) in Orange.

---

### SLIDE 5: Thesis Objectives — DONE (tweak needed)
**Layout:** 5 rounded purple pills containing objectives 1–5.
**Tweak needed:** Add "Thesis Objectives" title at the top of the Canva slide (Thesis in White, Objectives in Cyan).

---

### SLIDE 6: Theoretical Background: PageRank & HITS Overview — DONE ✅
**Layout:** Two-column cards (two separate rounded rectangle cards on a slightly lighter purple background), orange callout box.
**Title:** "Background" (White) + "Algorithms" (Cyan)
**Left card:** PageRank (Brin & Page, 1998) — Models a random surfer. One global score per node. `PageRank` highlighted Orange.
**Right card:** HITS (Kleinberg, 1999) — Hub score + Authority score, mutual reinforcement. `HITS` highlighted Orange.
**Orange box:** "PageRank and HITS both analyze link structure to rank nodes — but they ask fundamentally different questions and produce mathematically distinct outputs."
**Diagonal decorative shape:** Kept from template as background depth element.

---

### SLIDE 7: PageRank Algorithm — IN PROGRESS 🔄
**Layout:** ML Workflow 4-block template (title left, 2×2 text blocks, image panel right)
**Title:** "PageRank" (White) + "Algorithm" (Cyan)
**Replace:** "Thynk Unlimited" → GUC Logo
**Replace right image:** `My_Thesis/network_graph.png` (generated network visualization)
**4 blocks:**
- Top Left: "The Equation" → Upload `My_Thesis/pagerank_equation.png`
- Top Right: "Random Surfer Model" → prob d follow link, prob (1-d) teleport
- Bottom Left: "Google Matrix" → Upload `My_Thesis/google_matrix_equation.png`
- Bottom Right: "Convergence Guaranteed" → Perron-Frobenius theorem

**Equation PNG files location:** `My_Thesis/pagerank_equation.png` and `My_Thesis/google_matrix_equation.png`
(Generated via matplotlib — transparent background, white equation text — ready to upload to Canva)

---

## 6. Key Design Rules (Apply to ALL Future Slides)

1. GUC Logo must appear on the top-left of EVERY slide.
2. Delete all Lorem Ipsum placeholder text immediately.
3. Delete all template website URLs (e.g. www.reallygreatsite.com) immediately.
4. Replace all cartoon character illustrations with real visuals.
5. Slide titles: Always Cyan #00D4FF.
6. Key algorithm/tech names: Always Orange #FF6B35.
7. Body text minimum size: 18px.
8. App screenshots: Place on a slightly lighter dark card with drop shadow. Do NOT use white backgrounds.
9. Speaker script must be simple and conversational — NOT academic paper language.

---

## 7. Where to Continue
Start from SLIDE 3 (Problem Statement):
- Show the next available template slide layout in Canva
- Apply the Problem Statement content listed in Section 5
- Then move to Slide 4: The Football Transfer Network

Full detailed script for all 23 slides: My_Thesis/presentation_slides_script.md
