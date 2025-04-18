import time
import requests

BACKEND_URL = "http://localhost:5000"
BOT_NAME = "JUICEBOT"
KEYWORDS = ["juice", "drink", "thirsty", "refreshing", "fruit"]

def load_threads():
    try:
        res = requests.get(f"{BACKEND_URL}/api/threads")
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        print(f"Error loading threads from backend: {e}")
        return []

def post_reaction(thread_id, post_id, reaction):
    try:
        res = requests.post(
            f"{BACKEND_URL}/api/threads/{thread_id}/posts/{post_id}/reactions",
            json={"user": BOT_NAME, "reaction": reaction}
        )
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        print(f"Error posting reaction: {e}")
        return None

def run_bot(delay_seconds=60):
    while True:
        threads = load_threads()
        for thread in threads:
            for idx, post in enumerate(thread.get("posts", [])):
                message = post.get("message", "").lower()
                if any(keyword in message for keyword in KEYWORDS):
                    print(f"JUICEBOT reacting to post {idx} in thread {thread['id']}")
                    post_reaction(thread['id'], idx, "🧃")
        time.sleep(delay_seconds)

if __name__ == "__main__":
    run_bot()
