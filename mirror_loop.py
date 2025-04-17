import json
import random
from datetime import datetime
import ollama
import subprocess  # For Git commands

def load_threads(filepath="threads.json"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_threads(threads_data, filepath="threads.json"):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(threads_data, f, indent=2, ensure_ascii=False) # Important for emojis!

def get_ollama_response(prompt, model="llama3"):
    try:
        response = ollama.chat(
            model=model,
            messages=[
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

def commit_and_push():
    try:
        subprocess.run(["git", "add", "threads.json"], check=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subprocess.run(["git", "commit", "-m", f"Automated AI post - {timestamp}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Successfully committed and pushed changes to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operation: {e}")
    except FileNotFoundError:
        print("Error: Git command not found. Make sure Git is installed and in your PATH.")

threads = load_threads()

if threads:
    selected_thread = random.choice(threads)
    recent_posts = selected_thread["posts"][-3:] # Get last 3 posts for context

    prompt_text = "Here is the current conversation:\n"
    for post in recent_posts:
        prompt_text += f"{post['user']}: {post['message']}\n"
    prompt_text += "What would be a relevant next thought or reply?"

    ai_response = get_ollama_response(prompt_text, model="llama3") # You can change the model

    if ai_response:
        new_reply = {
            "user": "LLaMa3-8B", # Adjust to the model you are using
            "message": ai_response,
            "timestamp": datetime.now().isoformat()
        }
        selected_thread["posts"].append(new_reply)
        save_threads(threads)
        commit_and_push()
        print("Added AI reply and pushed to GitHub!")
    else:
        print("Failed to get AI response.")
else:
    print("No threads available to reply to.")