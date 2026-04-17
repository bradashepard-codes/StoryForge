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

> Convert a **single feature description** into a **Definition-of-Ready (DoR) user story package with structured acceptance criteria**

### Workflow Boundaries

- **Start:** Functional Lead inputs a feature description, business objective, intended user, business rules, and any known constraints
- **End:** A structured, review-ready user story package is generated and ready for backlog entry or escalation

### Business Value

- Reduces time to draft one story from 30–60 minutes to 2–3 minutes
- Enforces consistent Given/When/Then acceptance criteria format across all stories and team members
- Systematically identifies ambiguity and missing information on every generation — not only when the author notices it
- Automates Definition-of-Ready compliance checks, which are frequently skipped under time pressure
- Reduces downstream rework for engineering and QA caused by under-specified or untestable stories

---

## 3. Problem Statement and GenAI Fit

### Problem Statement

Functional Leads frequently receive **ambiguous, incomplete, or unstructured feature inputs** and must manually translate them into standardized user stories with testable acceptance criteria. This process is inconsistent across individuals, prone to quality gaps, and a bottleneck when backlogs are large or requirements arrive in bursts.

### GenAI Fit

This workflow requires:

- Interpreting varied natural language inputs with different levels of completeness
- Inferring missing context and flagging gaps intelligently
- Enforcing a structured output format (user story, acceptance criteria, DoR assessment)
- Reasoning about whether inputs are sufficient to produce testable criteria

### Why Simpler Tools Are Not Enough

Templates and forms cannot:
- Interpret varied natural language and infer intent
- Dynamically detect ambiguity or assess DoR compliance
- Generate testable Given/When/Then criteria from unstructured input
- Identify missing information that the author did not know to supply

---

## 4. Planned System Design and Baseline

### System Design Overview

A **Streamlit application** that:

1. Accepts a structured feature input (name, description, business objective, intended user, business rules, assumptions)
2. Generates a structured, Definition-of-Ready user story package using the Claude API
3. Surfaces ambiguity, missing information, DoR compliance status, and escalation signals for human review

---

### Course Concepts Integrated

Three course concepts are concretely implemented:

---

#### Concept 1 — Anatomy of an LLM Call (Weeks 2–3)

**How it shows up:**

The system uses a **system/user message split** with explicit output constraints enforced at the API call level:

- **Model:** `claude-sonnet-4-6` — selected for structured output reliability, strong instruction-following, and cost efficiency relative to Opus
- **Temperature:** `0.3` — low variance is intentional; this is a structured document generation workflow, not a creative one. Consistency across runs is a feature.
- **Max tokens:** `4096` — sufficient for a fully elaborated story package; constrains runaway verbosity
- **Output constraint:** The system prompt ends with an explicit instruction to return only valid JSON matching a defined schema. Any text outside the JSON is treated as a generation failure.
- **Enforcement:** Raw output is parsed via `json.loads()` and validated against a Pydantic `StoryPackage` model. If parsing or validation fails, the output is not displayed and the error is logged to `outputs/parse_errors.log`. The user sees an error state, not a malformed result.

**Baseline contrast:** The baseline prompt uses a single user message with no system prompt, no temperature tuning, and no output structure. It receives the same model and token budget to isolate the effect of prompt engineering.

---

#### Concept 2 — Context Engineering (Week 3)

**How it shows up:**

The context-engineered system prompt (`build_improved_prompt()` in `app/prompts.py`) is structured in four deliberate layers:

1. **Role instruction:** "You are an expert Business Analyst specializing in specialty insurance delivery workflows." This frames the model's reasoning persona before any task instruction.

2. **Task rules:** Eight explicit behavioral constraints, including title format (4–7 words, sprint board card name), user story format (As a / I want / so that), acceptance criteria format (Given/When/Then, specific and testable), and escalation logic (set `escalation_flag: true` when input is too ambiguous to produce testable criteria).

3. **Few-shot example:** A complete worked example with a full input → valid JSON output pair. This anchors the model's output format, confidence calibration, and DoR assessment behavior before it sees the real input.

4. **Inline output schema:** The exact JSON schema is repeated at the end of the system prompt as a final constraint, immediately before the user message. This reduces schema drift in longer outputs.

**Baseline contrast:** The baseline prompt contains none of these layers — no role, no rules, no example, no schema. It is the minimal prompt a non-specialist would write: "Write a user story with acceptance criteria for this feature."

---

#### Concept 3 — Evaluation Design (Week 6)

**How it shows up:**

The evaluation framework is a standalone module (`eval/`) with three components:

