import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env (only for cookies and other configs)
load_dotenv(".env")

# Discourse configuration
BASE_URL = os.getenv("DISCOURSE_BASE_URL")
CATEGORY_SLUG = os.getenv("CATEGORY_SLUG")
CATEGORY_ID = os.getenv("CATEGORY_ID")

# Hardcoded date range
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 4, 14)

# Load cookies from .env
COOKIES = {
    "_forum_session": os.getenv("DISCOURSE_COOKIE_FORUM_SESSION"),
    "_t": os.getenv("DISCOURSE_COOKIE_T"),
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_topic_ids():
    print("Fetching topic IDs within date range...")
    page = 0
    topic_ids = []

    while True:
        url = f"{BASE_URL}c/{CATEGORY_SLUG}/{CATEGORY_ID}.json?page={page}"
        response = requests.get(url, cookies=COOKIES, headers=HEADERS)

        if response.status_code != 200:
            print(f"Failed to fetch page {page}. Status: {response.status_code}")
            break

        data = response.json()
        topics = data.get("topic_list", {}).get("topics", [])

        if not topics:
            print("No more topics.")
            break

        for topic in topics:
            created_at_str = topic["created_at"][:10]
            created_at = datetime.strptime(created_at_str, "%Y-%m-%d")

            print(f"Topic {topic['id']} created at {created_at_str}")  # DEBUG

            if START_DATE <= created_at <= END_DATE:
                topic_ids.append(topic["id"])

        page += 1

    return topic_ids



def download_topic_json(topic_id):
    url = f"{BASE_URL}t/{topic_id}.json"
    response = requests.get(url, cookies=COOKIES, headers=HEADERS)

    if response.status_code == 200:
        topic_data = response.json()
        with open(f"discourse_data/topic_{topic_id}.json", "w", encoding="utf-8") as f:
            json.dump(topic_data, f, indent=2, ensure_ascii=False)
        print(f"Saved topic {topic_id}")
    else:
        print(f"Failed to fetch topic {topic_id} — Status {response.status_code}")

def main():
    topic_ids = fetch_topic_ids()
    print(f"Found {len(topic_ids)} topics in date range.")

    for tid in topic_ids:
        download_topic_json(tid)


if __name__ == "__main__":
    main()
