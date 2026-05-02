# StoryForge Enhanced — Project Handoff

**Branch:** `feature/storyforge-enhanced`
**Entry point:** `python3 -m streamlit run enhanced_app.py`
**Last updated:** April 2026
**Status:** Actively in development — core workflows complete, story edit workflow not yet built

---

## What This Is

StoryForge Enhanced is a second-generation version of the capstone StoryForge app. It is **not** the capstone deliverable. It extends the base app with user authentication, a persistent cloud database, a full project hierarchy, and an AI-powered fan-out story generation workflow. It lives permanently on the `feature/storyforge-enhanced` branch and must not be merged to `dev` or `main` without explicit approval.

---

## What It Can Do Today

### Authentication
- Email/password sign in and sign up via Supabase Auth
- Session persisted across Streamlit reruns via `restore_session()` called at the top of `main()` on every rerun — this is a critical fix; removing it will break auth on navigation
- Sign out clears all session state

### Project Management (Dashboard)
- View all projects belonging to the authenticated user with feature and story counts per card
- Add a new project via modal dialog (name, owner, status)
- Edit project metadata (name, owner, status) via modal dialog
- Delete a project inline
- Status options: Active, On Hold, Complete, Cancelled

### Feature Management (Project View)
- View all features for a project
- Add a new feature via modal dialog with optional AI description enhancement
- Edit a feature's name and description via modal dialog with optional AI enhancement
- Bulk delete features via modal with multi-select checkboxes
- Navigate into a feature to view its stories
- Features flagged as `is_enhanced = true` when the user accepts the AI-enhanced description — this flag unlocks fan-out story generation

### AI Description Enhancement
- Available in both Add Feature and Edit Feature modals
- User enters a description → clicks "✨ Enhance Description" → LLM refines it (preserves all original intent, improves clarity and specificity)
- Side-by-side comparison of Original vs. Enhanced with a radio selector
- User chooses which version to save; their choice sets `is_enhanced` on the feature record
- If the user accepts Enhanced: `is_enhanced = true` → unlocks fan-out generation on that feature
- If the user accepts Original or skips: `is_enhanced = false`

### Fan-Out Story Generation (Feature View)
Only available when `feature.is_enhanced = true`.

**Idle phase:**
1. When the user opens an enhanced feature, the system automatically calls the LLM to infer context (business objective, intended user, business rules, notes) from the feature name and description
2. Inferred context pre-populates a form — the user can edit any field before generating
3. Business Rules and Additional Notes use Preview/Edit tabs with markdown rendering (supports numbered lists and bullets returned by the LLM)
4. Business Objective and Intended User are required fields
5. User clicks "🚀 Generate All Stories" → LLM decomposes the feature into 3–7 atomic user stories (8192 token budget)
6. All generated stories are parsed and validated against the `StoryPackage` schema

**Preview phase:**
- Each story shown in a bordered container with a checkbox (all checked by default)
- Checked stories display: title, acceptance criteria, confidence, escalation warning if applicable
- Unchecked stories show as struck-through
- "Save Selected" saves only checked stories with `source = "A"` (AI-Generated)
- "Discard All" clears the preview with no saves
- All fanout session state is cleared after save or discard

### Single Story Generation (Feature View)
- Available on all features regardless of `is_enhanced`
- Inline form below the fan-out section (or at the bottom if no fan-out section)
- Fields: feature title, description, business objective, intended user, business rules (optional), notes (optional)
- Generates one story using the same context-engineered prompt as the capstone
- Saved with `source = "A"` (AI-Generated)

### Story Display
- All stories listed as expandable cards with source badge:
  - ⭐ AI-Generated (`source = "A"`)
  - ✍️ Manual (`source = "M"`)
  - ✏️ Edited (`source = "E"`) — reserved, not yet in use
- Each expanded story shows: user story, acceptance criteria, DoR status (green/red), criteria met/missing, missing information, assumptions, confidence, escalation flag
- Delete story available inline

---

## What Is Not Yet Built

| Feature | Notes |
|---|---|
| Story edit workflow | `source = "E"` is reserved in schema but edit modal not built |
| Story generation modal | Single story generation is still inline, not a modal — next planned UI refactor |
| Story export | No export to Jira, CSV, or other formats |
| Multi-user collaboration | RLS is per-user; no sharing or team access |
| Project archiving | No soft delete — delete is permanent |

---

## Architecture

### Stack
- **Frontend:** Streamlit (single-page, session_state routing)
- **Auth + Database:** Supabase (free tier) — email/password auth, PostgreSQL with RLS
- **LLM:** Anthropic Claude API (`claude-sonnet-4-6`, temperature 0.3)
- **Validation:** Pydantic `StoryPackage` model in `app/parser.py`

### Navigation Model
Single-page app with `st.session_state["view"]` routing:

