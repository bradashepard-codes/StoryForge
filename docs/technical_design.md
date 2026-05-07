# Technical Design — StoryForge
## Two-Workflow Generative AI Application for Specialty Insurance Functional Leads

## 1. Project Overview

**StoryForge** is a narrowly scoped Generative AI application designed for a **Functional Lead in a Specialty Insurance company** who manages a large portfolio of concurrent initiatives and must rapidly translate feature-level requirements into sprint-ready delivery artifacts.

The application provides two independent generative workflows on a single feature input:

**Workflow 1 — User Story Generation:** Accepts a feature description and generates a Definition-of-Ready user story package including:
- a user story (As a / I want / so that)
- structured acceptance criteria (Given/When/Then)
- a Definition of Ready assessment
- missing information / ambiguity flags
- a confidence and escalation signal

**Workflow 2 — Risk and Requirement Expansion:** Takes the same feature input and surfaces:
- edge cases and boundary conditions
- external dependencies
- ambiguities and conflicting requirements
- missing requirements (security, compliance, error handling, UX)
- an overall severity assessment (low / medium / high)

Both workflows use **Claude via API** with context-engineered prompts, structured output contracts, and Pydantic validation. Workflow 1 is evaluated against a human manual baseline. Workflow 2 is advisory and evaluated qualitatively.

This project is intentionally designed to prioritize:
- narrow workflow fit
- structured outputs
- human review
- evaluation against the manual process it replaces

---

## 2. Business Purpose

Functional Leads in specialty insurance frequently receive high-level business requirements that are too ambiguous or incomplete to place directly into a delivery backlog. Converting those requirements into usable user stories with acceptance criteria is time-consuming and inconsistent, especially across 20+ active projects.

This application is intended to improve the quality, speed, and consistency of that conversion step while preserving **human review before sprint entry**.

---

## 3. Core Technical Scope Statement

A Streamlit application with Supabase authentication and persistent storage that converts a single feature description into two complementary outputs: (1) a Definition-of-Ready user story package with structured acceptance criteria, and (2) a structured risk and requirement expansion that surfaces edge cases, dependencies, ambiguities, and missing requirements. Both workflows use Claude via API with context-engineered prompts and Pydantic-validated JSON output. Workflow 1 is evaluated against a human manual baseline.

---

## 4. In-Scope

The following capabilities are explicitly in scope for this project:

### 4.1 User Workflow
- One user: **Functional Lead**
- Two workflows on the same input: **User Story Generation** and **Risk and Requirement Expansion**
- One unit of generation at a time per workflow
- Human review before downstream use

### 4.2 Application Capabilities
- Web-based Streamlit interface with email/password authentication (Supabase)
- Persistent project → feature → user story hierarchy (Supabase PostgreSQL with RLS)
- AI-powered feature description enhancement (optional pre-step before story generation)
- **Workflow 1 — User Story Generation:**
  - Fan-out mode: decomposes one enhanced feature into 3–7 atomic user stories
  - Single-story mode: generates one story from a full input form
  - Outputs: user story, acceptance criteria, DoR assessment, missing information, assumptions, confidence, escalation flag
- **Workflow 2 — Risk and Requirement Expansion:**
  - Generates a structured risk analysis for any feature
  - Outputs: edge cases, dependencies, ambiguities, missing requirements, severity summary
- Source badges on all saved stories (AI-Generated, Manual, Edited)

### 4.3 Technical Design Elements
- Python-based application
- Streamlit UI with `st.dialog` modal pattern for all create/generate actions
- Anthropic Claude API integration (`claude-sonnet-4-6`)
- Pydantic-validated structured JSON output for both workflows
- Supabase auth and PostgreSQL database with row-level security
- Local test dataset for evaluation
- Human baseline vs. StoryForge output comparison in evaluation layer

### 4.4 Governance Controls
- Human review boundary before sprint entry
- Explicit escalation when requirements are too ambiguous
- Parse-or-reject enforcement — invalid outputs never shown to user
- Logging of parse errors for diagnosis
- Synthetic or manually created sample inputs only

---

## 5. Out-of-Scope

The following are explicitly out of scope to keep the project aligned to capstone requirements and technically manageable:

