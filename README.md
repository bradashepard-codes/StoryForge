# StoryForge

**Definition-of-Ready User Story Generator for Specialty Insurance Functional Leads**

---

## Overview

StoryForge is a narrowly scoped Generative AI application that converts a single feature description into a sprint-ready user story package. It is designed for Functional Leads in specialty insurance who manage large portfolios and need to rapidly translate ambiguous business requirements into structured, delivery-ready backlog items.

What would otherwise take a Functional Lead 30–60 minutes of manual drafting, iteration, and stakeholder reconciliation takes StoryForge under 3 minutes — with consistent structure, testable criteria, and explicit ambiguity detection every time.

The system is evaluated by comparing its outputs against a human manual baseline to demonstrate measurable improvement in quality, consistency, and Definition-of-Ready compliance.

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
| Language | Python |
| LLM Provider | Anthropic Claude API |
| Environment | `.env` / `python-dotenv` |
| Validation | Pydantic |
| Evaluation | Pandas, local scripts |
| Version Control | GitHub |

---

## Repository Structure

```text
storyforge/
├── app/
│   ├── main.py
│   ├── ui.py
│   ├── prompts.py
│   ├── llm_client.py
│   ├── parser.py
│   └── dor_checker.py
├── eval/
│   ├── run_eval.py
│   ├── rubric.py
│   ├── compare_results.py
│   └── test_cases.json
├── outputs/
│   ├── baseline_results.json
│   ├── improved_results.json
│   └── eval_scores.csv
├── docs/
│   ├── project_plan.md
│   ├── technical_design.md
│   └── evaluation_notes.md
├── .env.example
├── requirements.txt
├── README.md
└── streamlit_app.py
```

---

## Getting Started

### Prerequisites
- Python 3.9+
- An Anthropic API key

### Setup

```bash
git clone https://github.com/bradashepard-codes/StoryForge.git
cd StoryForge
pip install -r requirements.txt
cp .env.example .env
# Add your Anthropic API key to .env
```

### Run the App

```bash
streamlit run streamlit_app.py
```

---

## Usage

1. Enter a feature description into the input form
2. Click **Generate**
3. Review the structured user story and acceptance criteria
4. Assess the DoR status, missing information, and escalation flag
5. Accept, revise, or escalate as needed

**Human review is required before any output is treated as sprint-ready.**

---

## Evaluation

StoryForge includes a local evaluation harness that scores StoryForge outputs against a human manual baseline across a synthetic test set of 12 feature inputs using a five-dimension rubric:

| Dimension | What It Measures |
|---|---|
| Clarity | Precision and lack of ambiguity |
| Completeness | All required story elements present |
| Testability | Acceptance criteria are verifiable |
| DoR Compliance | Meets Definition of Ready criteria |
| Escalation Accuracy | Correctly flags ambiguous inputs |

Run evaluation:

```bash
python eval/run_eval.py
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
