# StoryForge

**Definition-of-Ready User Story Generator for Specialty Insurance Functional Leads**

🚀 **Live App:** [https://story-forge.streamlit.app/](https://story-forge.streamlit.app/)

---

## Overview

StoryForge is a narrowly scoped Generative AI application that converts a single feature description into a sprint-ready user story package. It is designed for Functional Leads in specialty insurance who manage large portfolios and need to rapidly translate ambiguous business requirements into structured, delivery-ready backlog items.

The application compares two prompt approaches side by side:
- a **baseline prompt** (minimal instruction)
- a **context-engineered prompt** (role framing, output contract, few-shot examples, escalation logic)

This comparison is the core evaluation mechanism of the project.

---

## The Problem

Functional Leads frequently receive high-level feature requests that are too vague or incomplete to place directly into a delivery backlog. Writing user stories with testable acceptance criteria is time-consuming, inconsistent, and prone to quality gaps — especially across 20+ concurrent projects.

StoryForge addresses that gap by generating a structured user story package and explicitly flagging ambiguity before it reaches engineering.

---

## What It Generates

For each feature description submitted, StoryForge returns:

- **User story** — role, goal, and rationale
- **Acceptance criteria** — Given/When/Then format
- **Definition of Ready assessment** — criteria met and missing
- **Missing information** — gaps that prevent sprint entry
- **Assumptions** — inferred context
- **Confidence level** — low / medium / high
- **Escalation flag** — triggered when ambiguity is unresolvable

All outputs conform to a fixed JSON schema. Outputs that do not match the schema are treated as invalid.

---

## Technology Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Language | Python 3.14 |
| LLM Provider | Anthropic Claude API (`claude-sonnet-4-6`) |
| Environment | `.env` / `python-dotenv` |
| Validation | Pydantic |
| Evaluation | Pandas, local scripts |
| Version Control | GitHub |
| Deployment | Streamlit Cloud |

---

## Repository Structure

```text
StoryForge/
├── app/
│   ├── main.py           ← entry point
│   ├── ui.py             ← Streamlit UI and form logic
│   ├── prompts.py        ← baseline and context-engineered prompts
│   ├── llm_client.py     ← Anthropic API integration
│   ├── parser.py         ← output parsing and Pydantic validation
│   └── dor_checker.py    ← DoR assessment logic
├── eval/
│   ├── run_eval.py       ← evaluation runner (parallelized)
│   ├── rubric.py         ← rubric definitions and scoring
│   ├── compare_results.py← baseline vs improved comparison
│   └── test_cases.json   ← 12 synthetic test cases
├── outputs/              ← generated results and eval scores
├── docs/
│   ├── project_plan.md
│   ├── technical_design.md
│   └── evaluation_notes.md
├── .env.example
├── .python-version
├── requirements.txt
├── README.md
└── streamlit_app.py
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- An Anthropic API key

### Setup

```bash
git clone https://github.com/bradashepard-codes/StoryForge.git
cd StoryForge
python3 -m pip install -r requirements.txt
cp .env.example .env
# Add your Anthropic API key to .env
```

### Run the App

```bash
python3 -m streamlit run streamlit_app.py
```

---

## Usage

1. Enter a feature description into the input form
2. Click **Generate**
3. Both baseline and improved outputs are generated in parallel
4. Review the outputs side by side:
   - Baseline — unstructured, minimal prompt response
   - Improved — structured user story, acceptance criteria, DoR assessment
5. Assess the DoR status, missing information, and escalation flag
6. Accept, revise, or escalate as needed

**Human review is required before any output is treated as sprint-ready.**

---

## Evaluation

StoryForge includes a local evaluation harness that scores both prompt variants against a synthetic test set of 12 feature inputs across four categories — standard, ambiguous, incomplete, and edge cases — using a five-dimension rubric:

| Dimension | What It Measures |
|---|---|
| Clarity | Precision and lack of ambiguity |
| Completeness | All required story elements present |
| Testability | Acceptance criteria are verifiable |
| DoR Compliance | Meets Definition of Ready criteria |
| Escalation Accuracy | Correctly flags ambiguous inputs |

Scoring: 1 (Poor) / 3 (Moderate) / 5 (Strong) per dimension.

Run evaluation:

```bash
python3 eval/run_eval.py
```

Compare results after manual scoring:

```bash
python3 eval/compare_results.py
```

---

## Branching Strategy

```
main                    ← stable, auto-deploys to Streamlit Cloud
└── dev                 ← integration branch
    └── docs/evaluation-notes  ← Jeff's documentation lane
```

All work flows through `dev` before merging to `main`.

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
