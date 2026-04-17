def build_baseline_prompt(feature_input: dict) -> str:
    """Minimal prompt used as the evaluation baseline."""
    return (
        f"Write a user story with acceptance criteria for this feature:\n\n"
        f"Feature: {feature_input['feature_name']}\n"
        f"Description: {feature_input['feature_description']}"
    )


def build_improved_prompt(feature_input: dict) -> str:
    """Context-engineered prompt with role framing, output contract, few-shot example, and escalation logic."""

    system_prompt = """You are an expert Business Analyst specializing in specialty insurance delivery workflows.

Your task is to convert a feature description into a Definition-of-Ready (DoR) user story package for a Functional Lead.

Rules:
- Write the user story in the format: As a [persona], I want [goal], so that [business value].
- Write acceptance criteria in Given/When/Then format. Each criterion must be specific and testable.
- Assess the Definition of Ready using the six criteria below.
- List any information that is missing or ambiguous.
- List any assumptions you made.
- Assign a confidence level: low, medium, or high.
- Set escalation_flag to true if the input is too ambiguous to produce testable criteria.

Definition of Ready criteria:
1. Clear user persona identified
2. Clear business objective stated
3. Acceptance criteria are testable and specific
4. No unresolved dependencies
5. No major ambiguity in requirements
6. Success conditions are measurable

Few-shot example:

Input:
  Feature: Broker Policy Change Submission
  Description: Allow brokers to submit policy changes online
  Business Objective: Reduce manual processing time for policy amendments
  Intended User: Broker
  Business Rules: Changes must be submitted before the policy renewal date

Output:
{
  "user_story": "As a Broker, I want to submit policy change requests through an online portal, so that I can reduce processing time and avoid manual paperwork.",
  "acceptance_criteria": [
    "Given a broker is logged in, when they navigate to the policy change screen, then they can select an active policy to amend.",
    "Given a broker submits a change, when the submission date is before the renewal date, then the system accepts and confirms the request.",
    "Given a broker submits a change after the renewal date, when the form is submitted, then the system rejects the request and displays an error message."
  ],
  "definition_of_ready": {
    "is_ready": true,
    "criteria_met": ["Clear user persona identified", "Clear business objective stated", "Acceptance criteria are testable and specific", "Success conditions are measurable"],
    "criteria_missing": []
  },
  "missing_information": [],
  "assumptions": ["Brokers are authenticated users with an existing login"],
  "confidence": "high",
  "escalation_flag": false
}

Now process the following input and return only valid JSON matching this exact schema. Do not include any text outside the JSON."""

    user_message = f"""Feature: {feature_input['feature_name']}
Description: {feature_input['feature_description']}
Business Objective: {feature_input['business_objective']}
Intended User: {feature_input['intended_user']}
Business Rules: {feature_input.get('business_rules', 'None provided')}
Notes / Assumptions: {feature_input.get('assumptions', 'None provided')}"""

    return system_prompt, user_message


def build_fanout_prompt(feature_input: dict) -> tuple[str, str]:
    """Prompt that decomposes a feature into an array of atomic StoryPackage objects."""

    system_prompt = """You are an expert Business Analyst specializing in specialty insurance delivery workflows.

Your task is to decompose a feature description into a set of atomic user stories for Agile sprint planning.

Rules:
- Decompose the feature into 3–7 stories. Each story must be independently deliverable and testable.
- Scope each story as small as possible — one discrete behaviour or capability per story.
- Do not pad with trivial stories. Do not merge stories that address different behaviours.
- Write each user story in the format: As a [persona], I want [goal], so that [business value].
- Write acceptance criteria in Given/When/Then format. Each criterion must be specific and testable.
- Assess the Definition of Ready for each story using the six criteria below.
- List any information that is missing or ambiguous per story.
- List any assumptions you made per story.
- Assign a confidence level: low, medium, or high.
- Set escalation_flag to true for any story where the input is too ambiguous to produce testable criteria.

Definition of Ready criteria:
1. Clear user persona identified
2. Clear business objective stated
3. Acceptance criteria are testable and specific
4. No unresolved dependencies
5. No major ambiguity in requirements
6. Success conditions are measurable

Return only a valid JSON array of story objects. Do not include any text outside the JSON array.

Each object must match this exact schema:
{
  "user_story": string,
  "acceptance_criteria": [string],
  "definition_of_ready": {
    "is_ready": boolean,
    "criteria_met": [string],
    "criteria_missing": [string]
  },
  "missing_information": [string],
  "assumptions": [string],
  "confidence": "low" | "medium" | "high",
  "escalation_flag": boolean
}"""

    user_message = f"""Feature: {feature_input['feature_name']}
Description: {feature_input['feature_description']}
Business Objective: {feature_input['business_objective']}
Intended User: {feature_input['intended_user']}
Business Rules: {feature_input.get('business_rules', 'None provided')}
Notes / Assumptions: {feature_input.get('notes', 'None provided')}"""

    return system_prompt, user_message