### 5.1 Workflow Scope Exclusions
- Full backlog generation across multiple features
- Epic decomposition into many stories
- Automatic prioritization across a portfolio
- Full BRD or requirements document generation
- Autonomous backlog grooming

### 5.2 Integration Exclusions
- Jira integration
- Azure DevOps integration
- Figma API integration
- GitHub issue creation automation
- Slack, Teams, or email workflow integration

### 5.3 AI / System Complexity Exclusions
- Multi-agent orchestration
- ReAct-style agent loops
- Tool-calling workflows
- Retrieval-augmented generation over enterprise documents
- Fine-tuning custom models
- Long-context document ingestion pipelines
- OCR or file parsing of uploaded business documents

### 5.4 Enterprise Platform Exclusions
- SSO / enterprise identity providers
- Role-based access control and multi-user collaboration
- Production-grade observability stack
- Real-time workflow orchestration

### 5.5 UX Exclusions
- Figma wireframe generation
- Pixel-perfect UI design generation
- Design system enforcement

---

## 6. Primary User

### Functional Lead in Specialty Insurance
A delivery-facing business lead responsible for:
- capturing high-level business requirements
- translating requirements into feature backlog items
- creating user stories and acceptance criteria
- ensuring backlog items meet Definition of Ready expectations
- occasionally partnering with design or engineering for downstream elaboration

---

## 7. End-to-End Workflow

## 7.1 Functional Workflow

**Setup:**
1. Functional Lead signs in and navigates to a project and feature

**Workflow 1 — User Story Generation:**
2. App constructs a context-engineered prompt from the feature input
3. Claude API generates the structured story package (fan-out or single-story mode)
4. Application parses and validates output against `StoryPackage` schema; displays on success
5. User reviews story, acceptance criteria, DoR assessment, missing information, confidence, escalation flag
6. User saves selected stories or escalates

**Workflow 2 — Risk and Requirement Expansion:**
7. User opens the Analyze Risks section on the same feature
8. App constructs the risk expansion prompt with optional additional context
9. Claude API generates a structured risk analysis
10. Application parses and validates output against `RiskAnalysisPackage` schema; displays on success
11. User reviews edge cases, dependencies, ambiguities, missing requirements, and severity
12. User uses findings to strengthen the feature or flag issues before sprint planning

**Evaluation:**
13. Evaluation module compares Workflow 1 StoryForge outputs against human baseline using rubric scoring

---

## 8. Technical Architecture

## 8.1 Architecture Summary

**Frontend**
- Streamlit web application

**Backend**
- Python application layer

**LLM Provider**
- Anthropic Claude API

**Evaluation Layer**
- Local Python evaluation scripts
- Static test set stored in JSON or CSV

**Storage**
- Local flat files during capstone development
- No production database required

---

## 8.2 Technical Workflow by Step

| Step | Function | Application / Component | Data Used | Language / Format |
|---|---|---|---|---|
| 1 | User enters feature details | Streamlit UI | Feature title, description, business objective, assumptions | Text form inputs |
| 2 | App validates required fields | Python backend | Input strings | Python |
| 3 | App prepares prompt payloads | Prompt builder module | Input + system prompt + few-shot examples | Python strings / JSON-like structures |
| 4 | Generate story package | Anthropic API call | Context-engineered prompt with constraints and output contract | Python / API JSON |
| 5 | Parse response | Output parser | Raw model output | Python / JSON |
| 6 | Render results | Streamlit UI | Parsed story package | UI components |
| 7 | Log outputs for review | Local files | Inputs, outputs, metadata | JSON / CSV |
| 8 | Evaluate against test set | Evaluation script | Saved test cases, rubric dimensions | Python |
| 9 | Compare human baseline vs StoryForge | Analysis module | Human-authored stories and StoryForge outputs, scored | Python / CSV / markdown tables |

---

## 9. Logical Components

## 9.1 Streamlit App Layer
Responsible for:
- collecting feature input
- triggering generation
- displaying the structured story package cleanly
- surfacing DoR status, escalation flags, and missing information

### Expected Inputs
- Feature name
- Feature description
- Business objective
- Intended end user
- Business rules or constraints
- Optional notes / assumptions

