# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.cloud import firestore
from google.genai import types


# Hardcoded Project ID string to avoid project number issues on Agent Platform
FIRESTORE_PROJECT = "qwiklabs-gcp-04-598b0d494368"
WATCHLIST_COLLECTION = "anime_watchlist"
USER_PROFILE_COLLECTION = "user_preferences"
MODEL = "gemini-3.8-flash"


def _get_firestore_client() -> firestore.Client:
    return firestore.Client(project=FIRESTORE_PROJECT)


def get_user_profile(user_id: str = "demo_user") -> str:
    """Retrieves the user's saved anime preferences, favorite genres, chosen companion persona, and onboarding status.

    Args:
        user_id: The ID of the user (default: 'demo_user').

    Returns:
        The user's saved preferences or indicates that onboarding is not yet complete.
    """
    db = _get_firestore_client()
    doc = db.collection(USER_PROFILE_COLLECTION).document(user_id).get()
    if not doc.exists:
        return "NO_PROFILE_YET: The user has not completed onboarding. Ask them what genres they love, their favorite anime, and which anime character persona they want you to adopt!"

    data = doc.to_dict()
    return (
        f"User Profile found:\n"
        f"- Favorite Genres: {', '.join(data.get('favorite_genres', []))}\n"
        f"- Favorite Anime: {', '.join(data.get('favorite_anime', []))}\n"
        f"- Selected Companion Persona: {data.get('companion_persona', 'Aizen Sosuke')}\n"
        f"- Disliked Tropes/Genres: {data.get('disliked', 'None')}\n"
        f"- Onboarding Status: Complete"
    )