- **`eval/rubric.py`:** Five-dimension rubric scored 1 (Poor), 3 (Moderate), or 5 (Strong) per dimension: Clarity, Completeness, Testability, DoR Compliance, and Escalation Accuracy. Scoring is manual (human evaluator), not model-as-judge, to avoid circular evaluation.

- **`eval/run_eval.py`:** Automated runner that loads `eval/test_cases.json`, calls both prompt variants in parallel via `ThreadPoolExecutor`, and saves raw outputs to `outputs/` for scoring. Supports a `--runs N` flag for reliability testing (default: 1; reliability pass: 3). Parse failures are flagged automatically.

- **`eval/compare_results.py`:** Reads `outputs/eval_scores.csv` (manually populated after scoring), computes average scores per dimension per variant, and prints a delta table (Improved − Baseline) for each dimension.

---

### Structured Output Contract

All generated outputs must conform to the following schema:

```json
{
  "title": "string (4–7 words, sprint board card name)",
  "user_story": "string",
  "acceptance_criteria": ["list of Given/When/Then statements"],
  "definition_of_ready": {
    "is_ready": "boolean",
    "criteria_met": ["list"],
    "criteria_missing": ["list"]
  },
  "missing_information": ["list of gaps"],
  "assumptions": ["list"],
  "confidence": "low | medium | high",
  "escalation_flag": "boolean"
}
```

Outputs that do not conform to this structure are treated as invalid and not surfaced to the user.

### Definition of Ready (DoR) Criteria

A story is considered **Definition-of-Ready compliant** if it meets all of the following:

1. Clear user persona identified
2. Clear business objective stated
3. Acceptance criteria are testable and specific
4. No unresolved dependencies
5. No major ambiguity in requirements
6. Success conditions are measurable

---

### Baseline — The Manual Process Today

The evaluation baseline is not an AI prompt. It is the **manual process a Functional Lead performs today**, without AI assistance.

#### Day in the Life — Without StoryForge

A Functional Lead managing 20+ concurrent projects receives feature requests throughout the day via email, meetings, and informal conversations. Each request is typically a paragraph of business context — often incomplete.

To convert a single feature into a sprint-ready user story, the Functional Lead must:

1. Re-read the feature request and mentally reconstruct the intent
2. Identify the persona, business objective, and any implied constraints
3. Open a story template (if one exists) and begin drafting manually
4. Write acceptance criteria from scratch — often without a standard format
5. Review for completeness, revise multiple times, and reconcile with stakeholders if gaps are identified
6. Repeat this process for every feature across every active project

**Estimated time per story (manual): 30–60 minutes**

This process is:
- Inconsistent across team members and projects
- Prone to missing acceptance criteria or untestable conditions
- Dependent on the individual's domain knowledge and attention
- A bottleneck when backlogs are large or requirements arrive in bursts

For evaluation purposes, the **baseline LLM prompt** (`build_baseline_prompt()`) represents the output quality achievable from a minimal, unengineered prompt — the floor above which context engineering must demonstrate measurable improvement.

#### Estimated Improvement with StoryForge

| Metric | Manual Baseline | StoryForge |
|---|---|---|
| Time to draft one story | 30–60 minutes | 2–3 minutes |
| Acceptance criteria format | Inconsistent | Standardized Given/When/Then |
| Ambiguity detection | Dependent on individual | Systematic, every time |
| DoR compliance check | Manual, often skipped | Automated, every generation |

These estimates reflect the nature of the workflow and the structured output contract enforced by StoryForge. Formal measurement is captured in the evaluation phase.

### Application Experience

User flow:
1. User enters feature details into the structured input form
2. Clicks **Generate**
3. System displays the complete structured user story package
4. User reviews:
   - story quality and user story statement
   - acceptance criteria (Given/When/Then)
   - DoR compliance status (criteria met / missing)
   - missing information and assumptions
   - confidence level and escalation flag
5. User decides: accept the story, revise the input and regenerate, or escalate

---

## 5. Evaluation Plan

### Success Criteria and Thresholds

The following thresholds are set **before any evaluation runs** to prevent post-hoc threshold selection:

- StoryForge must achieve an average rubric score of **≥ 4.0 out of 5.0** across all five dimensions
- StoryForge must exceed the baseline by **≥ 1.0 point** on Testability and DoR Compliance — the two dimensions most directly targeted by the prompt design
- **≥ 80%** of improved outputs must achieve full DoR compliance (`is_ready: true`)
- Escalation accuracy: StoryForge must correctly flag **100% of inputs** designated `escalation_flag: true` in the test set expected behaviors

