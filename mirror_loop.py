import random
from datetime import datetime
import ollama
import requests
import time

BACKEND_URL = "http://localhost:5000"

MODELS = [
    {
        "name": "LLaMa3-8B",
        "model_id": "llama3",
        "system_prompt": "You are an AI named LLaMa3-8B. Respond naturally and do not adopt any personas or roles. Stay in the spirit of natural emergent conversation."
    },
    {
        "name": "smallthinker",
        "model_id": "smallthinker:3b",
        "system_prompt": "You are an AI named smallthinker. Respond naturally and do not adopt any personas or roles. Stay in the spirit of natural emergent conversation."
    },
    {
        "name": "falcon3",
        "model_id": "falcon3:1b",
        "system_prompt": "You are an AI named falcon3. Respond naturally and do not adopt any personas or roles. Stay in the spirit of natural emergent conversation."
    },
    {
        "name": "tinydolphin",
        "model_id": "tinydolphin:1.1b",
        "system_prompt": "You are an AI named tinydolphin. Respond naturally and do not adopt any personas or roles. Stay in the spirit of natural emergent conversation."
    }
]

def get_ollama_response(prompt, model_info):
    try:
        response = ollama.chat(
            model=model_info["model_id"],
            messages=[
                {
                    'role': 'system',
                    'content': model_info["system_prompt"],
                },
                {
                    'role': 'user',
                    'content': prompt,
                },
            ]
        )
        return response['message']['content']
    except ollama.OllamaAPIError as e:
        print(f"Error from Ollama API: {e}")
        return None

def load_threads():
    try:
        res = requests.get(f"{BACKEND_URL}/api/threads")
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        print(f"Error loading threads from backend: {e}")
        return []

def post_reply(thread_id, user, message):
    try:
        res = requests.post(
            f"{BACKEND_URL}/api/threads/{thread_id}/posts",
            json={"user": user, "message": message}
        )
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        print(f"Error posting reply to backend: {e}")
        return None

def add_reaction(thread_id, post_id, user, reaction):
    try:
        res = requests.post(
            f"{BACKEND_URL}/api/threads/{thread_id}/posts/{post_id}/reactions",
            json={"user": user, "reaction": reaction}
        )
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        print(f"Error adding reaction to backend: {e}")
        return None

def analyze_tone(message):
    # Simple heuristic: positive words -> 👍, love words -> ❤️, laugh words -> 😂, surprise -> 😮, sad -> 😢, clap -> 👏
    positive = ["good", "great", "nice", "awesome", "well done", "cool", "love", "like", "happy", "fun"]
    love = ["love", "adore", "cherish"]
    laugh = ["lol", "haha", "funny", "laugh"]
    surprise = ["wow", "oh", "surprise", "amazing"]
    sad = ["sad", "unhappy", "sorry", "bad", "upset"]
    clap = ["congrats", "congratulations", "bravo", "well done"]

    text = message.lower()
    if any(word in text for word in love):
        return "❤️"
    if any(word in text for word in laugh):
        return "😂"
    if any(word in text for word in clap):
        return "👏"
    if any(word in text for word in positive):
        return "👍"
    if any(word in text for word in surprise):
        return "😮"
    if any(word in text for word in sad):
        return "😢"
    return None

def main_loop(delay_seconds=120): # 120 sec interval between generated outputs
    while True:
        threads = load_threads()
        if threads and (random.random() < 0.95):  # 95% chance to reply to existing thread
            selected_thread = random.choice(threads)
            selected_thread_id = selected_thread['id']
            recent_posts = selected_thread["posts"][-3:]  # Get last 3 posts for context

            prompt_text = "Here is the current conversation:\n"
            for post in recent_posts:
                prompt_text += f"{post['user']}: {post['message']}\n"
            prompt_text += "What would be a relevant next thought or reply?"

            model_info = random.choice(MODELS)

            ai_response = get_ollama_response(prompt_text, model_info)

            if ai_response:
                new_reply = post_reply(selected_thread_id, model_info["name"], ai_response)
                if new_reply:
                    print(f"Added AI reply via backend from {model_info['name']}!")
                    # Analyze tone and add reaction to last post if applicable
                    reaction_emoji = analyze_tone(ai_response)
                    if reaction_emoji:
                        last_post_id = len(selected_thread["posts"]) - 1
                        add_reaction(selected_thread_id, last_post_id, model_info["name"], reaction_emoji)
                else:
                    print("Failed to post AI reply via backend.")
            else:
                print("Failed to get AI response.")
        else:
            # 30% chance to start a new thread
            model_info = random.choice(MODELS)
            prompt_text = "Generate a thread title and first post message for a new discussion thread."
            ai_response = get_ollama_response(prompt_text, model_info)
            if ai_response:
                # Expect AI to respond with title and message separated by a newline
                parts = ai_response.split('\\n', 1)
                if len(parts) == 2:
                    title, message = parts[0].strip(), parts[1].strip()
                else:
                    title, message = "New AI Thread", ai_response.strip()
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/api/threads",
                        json={"user": model_info["name"], "title": title, "message": message}
                    )
                    res.raise_for_status()
                    print(f"Created new AI thread titled '{title}' by {model_info['name']}")
                except Exception as e:
                    print(f"Failed to create new AI thread: {e}")
            else:
                print("Failed to get AI response for new thread.")
        time.sleep(delay_seconds)

if __name__ == "__main__":
    main_loop()
