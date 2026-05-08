# StoryForge Enhanced — Presentation Deck
> 5 slides. Time targets listed per slide. Screenshot/visual notes in *italics*.

---

## Slide 1 — Title
🕒 10 sec

- **StoryForge Enhanced**
- Team: [Your Names]
- AI that turns feature descriptions into sprint-ready user stories and risk analysis — in seconds

*Visual: app logo or screenshot of the dashboard*

---

## Slide 2 — Problem
🕒 20 sec

*Visual: split screen — left: blank story template / sticky notes; right: screenshot of a vague feature description typed into the app*

- Business Analysts spend hours per sprint manually writing user stories and acceptance criteria
- Quality is inconsistent — vague criteria slip into sprints and cause rework mid-sprint
- Edge cases and dependencies are discovered during development, not planning

---

## Slide 3 — Solution / Workflows
🕒 40 sec

*Visual: two-lane flow diagram with screenshots at each step*

**Workflow 1 — Story Generation**
```
Feature Description
      ↓
✨ Enhance Feature  →  side-by-side Original vs. Enhanced
      ↓
🚀 Generate All Stories  →  3–5 atomic stories (Haiku, ~12s)
      ↓
Review & Save  →  DoR status · Confidence · Escalation flag
```

**Workflow 2 — Risk Signal Analysis**
```
Saved User Story
      ↓
🔬 Risk Signals (per story)  →  Edge Cases + Dependencies  [inline]
        — or —
🕵️ Risk Sweep (all stories)  →  Bulk analysis in one pass
```

*Screenshots to embed: Enhance Feature modal (side-by-side), Generate All Stories preview, Risk Signals in a story card*

---

## Slide 4 — Demo / Results
🕒 45 sec

*Visual: 3-panel screenshot layout*

**Panel 1 — Before: raw feature description**
> "Allow agents to capture UK address details for a new policy"

**Panel 2 — After Workflow 1: StoryPackage output**
- User Story: *As an Agent, I want to capture and validate a UK address during policy creation, so that policy records contain accurate, standardised location data.*
- Acceptance Criteria (Given/When/Then) — 3 testable criteria
- DoR: ✅ Ready · Confidence: Medium · Escalation: false

**Panel 3 — After Workflow 2: Risk Signals**
- *Edge case:* Postcode passes format check but does not exist in Royal Mail PAF
- *Edge case:* User pastes address from clipboard with inconsistent spacing
- *Dependency:* Address validation API — provider, rate limits, and failure behavior undefined

*Screenshot to embed: expanded story card showing Risk Signals section below the story content*

---

## Slide 5 — Key Takeaways
🕒 20–30 sec

**What worked**
- Few-shot examples grounded in the insurance domain improved acceptance criteria precision significantly
- Output contracts (exact JSON schema in prompt) eliminated hallucinated fields
- Haiku for structured, bounded outputs — 4–5× faster than Sonnet with no quality loss

**What we learned**
- Overlap analysis between two LLM workflows prevented redundant output — Risk Workflow was scoped down to only what the story model cannot produce (edge cases, dependencies)
- Model size is a UX decision, not just a cost decision

**Future improvements**
- Export stories to Jira / CSV for direct sprint board import
- Persist risk signals to database for cross-session audit trail
- Systematic evaluation harness (scaffolded — not yet run at scale)
