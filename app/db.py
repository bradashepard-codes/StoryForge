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


def create_feature(project_id: str, name: str, description: str, user_id: str) -> dict:
    response = (
        get_client()
        .table("features")
        .insert({"project_id": project_id, "name": name, "description": description, "created_by": user_id})
        .execute()
    )
    return response.data[0] if response.data else {}


def delete_feature(feature_id: str):
    get_client().table("features").delete().eq("id", feature_id).execute()


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


def save_story(feature_id: str, story_package: dict, user_id: str) -> dict:
    payload = {
        "feature_id": feature_id,
        "user_story": story_package.get("user_story", ""),
        "acceptance_criteria": story_package.get("acceptance_criteria", []),
        "definition_of_ready": story_package.get("definition_of_ready"),
        "missing_information": story_package.get("missing_information", []),
        "assumptions": story_package.get("assumptions", []),
        "confidence": story_package.get("confidence"),
        "escalation_flag": story_package.get("escalation_flag", False),
        "created_by": user_id,
    }
    response = get_client().table("user_stories").insert(payload).execute()
    return response.data[0] if response.data else {}


def delete_story(story_id: str):
    get_client().table("user_stories").delete().eq("id", story_id).execute()