### Expected UI Sections
- Feature Input Form
- Generated User Story and Acceptance Criteria
- DoR Assessment
- Missing Information / Escalation

---

## 9.2 Prompt Builder Layer
Responsible for constructing all context-engineered prompts.

### Workflow 1 — Story Generation Prompt (`build_improved_prompt`, `build_fanout_prompt`)
Design elements:
- Role: Business Analyst in specialty insurance
- Explicit task and output contract
- Definition of Ready lens with six criteria
- Few-shot example (input → full JSON output)
- Escalation instructions for ambiguous inputs
- Fan-out variant: decomposes feature into 3–7 atomic stories (JSON array)

### Workflow 2 — Risk Expansion Prompt (`build_risk_expansion_prompt`)
Design elements:
- Role: QA Lead and requirements analyst in specialty insurance
- Explicit task and output contract
- Seven behavioral constraints (specificity, severity assignment, feature-specific findings)
- Few-shot example (same broker policy change feature → full risk analysis JSON)
- Output schema: edge_cases, dependencies, ambiguities, missing_requirements, severity_summary

---

## 9.3 LLM Integration Layer
Responsible for:
- connecting to Claude through the Anthropic API
- sending prompt payloads
- handling responses
- capturing runtime metadata

### Likely API Inputs
- model name
- system prompt
- user message
- max tokens
- temperature
- structured output instructions if supported

---

## 9.4 Output Parsing and Validation Layer
Responsible for:
- turning model output into reliable sections
- validating that all required fields are present
- handling malformed or incomplete outputs

### Workflow 1 — `StoryPackage` (Pydantic model)
- `title`, `user_story`, `acceptance_criteria`
- `definition_of_ready` (is_ready, criteria_met, criteria_missing)
- `missing_information`, `assumptions`, `confidence`, `escalation_flag`

### Workflow 2 — `RiskAnalysisPackage` (Pydantic model)
- `edge_cases`, `dependencies`, `ambiguities`, `missing_requirements`
- `severity_summary` (validated: low / medium / high)

Both models use field validators. Outputs that fail validation are rejected and logged to `outputs/parse_errors.log`; the user sees an error state, not a malformed result.

---

## 9.5 Evaluation Layer
Responsible for:
- running test cases through StoryForge
- scoring StoryForge outputs against human baseline using the rubric
- producing evidence for project write-up

### Evaluation Dimensions
- clarity
- completeness
- testability of acceptance criteria
- alignment to Definition of Ready
- proper escalation when input is insufficient
- output structure compliance

### Evaluation Data
- 12 manually created synthetic feature inputs across 4 categories
- human-authored baseline stories (one per test case, written as a Functional Lead would today)
- StoryForge-generated outputs for each test case
- rubric-based scoring sheets comparing both

---

## 10. Data Design

## 10.1 Input Data
All inputs will be manually entered or synthetically created.

### Examples
- specialty insurance underwriting workflow feature
- claims intake feature
- policy servicing feature
- premium audit workflow feature

### Privacy Rule
No real client data, production documents, PII, secrets, or proprietary enterprise content will be used.

---

## 10.2 Output Data
Generated outputs may be saved locally for:
- evaluation
- rubric scoring
- baseline comparison
- demo evidence

Suggested flat-file storage:
- `data/test_cases.json`
- `outputs/baseline_results.json`
- `outputs/improved_results.json`
- `outputs/eval_scores.csv`

---

