# My agent: Aizen AI
One-liner: A conversational anime companion agent that adopts any anime character persona on demand, tracks what you are watching via public anime APIs, and recommends shows with rich cards and visuals.

Tool coverage:
- Memory: Remembers user taste profile (favorite genres, tropes, disliked themes), watch history, current progress, dropped shows, and the active companion persona.
- Tools:
  - `fetch_anime_details(title_or_id)`: Fetches live anime info, ratings, airing status, and streaming links from public APIs (e.g., Jikan / AniList).
  - `search_anime_catalog(query, genre, status, min_score)`: Searches live anime database for matching titles and recommendations.
  - `get_user_watchlist(username)` / `get_trending_anime()`: Retrieves trending season anime or user watchlists from public APIs.
  - `set_companion_persona(character_name, anime_series)`: Dynamically generates and configures the companion's speaking style, catchphrases, and tone based on any chosen anime character.
- Catalog/UI: Renders recommended anime titles as rich cards containing poster art, score, episode count, synopsis, and direct watch links via A2UI.
- Image gen: Generates custom anime-style art, visual match-ups, or custom scenes in the style of the chosen anime universe.
- Sandbox: Calculates watch-time marathons, binge-pacing schedules, and filler-episode percentage calculations.

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Dynamic character persona synthesis, live public anime APIs (Jikan / AniList GraphQL), code sandbox for binge schedules.