```
login → dashboard → project → feature
```

Relevant session state keys:

| Key | Type | Purpose |
|---|---|---|
| `session` | Supabase Session | Auth token; used by `restore_session()` on every rerun |
| `user` | Supabase User | Current authenticated user |
| `view` | str | Current view: login / dashboard / project / feature |
| `project_id` | str | UUID of open project |
| `project_name` | str | Display name of open project |
| `feature_id` | str | UUID of open feature |
| `feature_name` | str | Display name of open feature |
| `fanout_ctx_{feature_id}` | dict | Cached LLM-inferred fanout context for this feature |
| `fanout_stories` | list | Generated story packages pending save |
| `fanout_count` | int | Number of generated stories in preview |
| `fanout_sel_{i}` | bool | Checkbox state for story i in preview |
| `fanout_biz_obj` | str | Business objective form field |
| `fanout_intended_user` | str | Intended user form field |
| `fanout_biz_rules` | str | Business rules form field |
| `fanout_notes` | str | Notes form field |

### UI Pattern
All create/edit actions use `st.dialog` modals. Key rule: **never call `st.rerun()` inside a modal helper** — button clicks already trigger reruns, and `st.rerun()` inside `st.dialog` closes the modal.

---

## Database Schema (Supabase)

```sql
-- Projects
projects: id (uuid), name (text), owner (text), status (text),
          created_by (uuid), created_at (timestamptz)
RLS: users see only rows where created_by = auth.uid()

-- Features
features: id (uuid), project_id (uuid), name (text), description (text),
          is_enhanced (boolean, default false),
          created_by (uuid), created_at (timestamptz)
RLS: users see only features on their own projects

-- User Stories
user_stories: id (uuid), feature_id (uuid), title (text), user_story (text),
              acceptance_criteria (jsonb), definition_of_ready (jsonb),
              missing_information (jsonb), assumptions (jsonb),
              confidence (text), escalation_flag (boolean),
              source (text, default 'M'),
              created_by (uuid), created_at (timestamptz)
RLS: users see only stories on their own features
```

---

## File Map

| File | Purpose |
|---|---|
| `enhanced_app.py` | Entry point — loads env, calls `restore_session()`, routes views |
| `app/login_view.py` | Sign in / sign up with tabbed layout |
| `app/dashboard_view.py` | Project list, Add/Edit modals, feature and story counts per card |
| `app/project_view.py` | Feature list, Add/Edit/Bulk Delete modals, enhance workflow |
| `app/feature_view.py` | Story list, fan-out section, single story generation form |
| `app/db.py` | All Supabase queries — auth, projects, features, stories |
| `app/prompts.py` | `build_improved_prompt()`, `build_fanout_prompt()` |
| `app/llm_client.py` | `call_improved()`, `call_fanout()`, `enhance_feature_description()`, `suggest_fanout_context()` |
| `app/parser.py` | `StoryPackage` Pydantic model, `parse_output()`, `parse_fanout_output()` |

---

## LLM Calls in the Enhanced App

| Function | Model | Temp | Max Tokens | Purpose |
|---|---|---|---|---|
| `enhance_feature_description()` | claude-sonnet-4-6 | 0.4 | 512 | Refine feature description |
| `suggest_fanout_context()` | claude-sonnet-4-6 | 0.3 | 512 | Infer fanout context from feature |
| `call_improved()` | claude-sonnet-4-6 | 0.3 | 4096 | Single story generation |
| `call_fanout()` | claude-sonnet-4-6 | 0.3 | 8192 | Fan-out: 3–7 stories from one feature |

---

## Environment Setup

Requires a `.env` file (not committed) with:

```
ANTHROPIC_API_KEY=...
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
```

Run with:
```bash
python3 -m streamlit run enhanced_app.py
```

---

## Critical Bug Fixes on Record

| Bug | Root Cause | Fix |
|---|---|---|
| Auth lost on navigation | Supabase singleton client loses auth token on every Streamlit rerun | Call `restore_session(access_token, refresh_token)` at top of `main()` on every rerun |
| Enhance button closes modal | `st.rerun()` inside `st.dialog` dismisses the modal | Remove all `st.rerun()` calls from enhance helper; button clicks already trigger reruns |
| Enhance result not visible in modal | Session state read before button handler sets it in same rerun | Read `enhanced = st.session_state.get(enhanced_key)` **after** button handler executes, not before |

---

## Suggested Next Steps

1. **Story edit workflow** — Add Edit Story modal; set `source = "E"` on save; re-run LLM to update or allow manual edit
2. **Feature View modal refactor** — Move single story generation into a modal triggered from a header-row button (consistent with Dashboard and Project view patterns)
3. **Story export** — Add CSV or JSON export from the feature view for sprint board import
