<div align="center">

# ⚔️ Aizen AI · 藍染 惣右介
### The Intelligent Anime Companion & Watchlist Engine

A full-fledged, agentic anime companion that dynamically adopts anime character personas, grounds recommendations in live public APIs, syncs streaming watch status, and manages personal watchlists backed by Google Cloud Firestore and Agent Platform.

<br/>

![Build with Gemini](https://img.shields.io/badge/Build%20with%20Gemini-World%20Tour-4285F4?logo=google&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Agent%20Platform-4285F4?logo=googlecloud&logoColor=white)
![Built with ADK](https://img.shields.io/badge/Built%20with-ADK%20%2B%20agents--cli-34A853)
![Cloud Run](https://img.shields.io/badge/Frontend-Cloud%20Run-4285F4?logo=googlecloud&logoColor=white)
![Firestore](https://img.shields.io/badge/Database-Firestore-FFCA28?logo=firebase&logoColor=black)
![Model](https://img.shields.io/badge/Model-Gemini%203.8%20Flash-9C27B0)

<sub>🌐 <a href="https://aizen-ai-frontend-423899252366.us-east1.run.app">Live Web App</a> · 📖 <a href="https://cszhu.github.io/build-with-gemini/">Lab Guide</a> · 🛠️ <a href="https://google.github.io/agents-cli/guide/getting-started/">agents-cli</a> · 🤖 <a href="https://google.github.io/adk-docs/">ADK</a></sub>

</div>

---

## 📚 Table of Contents

- [🧩 Architecture & Google Cloud Blocks](#-architecture--google-cloud-blocks)
- [✨ Key Features](#-key-features)
- [🗄️ Firestore Backend Collections](#️-firestore-backend-collections)
- [🛠️ Tool Implementation](#️-tool-implementation)
- [💻 Local Development & Testing](#-local-development--testing)
- [🚀 Deployment](#-deployment)
- [📄 License](#-license)

---

## 🧩 Architecture & Google Cloud Blocks

Aizen AI leverages the core Google Cloud and ADK primitives to deliver an interactive, agent-first companion experience:

| Layer | What it does | Powered by |
|---|---|---|
| 🤖 **The Agent** | Core reasoning, conversational persona, tool execution | [ADK](https://google.github.io/adk-docs/) + [`agents-cli`](https://google.github.io/agents-cli/guide/getting-started/), Gemini 3.8 Flash (`gemini-3.8-flash`) |
| 🗄️ **Structured Data** | Watchlists, episode progress, ratings, and onboarding preferences | [Firestore Native](https://console.cloud.google.com/firestore) (`nam5`) |
| 🌐 **Live Data Grounding** | Real-time global ratings, trending series, and synopsis queries | [AniList GraphQL API](https://graphql.anilist.co) |
| 📺 **Live Activity Tracking** | Tracks in-progress shows and Crunchyroll stream status | Custom Activity & Watch State Resolver |
| 🌐 **Frontend** | Anime-themed web UI with onboarding and quick-action chips | FastAPI proxy on [Cloud Run](https://cloud.google.com/run) |

---

## ✨ Key Features

- **🎭 Dynamic Character Persona Onboarding**: Choose to chat with *Aizen Sōsuke* (Bleach), *Satoru Gojo* (Jujutsu Kaisen), *Makima* (Chainsaw Man), *Levi Ackerman* (Attack on Titan), or *Kakashi Hatake* (Naruto).
- **📋 Persistent Watchlist Management**: Add shows to your watchlist, update episode progress, mark completed, and maintain personal notes directly in Firestore.
- **🔥 Live Global Anime Intelligence**: Grounded queries against AniList GraphQL—no stale hallucinations. Retrieves real-time scores, status, and streaming links.
- **⚡ Interactive Anime Themed UI**: Responsive void-and-reiatsu themed chat interface with quick action prompts for one-click queries.

---

## 🗄️ Firestore Backend Collections

Aizen AI connects to Firestore (`nam5`) across two collections:

1. **`anime_watchlist`**:
   - `title` *(string)*: Name of the anime.
   - `status` *(string)*: `watching`, `plan_to_watch`, `completed`, `dropped`.
   - `current_episode` / `total_episodes` *(number)*.
   - `score` *(number)*: Personal rating (out of 10).
   - `streaming_service` *(string)*: Platform (e.g. *Crunchyroll*).
   - `genres` *(list of strings)*: E.g., `["Fantasy", "Action"]`.
   - `notes` *(string)*.

2. **`user_preferences`**:
   - `favorite_genres` *(list)*.
   - `favorite_anime` *(list)*.
   - `companion_persona` *(string)*.
   - `disliked` *(string)*.
   - `onboarded` *(boolean)*.

---

## 🛠️ Tool Implementation

The agent reasoning loop in `app/agent.py` is equipped with native ADK tools:

- `get_user_profile(user_id)`: Fetches user preferences and persona configuration.
- `save_user_profile(...)`: Persists onboarding answers and updates active persona.
- `get_watchlist(status)`: Queries personal Firestore watchlist by watch status.
- `get_anime_details_from_watchlist(title)`: Fetches progress and review notes for a specific title.
- `save_anime_to_watchlist(...)`: Upserts anime titles with episodes and scores.
- `update_anime_progress(...)`: Updates current episode and completion status.
- `search_live_anime_database(query)`: Real-time search against the global AniList GraphQL API.
- `get_trending_anime_live(limit)`: Real-time top trending anime worldwide.
- `check_live_watching_status(discord_user_id)`: Resolves active Crunchyroll or in-progress watching titles.

---

## 💻 Local Development & Testing

### 1. Install Dependencies
```bash
uv sync
```

### 2. Seed Firestore (Optional)
```bash
python seed_firestore.py
```

### 3. Run Locally with agents-cli
```bash
agents-cli run "What anime is currently trending worldwide?"
```

### 4. Launch Local Web UI
```bash
python frontend/server.py
# -> Open http://localhost:8080
```

---

## 🚀 Deployment

### Agent Engine (Agent Platform)
```bash
agents-cli deploy --project qwiklabs-gcp-04-598b0d494368 --no-confirm-project
```

### Frontend (Cloud Run)
```bash
gcloud run deploy aizen-ai-frontend \
  --source frontend \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/423899252366/locations/us-east1/reasoningEngines/418602768391995392",AGENT_DIRECTORY="app"
```

Live Service URL: **[https://aizen-ai-frontend-423899252366.us-east1.run.app](https://aizen-ai-frontend-423899252366.us-east1.run.app)**

---

## 📄 License

This project is created for the **Build with Gemini** workshop. Provided for demonstration purposes.