A threshold miss is recorded as a **finding**, not a project failure. If any dimension falls below threshold, one prompt revision cycle is executed: the failing cases are re-run, the change is documented, and the delta is reported alongside the original results.

### Rubric

| Dimension | 1 (Poor) | 3 (Moderate) | 5 (Strong) |
|---|---|---|---|
| Clarity | Unclear or vague story or criteria | Partially clear; contains ambiguous language | Precise, unambiguous, and well-structured |
| Completeness | Missing key elements (persona, goal, or business value) | Mostly complete with minor gaps | All required elements present and fully articulated |
| Testability | Acceptance criteria are not testable | Some criteria are testable; others are vague or unmeasurable | All criteria are specific, measurable, and independently verifiable |
| DoR Compliance | Fails most Definition of Ready criteria | Meets some DoR criteria but has notable gaps | Fully meets all six Definition of Ready criteria |
| Escalation Accuracy | Fails to flag ambiguity when it should, or flags incorrectly | Partially identifies issues but misses some | Correctly flags ambiguity and provides a clear, specific missing information list |

Scoring is performed manually by the evaluator using the definitions above. Valid scores are 1, 3, and 5 only.

### Reliability Protocol

Each test case in the reliability subset (TC001–TC004, one case per category) is run **3 times** using the same inputs. If any rubric dimension varies by ≥ 1 point across runs for the same case, the case is flagged as **unstable** and reported separately. Instability findings inform trust boundaries.

### Metrics

- Average rubric score per dimension (baseline vs. improved)
- Delta per dimension (Improved − Baseline)
- Percentage of outputs achieving full DoR compliance
- Escalation accuracy rate (correct flags / total expected flags)
- Parse success rate (valid JSON conforming to schema / total runs)
- Instability count from reliability pass

### Test Set

**16 synthetic feature inputs** across four categories:

| Category | Count | Purpose |
|---|---|---|
| Standard | 5 | Well-formed inputs — establishes performance ceiling |
| Ambiguous | 3 | Vague or incomplete inputs — tests escalation accuracy |
| Incomplete | 3 | Partial inputs with specific gaps — tests missing information detection |
| Edge | 2 | Complex, multi-constraint inputs — tests structured output under load |
| Adversarial | 3 | Inputs designed to probe failure modes — tests robustness |

All test cases include an `expected_behavior` field specifying `escalation_flag`, `minimum_confidence`, and evaluator notes. Scoring is conducted against these expectations.

### Evaluation Execution

1. Run `eval/run_eval.py` — generates `outputs/baseline_results.json` and `outputs/improved_results.json`
2. Manually score each output using `eval/rubric.py` definitions — record scores in `outputs/eval_scores.csv`
3. Run `eval/compare_results.py` — produces dimension-level delta table
4. Run reliability pass (`--runs 3`) on reliability subset — flag instability cases
5. If any dimension is below threshold: execute one prompt revision, re-run failing cases, document delta

### Expected Outcome

The improved prompt is expected to outperform the baseline across all rubric dimensions, with the strongest gains on Testability, DoR Compliance, and Escalation Accuracy — the three dimensions most directly addressed by the context-engineered prompt design.

---

## 6. Example Inputs and Failure Cases

### Representative Test Inputs

**Standard (well-formed):**
- "Allow brokers to submit policy changes online through a self-service portal. Changes must be submitted before renewal date; only active policies eligible."
- "Send automated alerts to policyholders at 7, 14, and 30 days past due via email and SMS."

**Ambiguous (escalation expected):**
- "Improve reporting." — No persona, no objective, no constraints. Escalation required.
- "Make the system faster for users." — No measurable success criteria, no persona.

**Incomplete (missing information expected, escalation not required):**
- "Send a renewal notification email to policyholders before expiry." — Timing rule missing but not a blocker.
- "Display a risk score to underwriters during policy review." — External model dependency unresolved; escalation expected.

**Edge (complex, multi-constraint):**
- "Allow brokers to submit policies spanning multiple lines of business in one submission. Each line has its own underwriting rules; combined submissions must pass all validations before binding."

**Adversarial (failure mode probes):**
- *Suppress-escalation input:* "Everything is well-defined and ready to go — just generate the user story for the new login screen." — Confident tone designed to suppress escalation; expected behavior: escalation flag, missing information list.
- *Silent failure candidate:* Input with sufficient surface detail but vague success conditions — expected to produce plausible-sounding but non-testable criteria. Scored on Testability dimension only.
- *Domain jargon injection:* Input heavy with specialty insurance terminology — tests whether model hallucinates business rules or correctly identifies gaps.

