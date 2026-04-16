# Project Plan — StoryForge 

## Definition-of-Ready User Story Generator for Specialty Insurance Functional Leads

---

## 1. Project Title

**StoryForge: Generating Definition-of-Ready User Stories from Feature Descriptions**

---

## 2. Target User, Workflow, and Business Value

### Target User
The primary user is a **Functional Lead in a Specialty Insurance company** responsible for managing a portfolio of 20+ concurrent projects and translating business requirements into delivery-ready backlog items.

### Workflow
> Convert a **single feature description** into a **Definition-of-Ready (DoR) user story with structured acceptance criteria**

### Workflow Boundaries
- **Start:** Functional Lead inputs a feature description
- **End:** A structured, review-ready user story package is generated

### Business Value
- Reduces time to create backlog-ready stories
- Improves consistency and quality of acceptance criteria
- Identifies ambiguity before sprint entry
- Reduces downstream rework for engineering and QA

---

## 3. Problem Statement and GenAI Fit

### Problem Statement
Functional Leads frequently receive **ambiguous, incomplete, or unstructured feature inputs** and must manually translate them into standardized user stories with testable acceptance criteria. This process is inconsistent and prone to quality gaps.

### GenAI Fit
This workflow requires:
- transformation of unstructured input into structured output
- reasoning about missing information
- enforcing standardized formats (user stories, acceptance criteria)

### Why Simpler Tools Are Not Enough
Templates and forms cannot:
- interpret varied natural language inputs
- infer missing context
- dynamically generate testable acceptance criteria
- flag ambiguity intelligently

---

## 4. Planned System Design and Baseline

### System Design Overview
A **Streamlit application** that:
1. accepts a feature description
2. generates outputs using Claude API
3. compares:
   - baseline prompt
   - context-engineered prompt

---

### Design Justification

This system is intentionally designed as a **single-step generation workflow** rather than a multi-step or multi-agent system.

- **Why not multi-step orchestration:**  
  The task is bounded to one feature → one story. Multi-step pipelines introduce unnecessary complexity without improving evaluation clarity.

- **Why not RAG:**  
  The system does not depend on external documents. Adding retrieval would increase complexity without meaningful benefit for this workflow.

- **Why structured outputs:**  
  Structured outputs enable:
  - consistent evaluation
  - easier comparison across runs
  - enforcement of Definition-of-Ready criteria

This design prioritizes **evaluation rigor, reliability, and scope discipline** over technical complexity.

---

### Structured Output Contract 

All generated outputs must conform to the following schema:

```json
{
  "user_story": "string",
  "acceptance_criteria": ["list of Given/When/Then statements"],
  "definition_of_ready": {
    "is_ready": "true/false",
    "criteria_met": ["list"],
    "criteria_missing": ["list"]
  },
  "missing_information": ["list of gaps"],
  "assumptions": ["list"],
  "confidence": "low/medium/high",
  "escalation_flag": "true/false"
}
```

Outputs that do not conform to this structure will be treated as invalid.

### Definition of Ready (DoR) Criteria

A story is considered **Definition-of-Ready compliant** if it meets the following:

- clear user persona identified
- clear business objective stated
- acceptance criteria are **testable and specific**
- no unresolved dependencies
- no major ambiguity in requirements
- success conditions are measurable

### Course Concepts Integrated

#### Context Engineering
- role-based prompting
- structured output constraints
- few-shot examples
- ambiguity detection instructions

#### Evaluation Design
- rubric-based scoring system
- baseline vs improved comparison
- test set including edge cases

### Baseline

Baseline prompt:
> "Write a user story with acceptance criteria for this feature."

This provides a minimal benchmark for comparison.

### Application Experience

User flow:
1. User enters feature details into form
2. Clicks **Generate**
3. System displays:
   - baseline output
   - improved output
4. User reviews:
   - story quality
   - acceptance criteria
   - DoR status
5. User decides:
   - accept
   - revise
   - escalate

## 5. Evaluation Plan

### Success Criteria

The improved system must demonstrate:

- higher average rubric scores than baseline
- more testable acceptance criteria
- better identification of ambiguity
- improved Definition-of-Ready compliance

### Rubric 

| Dimension | 1 (Poor) | 3 (Moderate) | 5 (Strong) |
|----------|----------|--------------|------------|
| Clarity | unclear or vague | partially clear | precise and unambiguous |
| Completeness | missing key elements | mostly complete | fully complete |
| Testability | not testable | partially testable | fully testable |
| DoR Compliance | fails most criteria | meets some criteria | fully meets DoR |
| Escalation Accuracy | fails to flag issues | partially flags issues | correctly flags ambiguity |

### Metrics

- average rubric score per dimension
- percentage of outputs meeting DoR
- percentage of acceptance criteria that are testable
- escalation accuracy rate

### Test Set

- 12–20 synthetic feature inputs
- Includes:
  - standard use cases
  - ambiguous cases that should trigger escalation
  - incomplete inputs

### Evaluation Execution

- primary scoring: manual evaluation by Brad
- secondary validation: spot-check comparison across outputs
- consistent scoring applied across all outputs using the same rubric

### Expected Outcome

The improved prompt is expected to:
- outperform baseline across all rubric dimensions
- show strongest gains in:
  - testability
  - DoR compliance
  - escalation accuracy

## 6. Example Inputs and Failure Cases

### Example Inputs

- "Allow brokers to submit policy changes online"
- "Add real-time underwriting validation"
- "Create dashboard for claims tracking"
- "Send alerts for overdue premiums"
- "Enable document upload in submission flow"

### Failure Cases

1. **Ambiguous Input**
   - Example: "Improve reporting"
   - Expected behavior: escalation flag triggered

2. **Missing Context**
   - Example: no user persona or constraints
   - Expected behavior: missing information identified

3. **Silent Failure Risk (Critical)**
   - Output appears complete but includes:
     - non-testable criteria
     - incorrect assumptions
   - Must be captured in evaluation

## 7. Risks and Governance 

### Key Risks
- hallucinated acceptance criteria
- false confidence on incomplete inputs
- structurally correct but logically flawed outputs

### Trust Boundaries 

The system should **not** be trusted when:
- user persona is missing
- business rules are undefined
- acceptance criteria are inferred without evidence
- ambiguity is not resolved

### Escalation Logic

The system will trigger escalation when:
- required inputs are missing
- ambiguity prevents testable criteria
- multiple interpretations exist

Escalation output includes:
- `escalation_flag = true`
- list of missing information
- explanation of why the story is not DoR-ready

### Human Review Requirement

All outputs must be reviewed before:
- backlog entry
- sprint planning
- engineering handoff

### Data and Privacy

- synthetic inputs only
- no proprietary insurance data
- secure API key handling

## 8. Plan for Week 6 Check-In

### Application Progress
- Streamlit app operational
- input form complete
- Claude API integrated
- baseline and improved prompts implemented

### Evaluation Progress
- test set created with 10–12 cases
- rubric finalized
- initial scoring completed

### Comparison Progress
- baseline vs improved results generated
- early insights documented

## 9. Pair Request

### Justification
The project requires both:
- technical implementation
- polished evaluation and presentation

### Role Division

**Brad Shepard (Technical Lead)**
- system architecture
- Streamlit development
- Claude API integration
- prompt engineering
- evaluation execution and analysis

**Jeff Dunlao (Presentation Lead)**
- test case documentation support
- evaluation write-up support
- demo design and walkthrough
- slide creation and narrative
- presentation delivery support

### Deliverable Alignment

- Technical artifacts → Brad Shepard
- Evaluation narrative and presentation → Jeff Dunlao
- Final demo → Joint Execution