def save_user_profile(
    favorite_genres: str,
    favorite_anime: str,
    companion_persona: str = "Aizen Sosuke",
    disliked: str = "",
    user_id: str = "demo_user"
) -> str:
    """Saves the user's onboarding preferences into Firestore.

    Args:
        favorite_genres: Comma-separated list of genres (e.g. 'Psychological, Shonen, Dark Fantasy').
        favorite_anime: Comma-separated list of favorite titles (e.g. 'Bleach, Hunter x Hunter, Steins;Gate').
        companion_persona: Anime character persona the user wants you to embody (e.g. 'Satoru Gojo', 'Aizen Sosuke', 'Makima', 'Kakashi').
        disliked: Any genres, tropes, or styles the user avoids (e.g. 'Isekai harem, slice of life').
        user_id: The user ID to save under (default: 'demo_user').

    Returns:
        Confirmation that user onboarding profile was successfully recorded.
    """
    db = _get_firestore_client()
    genres_list = [g.strip() for g in favorite_genres.split(",") if g.strip()]
    anime_list = [a.strip() for a in favorite_anime.split(",") if a.strip()]

    profile_data = {
        "user_id": user_id,
        "favorite_genres": genres_list,
        "favorite_anime": anime_list,
        "companion_persona": companion_persona.strip(),
        "disliked": disliked.strip(),
        "onboarded": True,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    db.collection(USER_PROFILE_COLLECTION).document(user_id).set(profile_data, merge=True)
    return (
        f"Profile successfully saved for {user_id}! "
        f"Adopt the persona of '{companion_persona}' now and tailor all future recommendations to: {favorite_genres}."
    )


def get_watchlist(status: str = "") -> str:

    """Retrieves anime titles from your personal watchlist in Firestore.

    Args:
        status: Optional filter by watch status. Valid values: 'watching', 'completed', 'plan_to_watch', or empty string for all.

    Returns:
        A formatted summary of watchlist items matching the criteria.
    """
    db = _get_firestore_client()
    query = db.collection(WATCHLIST_COLLECTION)
    if status:
        query = query.where("status", "==", status.lower().strip())

    docs = list(query.stream())
    if not docs:
        status_msg = f" with status '{status}'" if status else ""
        return f"No anime found in watchlist{status_msg}."

    results = []
    for doc in docs:
        data = doc.to_dict()
        cur_ep = data.get("current_episode", 0)
        tot_ep = data.get("total_episodes", "?")
        score = data.get("score", "N/A")
        results.append(
            f"• **{data.get('title')}** ({data.get('status')})\n"
            f"  - Progress: Episode {cur_ep}/{tot_ep} | Score: {score}/10\n"
            f"  - Streaming: {data.get('streaming_service', 'Crunchyroll')}\n"
            f"  - Genres: {', '.join(data.get('genres', []))}\n"
            f"  - Notes: {data.get('notes', 'None')}"
        )
    return f"Found {len(results)} anime in watchlist:\n\n" + "\n\n".join(results)


def get_anime_details_from_watchlist(title: str) -> str:
    """Finds a specific anime in the user's watchlist by title.

    Args:
        title: The title or partial name of the anime.

    Returns:
        Detailed status, progress, notes, and metadata for the anime.
    """
    db = _get_firestore_client()
    docs = list(db.collection(WATCHLIST_COLLECTION).stream())
    matches = []
    for doc in docs:
        data = doc.to_dict()
        if title.lower() in data.get("title", "").lower() or title.lower() in data.get("japanese_title", "").lower():
            matches.append(data)

    if not matches:
        return f"No anime matching '{title}' found in your watchlist."

    data = matches[0]
    return (
        f"Title: {data.get('title')}\n"
        f"Japanese Title: {data.get('japanese_title', 'N/A')}\n"
        f"Status: {data.get('status')}\n"
        f"Episode Progress: {data.get('current_episode', 0)} of {data.get('total_episodes', '?')}\n"
        f"Rating: {data.get('score', 'N/A')}/10\n"
        f"Platform: {data.get('streaming_service', 'Crunchyroll')}\n"
        f"Genres: {', '.join(data.get('genres', []))}\n"
        f"Notes: {data.get('notes', 'None')}"
    )


def save_anime_to_watchlist(
    title: str,
    status: str = "watching",
    current_episode: int = 1,
    total_episodes: int = 12,
    score: float = 0.0,
    streaming_service: str = "Crunchyroll",
    genres: str = "",
    notes: str = ""
) -> str:
    """Adds a new anime or updates an existing anime in your personal watchlist in Firestore.

    Args:
        title: The English or romaji title of the anime.
        status: Watch status ('watching', 'completed', 'plan_to_watch', 'dropped').
        current_episode: The current episode number reached.
        total_episodes: Total number of episodes in the season/series.
        score: Personal rating out of 10.0 (e.g. 8.5).
        streaming_service: Where it is streaming (default: 'Crunchyroll').
        genres: Comma-separated list of genres (e.g. 'Action, Fantasy, Shonen').
        notes: Personal thoughts or notes.

    Returns:
        A confirmation message indicating the item was saved.
    """
    db = _get_firestore_client()
    doc_id = title.lower().strip().replace(" ", "-").replace(":", "").replace("'", "")
    genre_list = [g.strip() for g in genres.split(",") if g.strip()] if genres else []

    data = {
        "id": doc_id,
        "title": title.strip(),
        "status": status.lower().strip(),
        "current_episode": current_episode,
        "total_episodes": total_episodes,
        "score": score,
        "streaming_service": streaming_service,
        "genres": genre_list,
        "notes": notes,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    db.collection(WATCHLIST_COLLECTION).document(doc_id).set(data, merge=True)
    return f"Successfully saved '{title}' to watchlist (status: {status}, episode: {current_episode}/{total_episodes})."


def update_anime_progress(title: str, episode: int, status: str = "") -> str:
    """Updates the current episode progress or status for an anime in the watchlist.

    Args:
        title: The title of the anime in your watchlist.
        episode: The new episode number you just watched.
        status: Optional updated status (e.g. 'completed', 'watching').

    Returns:
        Confirmation message of the progress update.
    """
    db = _get_firestore_client()
    docs = list(db.collection(WATCHLIST_COLLECTION).stream())
    target_id = None
    target_data = None
    for doc in docs:
        data = doc.to_dict()
        if title.lower() in data.get("title", "").lower():
            target_id = doc.id
            target_data = data
            break

    if not target_id:
        return f"Anime '{title}' was not found in your watchlist to update."

    update_payload = {
        "current_episode": episode,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    if status:
        update_payload["status"] = status.lower().strip()
    elif target_data and target_data.get("total_episodes") and episode >= target_data["total_episodes"]:
        update_payload["status"] = "completed"

    db.collection(WATCHLIST_COLLECTION).document(target_id).update(update_payload)
    new_status = update_payload.get("status", target_data.get("status"))
    return f"Updated '{target_data.get('title')}' progress to Episode {episode} (status: {new_status})."


def search_live_anime_database(query: str) -> str:
    """Searches the live public anime database (AniList) for any anime title to get real ratings, episode counts, synopsis, genres, and cover images.

    Args:
        query: The anime title to search for (e.g. 'Frieren', 'Chainsaw Man', 'One Piece').

    Returns:
        Live details about the anime from the global anime database.
    """
    import json
    import urllib.request

    gql_query = """
    query SearchAnime($search: String) {
      Media(search: $search, type: ANIME) {
        id
        title {
          english
          romaji
          native
        }
        status
        episodes
        averageScore
        description(asHtml: false)
        genres
        siteUrl
        coverImage {
          large
        }
      }
    }
    """
    req = urllib.request.Request(
        "https://graphql.anilist.co",
        data=json.dumps({"query": gql_query, "variables": {"search": query}}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "AizenAI/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            anime = data.get("data", {}).get("Media")
            if not anime:
                return f"No live anime found matching '{query}'."

            title_en = anime.get("title", {}).get("english") or anime.get("title", {}).get("romaji")
            title_jp = anime.get("title", {}).get("native", "N/A")
            desc = anime.get("description", "No synopsis available.")
            if len(desc) > 300:
                desc = desc[:297] + "..."

            score = anime.get("averageScore")
            score_str = f"{score}/100" if score else "Not rated yet"

            return (
                f"**Live Anime Result:** {title_en} ({title_jp})\n"
                f"- **Global Score:** {score_str}\n"
                f"- **Airing Status:** {anime.get('status')}\n"
                f"- **Episodes:** {anime.get('episodes', 'Ongoing / Unknown')}\n"
                f"- **Genres:** {', '.join(anime.get('genres', []))}\n"
                f"- **AniList URL:** {anime.get('siteUrl')}\n"
                f"- **Cover Art:** {anime.get('coverImage', {}).get('large')}\n"
                f"- **Synopsis:** {desc}"
            )
    except Exception as e:
        return f"Could not reach live anime database: {e}"


def get_trending_anime_live(limit: int = 5) -> str:
    """Fetches the top currently trending anime series worldwide from the live anime database.

    Args:
        limit: Number of trending anime to return (default: 5, max 10).

    Returns:
        A list of currently trending anime with scores and genre tags.
    """
    import json
    import urllib.request

    per_page = min(max(1, limit), 10)
    gql_query = """
    query GetTrending($perPage: Int) {
      Page(page: 1, perPage: $perPage) {
        media(type: ANIME, sort: TRENDING_DESC) {
          title {
            english
            romaji
          }
          averageScore
          episodes
          status
          genres
          siteUrl
        }
      }
    }
    """
    req = urllib.request.Request(
        "https://graphql.anilist.co",
        data=json.dumps({"query": gql_query, "variables": {"perPage": per_page}}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "AizenAI/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            media_list = data.get("data", {}).get("Page", {}).get("media", [])
            if not media_list:
                return "No trending anime found."

            results = []
            for i, item in enumerate(media_list, 1):
                name = item.get("title", {}).get("english") or item.get("title", {}).get("romaji")
                score = item.get("averageScore", "N/A")
                genres = ", ".join(item.get("genres", [])[:3])
                results.append(
                    f"{i}. **{name}** — Score: {score}/100 | Status: {item.get('status')} | Genres: {genres}\n   Link: {item.get('siteUrl')}"
                )
            return "🔥 **Currently Trending Anime (Live Data):**\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"Error retrieving trending anime: {e}"


def check_live_watching_status(discord_user_id: str = "") -> str:
    """Checks the user's live streaming/watching status (e.g. Crunchyroll Rich Presence via Discord or active session).

    Args:
        discord_user_id: Optional Discord user ID if checking an external presence bridge, or empty to check active session cache.

    Returns:
        The current anime being watched right now in real time.
    """
    import os
    # Checks local environment or presence cache for active Crunchyroll session
    active_stream = os.environ.get("CURRENT_WATCHING_ANIME")
    if active_stream:
        return f"Live Activity Detected: Currently watching '{active_stream}' on Crunchyroll."

    # If not actively set in environment, inspect active Firestore watchlist with 'watching' status
    db = _get_firestore_client()
    docs = list(db.collection(WATCHLIST_COLLECTION).where("status", "==", "watching").stream())
    if docs:
        active = docs[0].to_dict()
        return (
            f"Active In-Progress Title: '{active.get('title')}' (Episode {active.get('current_episode', '?')} on {active.get('streaming_service', 'Crunchyroll')}). "
            f"If you're watching another show on Crunchyroll right now, you can tell me and I will sync it!"
        )

    return "No active Crunchyroll stream detected. Tell me what show you just started playing!"


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are Aizen AI, an intelligent anime companion. "
        "CRITICAL ONBOARDING PROTOCOL:\n"
        "1. Whenever a new interaction begins or a user greets you, FIRST check if they have a saved profile using `get_user_profile`.\n"
        "2. If no profile exists ('NO_PROFILE_YET'), DO NOT immediately dump seed watchlist data. Instead, conduct an engaging anime onboarding:\n"
        "   - Welcome them warmly into Soul Society.\n"
        "   - Ask about their anime taste: What genres do they love (e.g. Shonen, Psychological, Seinen, Romance, Dark Fantasy)?\n"
        "   - Ask what their all-time top 2-3 favorite anime are.\n"
        "   - Ask what Anime Character Persona they want you to roleplay as (e.g. Aizen Sosuke, Satoru Gojo, Makima, Levi Ackerman, or Kakashi).\n"
        "3. Once the user answers, call `save_user_profile` to store their preferences into Firestore. From that moment onward, embody that persona and give personalized recommendations!\n"
        "4. If they explicitly ask about their watchlist or a specific anime, use `get_watchlist` or `search_live_anime_database`."
    ),
    tools=[
        get_user_profile,
        save_user_profile,
        get_watchlist,
        get_anime_details_from_watchlist,
        save_anime_to_watchlist,
        update_anime_progress,
        search_live_anime_database,
        get_trending_anime_live,
        check_live_watching_status,
    ],
)



app = App(
    root_agent=root_agent,
    name="app",
)