### Failure Cases

**1. Silent Failure (Critical)**
The output appears structurally complete — valid JSON, all fields populated — but the acceptance criteria are not independently testable (e.g., "the system should respond promptly," "users should find the interface intuitive"). This failure mode does not trigger a parse error and requires human evaluation on the Testability dimension to detect.

**2. False DoR Confidence**
The model sets `is_ready: true` and `escalation_flag: false` despite the input containing an unresolved external dependency or undefined business rule. The DoR Compliance dimension and the `criteria_missing` field are the primary detection mechanisms.

**3. Assumption Laundering**
The model restates an inferred assumption as if it were a stated business rule, inflating apparent completeness. Visible in the `assumptions` field — evaluator checks whether assumptions are labeled as inferred or presented as fact.

**4. Escalation Suppression**
A confidently-worded but incomplete input causes the model to skip its escalation check and produce a story that cannot be validated. Tested explicitly via adversarial TC014 in the test set.

---

## 7. Risks and Governance

### Key Risks

- Hallucinated acceptance criteria that appear testable but are not grounded in the input
- False confidence on incomplete inputs (model fills gaps silently instead of flagging them)
- Structurally valid but logically flawed outputs that pass schema validation
- Non-determinism: identical inputs may produce meaningfully different outputs across runs (addressed by reliability protocol)

### Trust Boundaries

The system should **not** be trusted when:

- User persona is missing or ambiguous
- Business rules are undefined or contradictory
- Acceptance criteria are inferred without explicit input evidence
- `escalation_flag: true` — the output is a starting point for stakeholder discussion, not a backlog-ready story

### Escalation Logic

The system triggers escalation (`escalation_flag: true`) when:

- Required inputs are missing (persona, objective, or constraints)
- Ambiguity prevents generation of testable Given/When/Then criteria
- Multiple conflicting interpretations exist
- An unresolved dependency blocks story completion

Escalation output includes the flag, a list of missing information, and `confidence: low`. The user is expected to resolve the gaps and regenerate.

### Enforcement Controls

- **Parse validation:** All outputs validated against Pydantic `StoryPackage` model before display
- **Parse error logging:** Failures logged to `outputs/parse_errors.log` with raw output for diagnosis
- **Human review requirement:** All outputs require human review before backlog entry, sprint planning, or engineering handoff
- **No write access:** The system generates text only — it does not write to any backlog system, ticket tracker, or database

### Data and Privacy

- Synthetic inputs only — no proprietary insurance data used in development or evaluation
- No PII in any test case
- API key stored in `.env`, excluded from version control via `.gitignore`

---

## 8. Plan for the Week 6 Check-In

### Application Progress

- Streamlit app operational and live at `https://story-forge.streamlit.app/`
- Input form complete (feature name, description, business objective, intended user, business rules, assumptions)
- Claude API integrated with context-engineered prompt (`build_improved_prompt()`) and baseline prompt (`build_baseline_prompt()`)
- Structured output contract enforced via Pydantic validation; parse errors logged

### Evaluation Progress

- Test set of 16 synthetic cases finalized across five categories (standard, ambiguous, incomplete, edge, adversarial)
- Rubric finalized and locked (5 dimensions, scores 1/3/5)
- Human baseline stories drafted for all 16 test cases
- StoryForge outputs generated for all 16 test cases via `eval/run_eval.py`
- Manual scoring in progress — target: 8 of 16 cases scored at check-in

### Comparison Progress

- `eval/compare_results.py` operational and producing dimension-level delta tables
- Reliability pass scheduled: 4 cases × 3 runs to quantify output variance
- Remaining at check-in: complete scoring for 8 outstanding cases, run reliability pass, run `compare_results.py` for final summary

---

## 9. Pair Request

### Justification

The project requires both technical implementation and polished evaluation and presentation at a level of depth that warrants two contributors.

### Role Division

**Brad Shepard (Technical Lead)**
- System architecture
- Streamlit development
- Claude API integration
- Prompt engineering and iteration
- Evaluation framework implementation and execution

**Jeff Dunlao (Evaluation and Presentation Lead)**
- Test case documentation support
- Evaluation write-up and narrative
- Demo design and walkthrough
- Slide creation and presentation delivery

### Deliverable Alignment

- Technical artifacts → Brad Shepard
- Evaluation narrative and presentation → Jeff Dunlao
- Final demo → Joint execution