## 11. Proposed Repository Structure

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
│   ├── technical_design.md
│   ├── project_plan.md
│   └── evaluation_notes.md
├── .env.example
├── requirements.txt
├── README.md
└── streamlit_app.py
```

## 12. Technology Stack

### Core Stack
- **Language:** Python
- **UI Framework:** Streamlit
- **IDE:** Visual Studio Code
- **LLM Provider:** Anthropic Claude API
- **Version Control:** GitHub
- **Environment Management:** `.env` file for API key
- **Dependency Management:** `requirements.txt`

### Suggested Libraries
- `streamlit`
- `anthropic`
- `python-dotenv`
- `pydantic` or equivalent for schema validation
- `pandas` for evaluation analysis

## 13. Workflow Architecture Narrative

### Step 1 — Feature Input
The Functional Lead enters a single feature request into the Streamlit interface. This is the only required business input and represents the top of the workflow.

### Step 2 — Prompt Construction
The Python backend constructs the context-engineered prompt, incorporating role framing, output contract, few-shot examples, and DoR expectations.

### Step 3 — Claude API Execution
The system sends the request to Claude via API and receives a structured story package.

### Step 4 — Parsing and Structuring
The application validates and normalizes the returned text into predefined sections so that outputs are operational and comparable.

### Step 5 — User Review
The user inspects the result, especially:
- acceptance criteria quality
- missing information
- escalation recommendations

### Step 6 — Evaluation and Comparison
For project scoring and evidence, test cases are run through both versions and scored using a rubric. This establishes whether context engineering improves outcomes relative to the baseline.

## 14. Course Concepts Embedded in the Design

This design intentionally operationalizes at least two required course concepts.

### 14.1 Anatomy of an LLM Call
The application explicitly controls:
- system instructions
- user input
- temperature
- max tokens
- output structure

### 14.2 Context Engineering
The improved version will use:
- role framing
- task framing
- constraints
- output contract
- few-shot examples
- escalation rules

### 14.3 Evaluation Design
The project will compare:
- human-authored baseline stories (the manual process)
- StoryForge-generated outputs

Using a fixed 12-case test set and five-dimension rubric to measure improvement in clarity, completeness, testability, DoR compliance, and escalation accuracy.

### 14.4 Governance and Deployment Controls
The design includes:
- human review boundary
- escalation for ambiguity
- no autonomous downstream action
- no direct system-of-record integration

## 15. Human Review and Trust Boundary

This project is designed as a **decision-support and drafting tool**, not an autonomous delivery workflow.

### The system may:
- generate draft user stories
- generate candidate acceptance criteria
- identify ambiguity
- suggest whether the feature is not ready

### The system may not:
- automatically place items into sprint backlog
- create work in Jira
- make delivery governance decisions autonomously
- approve Definition of Ready status without human review

### Trust Boundary
Human review is required before any generated output is treated as sprint-ready.

## 16. Failure Modes

Expected failure modes include:
- vague user story generation from weak inputs
- acceptance criteria that are not testable
- hallucinated assumptions
- false confidence on ambiguous requirements
- incomplete DoR checks
- over-structured output that appears correct but is logically weak

These failure modes will be explicitly included in evaluation and governance write-up.

## 17. Security, Privacy, and Cost Approach

### Security / Privacy
- Use only synthetic or user-authored sample data
- Never commit API keys
- Keep `.env` out of version control
- No proprietary insurance client information

### Cost
- Use limited-volume API calls during development
- Keep prompts narrow and token-efficient
- Evaluate on a modest but credible synthetic test set

## 18. Success Criteria

A successful technical implementation will demonstrate that:
1. the app runs locally and accepts authenticated user sessions
2. a user can submit one feature and receive a structured story package in under 30 seconds (Workflow 1)
3. a user can submit the same feature and receive a structured risk analysis in under 30 seconds (Workflow 2)
4. StoryForge Workflow 1 outputs score measurably higher than human baseline stories on the evaluation rubric
5. the system correctly flags cases where human escalation is appropriate
6. time-to-draft is reduced from 30–60 minutes to under 3 minutes per story
7. all structured outputs are validated against Pydantic schemas before display; invalid outputs are never surfaced

## 19. Future Extensions (Not Part of Current Scope)

Potential future enhancements, intentionally deferred:
- Jira or Azure DevOps integration
- Figma prompt or design export
- RAG over business requirement libraries
- multi-story decomposition
- insurer-specific playbooks or templates
- team collaboration and approval routing

These are intentionally excluded from the current capstone to preserve scope discipline.

## 20. Summary

StoryForge is a deliberately narrow GenAI application focused on one high-value business workflow: converting a single feature description into a Definition-of-Ready user story package.

The system is intentionally lightweight:
- Python
- Streamlit
- Claude API
- local evaluation harness

Its strength is not technical sprawl. Its strength is controlled scope, structured outputs, measurable comparison, and explicit governance.
