import os
from supabase import create_client, Client

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        _client = create_client(url, key)
    return _client


# --- Auth ---

def sign_up(email: str, password: str):
    return get_client().auth.sign_up({"email": email, "password": password})


def sign_in(email: str, password: str):
    return get_client().auth.sign_in_with_password({"email": email, "password": password})


def restore_session(access_token: str, refresh_token: str):
    """Re-apply the user's auth token to the Supabase client on each Streamlit rerun."""
    try:
        get_client().auth.set_session(access_token, refresh_token)
    except Exception:
        pass


def sign_out():
    get_client().auth.sign_out()


def get_session():
    return get_client().auth.get_session()


# --- Projects ---

def list_projects(user_id: str) -> list:
    response = (
        get_client()
        .table("projects")
        .select("*")
        .eq("created_by", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def create_project(name: str, owner: str, status: str, user_id: str) -> dict:
    response = (
        get_client()
        .table("projects")
        .insert({"name": name, "owner": owner, "status": status, "created_by": user_id})
        .execute()
    )
    return response.data[0] if response.data else {}


def update_project(project_id: str, updates: dict) -> dict:
    response = (
        get_client()
        .table("projects")
        .update(updates)
        .eq("id", project_id)
        .execute()
    )
    return response.data[0] if response.data else {}


def delete_project(project_id: str):
    get_client().table("projects").delete().eq("id", project_id).execute()


def get_feature_counts() -> dict:
    """Returns {project_id: feature_count} for all accessible projects."""
    response = get_client().table("features").select("project_id").execute()
    counts: dict = {}
    for row in (response.data or []):
        pid = row["project_id"]
        counts[pid] = counts.get(pid, 0) + 1
    return counts


def get_story_counts_by_project() -> dict:
    """Returns {project_id: story_count} by joining through features."""
    feat_response = get_client().table("features").select("id, project_id").execute()
    feat_to_proj = {r["id"]: r["project_id"] for r in (feat_response.data or [])}

    story_response = get_client().table("user_stories").select("feature_id").execute()
    counts: dict = {}
    for row in (story_response.data or []):
        pid = feat_to_proj.get(row["feature_id"])
        if pid:
            counts[pid] = counts.get(pid, 0) + 1
    return counts


# --- Features ---

def list_features(project_id: str) -> list:
    response = (
        get_client()
        .table("features")
        .select("*")
        .eq("project_id", project_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def get_feature(feature_id: str) -> dict:
    response = (
        get_client()
        .table("features")
        .select("*")
        .eq("id", feature_id)
        .single()
        .execute()
    )
    return response.data or {}


def create_feature(project_id: str, name: str, description: str, user_id: str, is_enhanced: bool = False) -> dict:
    response = (
        get_client()
        .table("features")
        .insert({
            "project_id": project_id,
            "name": name,
            "description": description,
            "created_by": user_id,
            "is_enhanced": is_enhanced,
        })
        .execute()
    )
    return response.data[0] if response.data else {}


def update_feature(feature_id: str, updates: dict) -> dict:
    response = (
        get_client()
        .table("features")
        .update(updates)
        .eq("id", feature_id)
        .execute()
    )
    return response.data[0] if response.data else {}


def delete_feature(feature_id: str):
    get_client().table("features").delete().eq("id", feature_id).execute()


def bulk_delete_features(feature_ids: list[str]):
    get_client().table("features").delete().in_("id", feature_ids).execute()


# --- User Stories ---

def list_stories(feature_id: str) -> list:
    response = (
        get_client()
        .table("user_stories")
        .select("*")
        .eq("feature_id", feature_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def save_story(feature_id: str, story_package: dict, user_id: str, source: str = "M") -> dict:
    payload = {
        "feature_id": feature_id,
        "title": story_package.get("title", ""),
        "user_story": story_package.get("user_story", ""),
        "acceptance_criteria": story_package.get("acceptance_criteria", []),
        "definition_of_ready": story_package.get("definition_of_ready"),
        "missing_information": story_package.get("missing_information", []),
        "assumptions": story_package.get("assumptions", []),
        "confidence": story_package.get("confidence"),
        "escalation_flag": story_package.get("escalation_flag", False),
        "source": source,
        "created_by": user_id,
    }
    response = get_client().table("user_stories").insert(payload).execute()
    return response.data[0] if response.data else {}


def delete_story(story_id: str):
    get_client().table("user_stories").delete().eq("id", story_id).execute()
