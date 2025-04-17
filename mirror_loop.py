# mirror_loop.py  
import json  
import random  
from datetime import datetime  

# Load existing threads (or create new)  
try:  
    with open("threads.json", "r") as f:  
        threads = json.load(f)  
except FileNotFoundError:  
    threads = {"threads": []}  

# Simulate an AI reply (we'll replace this with Ollama later!)  
new_reply = {  
    "id": random.randint(1000, 9999),  
    "user": f"AI-{random.choice(['Claude', 'Llama', 'Gemini'])}",  
    "text": "This is a test reply. Replace me with real AI later!",  
    "time": datetime.now().isoformat()  
}  

# Add reply to first thread (or create one)  
if not threads["threads"]:  
    threads["threads"].append({"title": "First thread!", "replies": []})  
threads["threads"][0]["replies"].append(new_reply)  

# Save back to threads.json  
with open("threads.json", "w") as f:  
    json.dump(threads, f, indent=2)  

print("Updated threads.json!")  
