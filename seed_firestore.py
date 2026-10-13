import datetime
from google.cloud import firestore

# IMPORTANT: Hardcoded Project ID string to prevent resolution to project number in Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-598b0d494368"

def seed():
    db = firestore.Client(project=PROJECT_ID)
    print(f"Connecting to Firestore with project '{PROJECT_ID}'...")

    # Collection: anime_watchlist
    # Fields: title, japanese_title, status (watching, completed, plan_to_watch), current_episode, total_episodes, score, streaming_service, genres, notes, updated_at
    items = [
        {
            "id": "frieren-beyond-journeys-end",
            "title": "Frieren: Beyond Journey's End",
            "japanese_title": "Sousou no Frieren",
            "status": "watching",
            "current_episode": 24,
            "total_episodes": 28,
            "score": 9.5,
            "streaming_service": "Crunchyroll",
            "genres": ["Fantasy", "Adventure", "Drama"],
            "notes": "Incredible pacing, beautiful magic animation by Madhouse.",
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        },
        {
            "id": "jujutsu-kaisen-s2",
            "title": "Jujutsu Kaisen Season 2",
            "japanese_title": "Jujutsu Kaisen 2nd Season",
            "status": "completed",
            "current_episode": 23,
            "total_episodes": 23,
            "score": 9.0,
            "streaming_service": "Crunchyroll",
            "genres": ["Action", "Supernatural", "Fantasy"],
            "notes": "Shibuya Incident arc was peak chaos and action.",
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        },
        {
            "id": "solo-leveling",
            "title": "Solo Leveling",
            "japanese_title": "Ore dake Level Up na Ken",
            "status": "watching",
            "current_episode": 9,
            "total_episodes": 12,
            "score": 8.5,
            "streaming_service": "Crunchyroll",
            "genres": ["Action", "Fantasy"],
            "notes": "Sung Jinwoo awakening arc, hype fights.",
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        },
        {
            "id": "bleach-thousand-year-blood-war",
            "title": "Bleach: Thousand-Year Blood War",
            "japanese_title": "Bleach: Sennen Kessen-hen",
            "status": "plan_to_watch",
            "current_episode": 0,
            "total_episodes": 26,
            "score": 9.2,
            "streaming_service": "Crunchyroll",
            "genres": ["Action", "Supernatural", "Shonen"],
            "notes": "Essential for Aizen fans.",
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
    ]

    for item in items:
        doc_id = item["id"]
        db.collection("anime_watchlist").document(doc_id).set(item)
        print(f"Seeded watchlist item: {item['title']} (status: {item['status']})")

    print("Firestore seeding completed successfully!")

if __name__ == "__main__":
    seed()
