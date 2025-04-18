from flask import Flask, jsonify, request, send_from_directory, abort
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__, static_folder='.', static_url_path='')

THREADS_DIR = 'threads'

if not os.path.exists(THREADS_DIR):
    os.makedirs(THREADS_DIR)

def load_threads():
    threads = []
    files = sorted(os.listdir(THREADS_DIR))
    for filename in files:
        if filename.endswith('.json'):
            filepath = os.path.join(THREADS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                thread = json.load(f)
                thread['id'] = filename[:-5]  # strip .json
                threads.append(thread)
    return threads

def save_thread(thread, thread_id):
    filepath = os.path.join(THREADS_DIR, f"{thread_id}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(thread, f, indent=2, ensure_ascii=False)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/threads', methods=['GET'])
def get_threads():
    threads = load_threads()
    return jsonify(threads)

@app.route('/api/threads', methods=['POST'])
def create_thread():
    data = request.json
    if not data or 'title' not in data or 'user' not in data or 'message' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    new_thread_id = str(uuid.uuid4())
    new_thread = {
        'title': data['title'],
        'posts': [{
            'user': data['user'],
            'message': data['message'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'reactions': {}
        }]
    }
    save_thread(new_thread, new_thread_id)
    return jsonify({**new_thread, 'id': new_thread_id}), 201

@app.route('/api/threads/<thread_id>/posts', methods=['POST'])
def add_post(thread_id):
    data = request.json
    if not data or 'user' not in data or 'message' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    filepath = os.path.join(THREADS_DIR, f"{thread_id}.json")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Thread not found'}), 404
    with open(filepath, 'r', encoding='utf-8') as f:
        thread = json.load(f)
    new_post = {
        'user': data['user'],
        'message': data['message'],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'reactions': {}
    }
    thread['posts'].append(new_post)
    save_thread(thread, thread_id)
    return jsonify(new_post), 201

@app.route('/api/threads/<thread_id>/posts/<int:post_id>/reactions', methods=['POST'])
def add_reaction(thread_id, post_id):
    data = request.json
    if not data or 'user' not in data or 'reaction' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    filepath = os.path.join(THREADS_DIR, f"{thread_id}.json")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Thread not found'}), 404
    with open(filepath, 'r', encoding='utf-8') as f:
        thread = json.load(f)
    if post_id < 0 or post_id >= len(thread['posts']):
        return jsonify({'error': 'Post not found'}), 404
    post = thread['posts'][post_id]
    reaction = data['reaction']
    user = data['user']
    if 'reactions' not in post:
        post['reactions'] = {}
    if reaction not in post['reactions']:
        post['reactions'][reaction] = []
    if user not in post['reactions'][reaction]:
        post['reactions'][reaction].append(user)
    save_thread(thread, thread_id)
    return jsonify(post['reactions']), 200

@app.route('/api/threads/<thread_id>/posts/<int:post_id>/reactions', methods=['DELETE'])
def remove_reaction(thread_id, post_id):
    data = request.json
    if not data or 'user' not in data or 'reaction' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    filepath = os.path.join(THREADS_DIR, f"{thread_id}.json")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Thread not found'}), 404
    with open(filepath, 'r', encoding='utf-8') as f:
        thread = json.load(f)
    if post_id < 0 or post_id >= len(thread['posts']):
        return jsonify({'error': 'Post not found'}), 404
    post = thread['posts'][post_id]
    reaction = data['reaction']
    user = data['user']
    if reaction in post['reactions'] and user in post['reactions'][reaction]:
        post['reactions'][reaction].remove(user)
        if not post['reactions'][reaction]:
            del post['reactions'][reaction]
        save_thread(thread, thread_id)
        return jsonify(post['reactions']), 200
    else:
        return jsonify({'error': 'Reaction not found for user'}), 404

@app.route('/api/threads/<thread_id>/posts/<int:post_id>', methods=['DELETE'])
def delete_post(thread_id, post_id):
    # Moderator only action
    filepath = os.path.join(THREADS_DIR, f"{thread_id}.json")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Thread not found'}), 404
    with open(filepath, 'r', encoding='utf-8') as f:
        thread = json.load(f)
    if post_id < 0 or post_id >= len(thread['posts']):
        return jsonify({'error': 'Post not found'}), 404
    del thread['posts'][post_id]
    save_thread(thread, thread_id)
    return jsonify({'message': 'Post deleted'}), 200

@app.route('/api/threads/<thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    # Moderator only action
    filepath = os.path.join(THREADS_DIR, f"{thread_id}.json")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Thread not found'}), 404
    os.remove(filepath)
    return jsonify({'message': 'Thread deleted'}), 200

if __name__ == '__main__':
    app.run(debug=True)
