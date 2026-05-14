# StoryForge

**Generative AI Application for Specialty Insurance Functional Leads**

---

## Context, User, and Problem

**User:** Functional Leads in specialty insurance who own the delivery backlog for one or more product lines.

**Workflow being improved:** Translating high-level feature requests into sprint-ready user stories with testable acceptance criteria.

**Why it matters:** Functional Leads routinely receive feature requests that are too vague to place directly into a backlog. Writing a Definition-of-Ready (DoR) user story manually takes 30–60 minutes per feature and produces inconsistent output — acceptance criteria vary in specificity, gaps in requirements are missed, and hidden risks surface mid-sprint. At scale, this creates rework, missed deadlines, and scope disputes.

GenAI is well-suited here because the task is structured (the output format is fixed — user story + Given/When/Then criteria + DoR assessment) but the input is unstructured (natural language feature requests). The model can also detect ambiguity and flag incomplete inputs before the story reaches the backlog — something a keyword search or template cannot do.

---

## Solution and Design

StoryForge provides two independent workflows that operate on the same feature input.

### Workflow 1 — User Story Generation

Converts a feature description into a Definition-of-Ready story package in under 3 minutes.

| Output Field | Description |
|---|---|
| User story | As a / I want / so that format |
| Acceptance criteria | Given/When/Then, specific and testable |
| DoR assessment | Criteria met and criteria missing |
| Missing information | Gaps that prevent sprint entry |
| Assumptions | Inferred context made explicit |
| Confidence level | low / medium / high |
| Escalation flag | Triggered when ambiguity is unresolvable |

The output is validated at parse time using a Pydantic model (`StoryPackage`). If the model returns malformed JSON, the call fails cleanly with an error — no partial data reaches the UI.

**Fan-out:** A second call (Haiku model, lower cost) decomposes a feature into 3–5 atomic stories in parallel, each independently structured and scored.

**Enhance Feature:** Before generating stories, users can optionally enhance the raw feature description using a focused prompt that sharpens all three fields (description, business objective, intended user) and infers missing fields.

### Workflow 2 — Risk Signal Analysis

After stories are generated, a second prompt surfaces risk signals that the story generation prompt intentionally excludes — edge cases and dependencies that only make sense once the story structure exists.

Two modes:
- **Risk Signals** — per-story edge cases and dependencies, rendered inline on each story card
- **Risk Sweep** — all stories in a feature analyzed in one pass

### Key Design Choices

- **Structured output over free text.** The improved prompt returns a JSON object with typed fields. This enables Pydantic validation, DoR computation, and confident rendering — none of which are possible from unstructured markdown.
- **Separation of concerns across workflows.** Story generation, risk analysis, and feature enhancement are separate prompts with separate outputs. Combining them would increase token cost, make evaluation harder, and reduce reliability.
- **Two models for cost control.** Haiku runs the fan-out and suggest-context calls where speed and cost matter more than prose quality. Sonnet runs story generation and risk expansion where output quality is graded.
- **No RAG, no agents.** The workflow is stateless per call. Retrieval and orchestration would add complexity without improving the output for this use case.

### Technology Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Language | Python |
| LLM Provider | Anthropic Claude API (`claude-sonnet-4-6`, `claude-haiku-4-5`) |
| Auth + Database | Supabase (email/password auth, PostgreSQL with RLS) |
| Validation | Pydantic |
| Environment | `.env` / `python-dotenv` |

---

## Evaluation and Results

### Setup

The evaluation compares Workflow 1 outputs against a simpler baseline prompt. The baseline uses the same model (`claude-sonnet-4-6`) with a single instruction to write a user story — no system prompt, no output format, no DoR framing. This isolates the effect of prompt engineering from model capability.

### Test Cases

15 synthetic test cases covering five input categories:

| Category | Count | Description |
|---|---|---|
| Standard | 5 | Well-defined features with persona, objective, and business rules |
| Ambiguous | 3 | Vague or contradictory descriptions where escalation is correct |
| Incomplete | 3 | Missing required fields (no rules, no user, no objective) |
| Edge | 1 | Structurally valid but highly complex multi-line-of-business scenario |
| Adversarial | 3 | Pure placeholders, single words, or enterprise-sized scope in one sentence |

