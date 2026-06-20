# Presentation Context: Thesis Defense
**Last Updated:** 2026-06-19 (Session 2)

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
- **PageRank highlights:** Magenta/Pink (for every mention of "PageRank")
- **HITS highlights:** Orange `#FF6B35` (for every mention of "HITS")
- **Apache Spark highlights:** Orange `#FF6B35`
- **Body text:** White `#FFFFFF`
- **Secondary text:** Light gray
- **Network graph element:** Light blue/cyan nodes and edges (used as right-side visual on slides)

### Color Rules (apply to ALL slides):
| Element | Color |
|---|---|
| Slide titles | Cyan `#00D4FF` |
| **PageRank** mentions | Magenta/Pink |
| **HITS** mentions | Orange `#FF6B35` |
| **Apache Spark** mentions | Orange `#FF6B35` |
| Body/bullet text | White `#FFFFFF` |
| Secondary/caption text | Light gray |
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

## 4. Presentation Flow (Confirmed Slide Order — OPTION A LOCKED IN)
> **Decision (2026-06-19 Session 3):** Following `presentation_slides_script.md` order (Option A).
> This matches the thesis chapter structure: Intro → Problem → RQs → Objectives → Theory → Methodology → App → Results → Conclusion.
> The "Football Transfer Network dataset intro" slide has been REMOVED — dataset context is woven into the Methodology slide instead.

| Slide # | Topic | Source (script.md) | Status |
|---|---|---|---|
| 1 | Title Slide | Slide 1 | DONE |
| 2 | Introduction & Motivation | Slide 2 | DONE (3 tweaks remaining) |
| 3 | Problem Statement | Slide 3 | IN PROGRESS |
| 4 | Research Questions | Slide 4 | TODO |
| 5 | Thesis Objectives | Slide 5 | TODO |
| 6 | Theoretical Background: The Web Graph | Slide 6 | TODO |
| 7 | PageRank: Random Surfer & Google Matrix | Slide 7 | TODO |
| 8 | PageRank: Convergence & Limitations | Slide 8 | TODO |
| 9 | HITS: Hubs & Authorities Duality | Slide 9 | TODO |
| 10 | HITS: Mathematical & Matrix Formulation | Slide 10 | TODO |
| 11 | Algorithmic Comparison: PageRank vs. HITS | Slide 11 | TODO |
| 12 | Methodology: Graph & Transfer Market Formulation | Slide 12 | TODO |
| 13 | Methodology: PySpark Processing Pipeline | Slide 13 | TODO |
| 14 | System Architecture: The Transfer Analyzer | Slide 14 | TODO |
| 15 | App Demo: Interactive Visualizations | Slide 15 | TODO |
| 16 | App Demo: Compare Mode & Details Panel | Slide 16 | TODO |
| 17 | App Demo: Dynamic Historical View | Slide 17 | TODO |
| 18 | Results: Buyer-Oriented Analysis | Slide 18 | TODO |
| 19 | Results: Seller-Oriented Analysis | Slide 19 | TODO |
| 20 | Results: Weighting Mode Comparison | Slide 20 | TODO |
| 21 | Case Study: FC Barcelona Longitudinal Analysis | Slide 21 | TODO |
| 22 | Discussion & Contributions | Slide 22 | TODO |
| 23 | Conclusion & Q&A | Slide 23 | TODO |

---

## 5. Completed Slides — Exact Content

### SLIDE 1: Title Slide — DONE
**Layout:** Dark purple bg, title left, network graph right, GUC logo top-left.

**Content:**
- Main Title: Comparing PageRank and HITS using Apache Spark
  - "PageRank" = Orange, "HITS" = Orange, rest = White
- Subtitle: A Network Analysis of the Global Football Transfer Market (White)
- Presented by: Mark Maged Samir
- Supervised by: Dr. Islam A. El-Maddah
- German University in Cairo — 2026
- GUC Logo: Top left
- Visual: Network node graph (light blue/cyan) on the right side

**Speaker script:** None — this is the opening slide shown while the committee settles.

---

### SLIDE 2: Introduction & Motivation — DONE (3 tweaks remaining)
**Layout:** Title + 4 bullet points on left, large network graph visual on right.

**Content:**
- Title: Introduction & Motivation (Cyan #00D4FF) — CURRENTLY STILL GREEN, NEEDS CHANGING
- Bullet 1: The web is a graph — hyperlinks are votes, PageRank & HITS turn those votes into rankings.
- Bullet 2: These algorithms power Google Search, recommendations, and fraud detection.
- Bullet 3: Can they reveal hidden structure in a completely different domain — professional football?
- Bullet 4: This thesis uses the global transfer market as a testbed to compare them at scale using Apache Spark.
- Orange highlights: "PageRank & HITS", "Google Search", "Apache Spark" — NOT YET DONE

**3 remaining tweaks:**
1. Change title color from GREEN to Cyan #00D4FF
2. Highlight "PageRank & HITS", "Google Search", "Apache Spark" in Orange #FF6B35
3. Increase bullet text size to 18-20px

**Speaker script:**
"When Larry Page and Jon Kleinberg introduced PageRank and HITS in the late 1990s, they changed how we understand networks. Instead of looking at content alone, they looked at connections — who links to whom, and what that says about importance.

These algorithms are everywhere today. Google Search, YouTube recommendations, even fraud detection. But they have mostly been studied on web data.

So the question I asked was: can these same algorithms reveal something meaningful about a completely different kind of network — the global football transfer market? And how do they compare when running on the same data, at the same time, under identical conditions? That is exactly what this thesis explores."

---

### SLIDE 3: Problem Statement — IN PROGRESS (not yet built in Canva)
**Decision:** Problem Statement comes BEFORE the Transfer Network intro slide.
**Layout:** Clean dark purple background. No world map. Simple title + 4 bullets.

**Content:**
- Title: Problem Statement (Cyan)
- Bullet 1: Most studies evaluate PageRank and HITS separately — never on the same dataset under identical conditions.
- Bullet 2: Existing research is web-centric — little work on weighted, financially-driven networks.
- Bullet 3: No interactive tool exists to explore how parameter changes affect rankings in real time.
- Bullet 4 (bold/orange): This thesis bridges all three gaps.

**Speaker script:**
"What is actually missing in the literature? First, there is no unified comparison — studies use different datasets, so results cannot be fairly evaluated side by side. Second, almost everything uses web data. Nobody has tested these algorithms on a financially-weighted network. And third, there is no interactive way to explore the results. My thesis addresses all three gaps."

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
