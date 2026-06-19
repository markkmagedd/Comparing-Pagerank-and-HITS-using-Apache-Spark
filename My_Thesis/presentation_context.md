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
| 2 | Introduction & Motivation | DONE (3 tweaks remaining) |
| 3 | Problem Statement | IN PROGRESS |
| 4 | The Football Transfer Network (dataset intro) | TODO |
| 5 | Background: PageRank Algorithm | TODO |
| 6 | Background: HITS Algorithm | TODO |
| 7 | Methodology: Graph Construction | TODO |
| 8 | Methodology: Apache Spark & PySpark | TODO |
| 9 | System Architecture (Transfer Analyzer) | TODO |
| 10-12 | Results: Rankings & Comparisons | TODO |
| 13-15 | Live App Demo | TODO |
| 16-17 | Computational Performance | TODO |
| 18-19 | Discussion & Analysis | TODO |
| 20 | Conclusion | TODO |
| 21 | Future Work | TODO |
| 22 | References | TODO |
| 23 | Thank You / Q&A | TODO |

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