Test cases are in `eval/test_cases.json`. Outputs are in `outputs/`.

### Rubric

Five dimensions scored 1 / 3 / 5:

| Dimension | 1 (Poor) | 3 (Moderate) | 5 (Strong) |
|---|---|---|---|
| Clarity | Unclear or vague | Partially clear | Precise and unambiguous |
| Completeness | Missing key elements | Mostly complete | All required elements present |
| Testability | Criteria not testable | Some testable | All criteria specific and measurable |
| DoR Compliance | Fails most DoR criteria | Meets some | Fully meets all DoR criteria |
| Escalation Accuracy | Fails to flag ambiguity | Partially flags | Correctly flags or correctly does not flag |

### Results

| Dimension | Baseline | Improved | Delta |
|---|---|---|---|
| Clarity | 3.0 | 5.0 | +2.0 |
| Completeness | 3.0 | 5.0 | +2.0 |
| Testability | 3.0 | 3.8 | +0.8 |
| DoR Compliance | 1.0 | 5.0 | **+4.0** |
| Escalation Accuracy | 2.7 | 5.0 | **+2.3** |

Overall: baseline avg **2.5 / 5.0**, improved avg **4.8 / 5.0**.

Run the comparison yourself:

```bash
python3 eval/run_eval.py
python3 eval/compare_results.py
```

### What the Comparison Showed

**DoR Compliance (+4.0):** The single largest gap. The baseline prompt produces markdown prose — no DoR assessment exists unless the model improvises one. The improved prompt always returns `criteria_met` and `criteria_missing` as typed lists, enabling the UI to compute and display sprint-readiness at a glance.

**Escalation Accuracy (+2.3):** On the 8 ambiguous, incomplete, and adversarial cases, the baseline wrote a story in all 8 — improvising details where the input gave it nothing to work with (e.g., generating a full login flow from the input "Login screen"). The improved prompt correctly escalated all 8 and surfaced specific missing information. On the 7 standard and edge cases, both variants correctly did not escalate.

**Testability (+0.8):** The smallest gain. Both the baseline and improved prompts produce Given/When/Then acceptance criteria. The difference is precision: improved criteria are specific to the stated business rules (e.g., referencing the exact renewal date boundary). The gap narrows on ambiguous inputs — when the feature description is vague, neither variant can produce fully testable criteria.

### Where It Broke Down

- **Testability on ambiguous inputs.** When the input is underspecified, the model still generates acceptance criteria — they just aren't testable without more information. The improved prompt handles this correctly by escalating and flagging the gaps, but the criteria it produces in those cases are still imprecise (scored 3, not 5).
- **TC012 (multi-line-of-business edge case).** The improved prompt returned medium confidence and did not escalate on an input that may have warranted flagging — a complex simultaneous GL + Property + Excess submission scenario. The system produced criteria that are reasonable but incomplete without knowing the downstream rating and binding rules per line.
- **Human review is always required.** Escalation accuracy and DoR compliance measure whether the system correctly identifies what it does not know. They do not measure whether the output is correct when the system is confident. Even high-confidence stories with full DoR scores should be reviewed by a Functional Lead before backlog entry.

---

## Artifact Snapshot

### Sample Input

```
Feature: Broker Policy Change Submission
Description: Allow brokers to submit policy changes online through a self-service portal.
Business Objective: Reduce manual processing time for policy amendments and eliminate paper-based submissions.
Intended User: Broker
Business Rules: Changes must be submitted before the policy renewal date. Only active policies are eligible.
```

### Sample Output (Workflow 1 — Improved Prompt)

