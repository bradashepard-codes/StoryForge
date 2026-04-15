# Technical Design — StoryForge
## Definition-of-Ready User Story Generator for Specialty Insurance Functional Leads

## 1. Project Overview

**StoryForge** is a narrowly scoped Generative AI application designed for a **Functional Lead in a Specialty Insurance company** who manages a large portfolio of concurrent initiatives and must rapidly translate feature-level requirements into sprint-ready delivery artifacts.

The application will accept a **single feature description** and generate a **Definition-of-Ready user story package** that includes:
- a user story
- structured acceptance criteria
- a Definition of Ready assessment
- missing information / ambiguity flags
- a confidence and escalation signal

The system will use **Claude via API** and will explicitly compare:
1. a **baseline prompt-only version**
2. an **improved context-engineered version**

This project is intentionally designed to prioritize:
- narrow workflow fit
- structured outputs
- human review
- evaluation against a simpler baseline

---

## 2. Business Purpose

Functional Leads in specialty insurance frequently receive high-level business requirements that are too ambiguous or incomplete to place directly into a delivery backlog. Converting those requirements into usable user stories with acceptance criteria is time-consuming and inconsistent, especially across 20+ active projects.

This application is intended to improve the quality, speed, and consistency of that conversion step while preserving **human review before sprint entry**.

---

## 3. Core Technical Scope Statement

A Streamlit app that converts a single feature description into a Definition-of-Ready user story package with structured acceptance criteria, using Claude via API, and compares a baseline prompt against a context-engineered version.

---

## 4. In-Scope

The following capabilities are explicitly in scope for this project:

### 4.1 User Workflow
- One user: **Functional Lead**
- One workflow: **single feature description → single DoR-ready user story package**
- One unit of generation at a time
- Human review before downstream use

### 4.2 Application Capabilities
- Web-based Streamlit interface
- Manual text input for one feature description
- Submission to Anthropic Claude API
- Generation of:
  - user story
  - structured acceptance criteria
  - Definition of Ready assessment
  - missing information / assumptions
  - escalation or confidence flag
- Side-by-side or selectable comparison of:
  - baseline prompt output
  - context-engineered prompt output

### 4.3 Technical Design Elements
- Python-based application
- Streamlit UI
- Anthropic API integration
- JSON or schema-like structured response handling
- Local test dataset for evaluation
- Baseline vs improved prompt comparison
- Evaluation support module or script

### 4.4 Governance Controls
- Human review boundary before sprint entry
- Explicit escalation when requirements are too ambiguous
- Logging of generated outputs for evaluation and review
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
- Authentication / SSO
- Role-based access control
- Production-grade observability stack
- Database-backed persistence
- Multi-user collaboration
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
1. Functional Lead enters one feature description into the app
2. App packages the input into two prompt paths:
   - baseline prompt
   - context-engineered prompt
3. Claude API generates candidate outputs
4. Application parses and displays the generated story package
5. User reviews output
6. User decides whether the story is:
   - acceptable
   - needs edits
   - should be escalated due to ambiguity
7. Evaluation module stores or compares output against rubric/test cases

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
| 4 | Baseline generation | Anthropic API call | Minimal prompt | Python / API JSON |
| 5 | Improved generation | Anthropic API call | Context-engineered prompt with constraints and output contract | Python / API JSON |
| 6 | Parse responses | Output parser | Raw model outputs | Python / JSON |
| 7 | Render results | Streamlit UI | Parsed story package | UI components |
| 8 | Log outputs for review | Local files | Inputs, outputs, metadata | JSON / CSV |
| 9 | Evaluate against test set | Evaluation script | Saved test cases, rubric dimensions | Python |
| 10 | Compare baseline vs improved | Analysis module | Scored outputs | Python / CSV / markdown tables |

---

## 9. Logical Components

## 9.1 Streamlit App Layer
Responsible for:
- collecting feature input
- triggering generation
- showing baseline vs improved outputs
- displaying structured sections cleanly

### Expected Inputs
- Feature name
- Feature description
- Business objective
- Intended end user
- Business rules or constraints
- Optional notes / assumptions

### Expected UI Sections
- Feature Input Form
- Baseline Output
- Improved Output
- DoR Assessment
- Missing Information / Escalation
- Evaluation View

---

## 9.2 Prompt Builder Layer
Responsible for constructing two prompt variants.

### Baseline Prompt
A simple prompt with minimal structure, intended to serve as the comparison benchmark.

Example design intent:
- basic instruction
- limited constraints
- no or minimal output contract
- no few-shot examples

### Context-Engineered Prompt
An improved prompt that reflects course concepts.

Expected design elements:
- explicit role
- explicit task
- constraints
- output contract
- Definition of Ready lens
- few-shot examples
- escalation instructions for ambiguity

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

### Target Output Structure
- `user_story`
- `acceptance_criteria`
- `definition_of_ready_status`
- `missing_information`
- `assumptions`
- `confidence`
- `escalation_flag`

---

## 9.5 Evaluation Layer
Responsible for:
- running test cases
- scoring baseline and improved variants
- producing evidence for project write-up

### Evaluation Dimensions
- clarity
- completeness
- testability of acceptance criteria
- alignment to Definition of Ready
- proper escalation when input is insufficient
- output structure compliance

### Evaluation Data
- manually created synthetic feature inputs
- expected behavior notes
- rubric-based scoring sheets

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
The Python backend constructs two prompt versions:
- a baseline prompt
- a context-engineered prompt

The improved version includes stronger behavioral controls, formatting, and DoR expectations.

### Step 3 — Claude API Execution
The system sends both requests to Claude via API. Each request returns a candidate story package.

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
- baseline prompt
- improved prompt  
using a fixed test set and rubric dimensions.

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
1. the app runs locally from the repository
2. a user can submit one feature and receive a structured story package
3. baseline and improved prompt variants can be compared
4. the improved version shows measurable gains on the evaluation rubric
5. the system flags cases where human escalation is appropriate

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
