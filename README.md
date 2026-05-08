# StoryForge

**Two-Workflow Generative AI Application for Specialty Insurance Functional Leads**

---

## Overview

StoryForge is a narrowly scoped Generative AI application designed for **Functional Leads in specialty insurance** who manage large portfolios and must rapidly translate ambiguous business requirements into structured, sprint-ready delivery artifacts.

The application provides two independent generative workflows that operate on the same feature input and address complementary aspects of sprint readiness.

---

## The Problem

Functional Leads frequently receive high-level feature requests that are too vague or incomplete to place directly into a delivery backlog. Writing user stories with testable acceptance criteria is time-consuming and inconsistent. Hidden risks, dependencies, and missing requirements routinely surface mid-sprint — causing rework, missed deadlines, and scope disputes.

StoryForge addresses both problems with a unified interface: generate the story, then stress-test the feature's readiness.

---

## Two Workflows

### Workflow 1 — User Story Generation

Converts a feature description into a Definition-of-Ready user story package:

| Output | Description |
|---|---|
| User story | As a / I want / so that format |
| Acceptance criteria | Given/When/Then, specific and testable |
| DoR assessment | Criteria met and missing |
| Missing information | Gaps that prevent sprint entry |
| Assumptions | Inferred context made explicit |
| Confidence level | low / medium / high |
| Escalation flag | Triggered when ambiguity is unresolvable |

**Time reduction: 30–60 minutes (manual) → under 3 minutes**

### Workflow 2 — Risk Signal Analysis

After stories are generated, surface the risk signals that story generation cannot produce:

| Output | Description |
|---|---|
| Edge cases | Boundary conditions, error scenarios, race conditions not covered by acceptance criteria |
| Dependencies | External systems, teams, APIs, and data sources this story relies on |

Two modes:
- **🔬 Risk Signals** — analyze one story inline with a single button click
- **🕵️ Risk Sweep** — analyze all stories in a feature in one pass

Results render inline within each story card. Only non-duplicative signals are returned — ambiguities and missing requirements are intentionally excluded because the `StoryPackage` already surfaces those via `missing_information` and `criteria_missing`.

---

## Technology Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Language | Python |
| LLM Provider | Anthropic Claude API (`claude-sonnet-4-6`, `claude-haiku-4-5`) |
| Auth + Database | Supabase (email/password auth, PostgreSQL with RLS) |
| Validation | Pydantic |
| Environment | `.env` / `python-dotenv` |
| Version Control | GitHub |

---

## Repository Structure

```text
StoryForge/
├── app/
│   ├── dashboard_view.py     # Project list with Add/Edit modals and feature/story counts
│   ├── db.py                 # All Supabase queries
│   ├── dor_checker.py        # DoR compliance utilities
│   ├── feature_view.py       # Story list, fan-out, Risk Signals, Risk Sweep, Edit Story modal
│   ├── llm_client.py         # All LLM calls (Sonnet + Haiku)
│   ├── login_view.py         # Sign in / sign up
│   ├── main.py               # App routing and session restore
│   ├── parser.py             # Pydantic models and output parsers
│   ├── project_view.py       # Feature list with Add/Edit/Enhance/Bulk Delete modals
│   ├── prompts.py            # All prompt builders
│   └── ui.py                 # Shared UI helpers
├── eval/
│   ├── run_eval.py           # Automated evaluation runner (--runs flag for reliability)
│   ├── rubric.py             # Five-dimension scoring rubric
│   ├── compare_results.py    # Dimension-level delta analysis
│   └── test_cases.json       # 16 synthetic test cases
├── outputs/
│   ├── baseline_results.json
│   ├── improved_results.json
│   ├── eval_scores.csv
│   └── parse_errors.log
├── docs/
│   ├── project_plan.md
│   ├── technical_design.md
│   └── storyforge_enhanced_handoff.md
├── enhanced_app.py           # Entry point
├── .env.example
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- An Anthropic API key
- A Supabase project (free tier) with `SUPABASE_URL` and `SUPABASE_ANON_KEY`

### Setup

```bash
git clone https://github.com/bradashepard-codes/StoryForge.git
cd StoryForge
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY, SUPABASE_URL, and SUPABASE_ANON_KEY to .env
```

### Run the App

```bash
python3 -m streamlit run enhanced_app.py
```

---

## Usage

1. Sign in or create an account
2. Create a project and add a feature
3. Open a feature to access both workflows:
   - **🚀 Generate All Stories** — fan-out decomposition into 3–5 atomic stories (requires AI-enhanced feature)
   - **✍️ Add Story Manually** — generate a single story via modal
   - **🔬 Risk Signals** — per-story edge cases and dependencies (button on each story card)
   - **🕵️ Risk Sweep** — analyze all stories in one pass (header button)
4. Review all outputs before sprint entry

**Human review is required before any output is treated as sprint-ready.**

---

## Evaluation

StoryForge includes a local evaluation harness that scores Workflow 1 outputs against a human manual baseline across 16 synthetic test cases using a five-dimension rubric:

| Dimension | What It Measures |
|---|---|
| Clarity | Precision and lack of ambiguity |
| Completeness | All required story elements present |
| Testability | Acceptance criteria are verifiable |
| DoR Compliance | Meets all six Definition of Ready criteria |
| Escalation Accuracy | Correctly flags ambiguous inputs |

Run evaluation:

```bash
python eval/run_eval.py
python eval/run_eval.py --runs 3   # reliability pass
```

---

## Governance

- All outputs require human review before backlog entry or sprint planning
- The system does not write to Jira, GitHub Issues, or any external system
- Only synthetic or user-authored inputs are used — no proprietary insurance data
- API keys must never be committed to version control

---

## Project Team

| Role | Contributor |
|---|---|
| Technical Lead — Architecture, development, prompt engineering, evaluation | Brad Shepard |
| Presentation Lead — Test case support, evaluation write-up, demo, slides | Jeff Dunlao |

---

## Documentation

- [Project Plan](docs/project_plan.md)
- [Technical Design](docs/technical_design.md)
- [Enhanced App Handoff](docs/storyforge_enhanced_handoff.md)