```
User Story:
  As a Broker, I want to submit policy change requests through a self-service
  online portal, so that I can reduce manual processing time and eliminate
  the need for paper-based submissions.

Acceptance Criteria:
  1. Given a broker is authenticated, when they navigate to the policy change
     screen, then only active policies are displayed.
  2. Given a broker selects an active policy, when they submit before the
     renewal date, then the system accepts the submission and returns a
     confirmation with a reference number.
  3. Given a broker attempts to submit on or after the renewal date, when the
     form is submitted, then the system rejects the request and displays an
     error stating the deadline has passed.
  4. Given a successful submission, when confirmed, then the broker receives
     an email acknowledgement with the reference number.

Definition of Ready: NOT READY
  Met: clear persona, clear business objective, testable acceptance criteria
  Missing: authentication mechanism undefined, allowable change types not
           specified, no quantitative target for processing time reduction

Missing Information:
  - What specific types of policy changes are permitted (coverage limits,
    named insured, endorsements)?
  - What is the downstream workflow after submission — underwriter queue or
    auto-processed?
  - What authentication method is used for broker login?

Confidence: medium    Escalation: false
```

### Baseline Output (same input, simple prompt)

The baseline prompt returns unstructured markdown — a user story and acceptance criteria in similar format, but with no DoR assessment, no missing information list, no confidence level, and no escalation mechanism. When given ambiguous inputs, the baseline improvises plausible details rather than flagging the gap.

---

## Setup and Usage

### Prerequisites

- Python 3.9+
- An Anthropic API key (`ANTHROPIC_API_KEY`)
- A Supabase project with `SUPABASE_URL` and `SUPABASE_ANON_KEY`

The grader should create a free Supabase project at [supabase.com](https://supabase.com), create a user via the Supabase Auth dashboard (or sign up through the app), and copy the project URL and anon key from the Supabase API settings page.

### Setup

```bash
git clone https://github.com/bradashepard-codes/StoryForge.git
cd StoryForge
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_ANON_KEY
```

### Run the App

```bash
python3 -m streamlit run enhanced_app.py
```

### Run the Evaluation

```bash
python3 eval/run_eval.py              # generates outputs/baseline_results.json and improved_results.json
python3 eval/compare_results.py       # prints dimension-level comparison table
```

Pre-generated outputs are committed to `outputs/` so the comparison can be run without re-calling the API.

---

## Repository Structure

```text
StoryForge/
├── app/
│   ├── dashboard_view.py     # Project list with Add/Edit modals
│   ├── db.py                 # All Supabase queries
│   ├── dor_checker.py        # DoR compliance utilities
│   ├── feature_view.py       # Story list, fan-out, Risk Signals, Risk Sweep
│   ├── llm_client.py         # All LLM calls (Sonnet + Haiku)
│   ├── login_view.py         # Sign in / sign up
│   ├── parser.py             # Pydantic models and output parsers
│   ├── project_view.py       # Feature list with Add/Edit/Enhance modals
│   └── prompts.py            # All prompt builders
├── eval/
│   ├── run_eval.py           # Evaluation runner (--runs flag for reliability)
│   ├── rubric.py             # Five-dimension scoring rubric
│   ├── compare_results.py    # Dimension-level delta analysis
│   └── test_cases.json       # 15 synthetic test cases
├── outputs/
│   ├── baseline_results.json # Raw baseline outputs
│   ├── improved_results.json # Raw improved outputs with parsed fields
│   ├── eval_scores.csv       # Manual rubric scores (1/3/5 per dimension)
│   └── parse_errors.log      # Parse failures (0 in the current run)
├── docs/
│   ├── project_plan.md
│   ├── technical_design.md
│   └── storyforge_enhanced_handoff.md
├── enhanced_app.py           # Entry point
├── .env.example
└── requirements.txt
```

---

## Governance

- All outputs require human review before backlog entry or sprint planning
- The system does not write to Jira, GitHub Issues, or any external system
- Only synthetic or user-authored inputs are used — no proprietary insurance data
- No API keys or secrets are committed to version control

---

## Project Team

| Role | Contributor |
|---|---|
| Technical Lead — Architecture, development, prompt engineering, evaluation | Brad Shepard |
| Presentation Lead — Test case support, evaluation write-up, demo, slides | Jeff Dunlao |
