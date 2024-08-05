from flask import Flask, request, jsonify, render_template
import os
import json
from chatbot import Chatbot
from video_upload import upload_video
from frt_processing import process_frt, live_frt, needs_frt

app = Flask(__name__)

# Directory to store uploaded videos
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load questions and criteria from JSON file
with open('questions.json', 'r') as file:
    data = json.load(file)

questions = {
    'personal_details': data['personal_details'],
    'symptoms': data['symptoms'],
    'history': data['history']
}

# Initialize chatbot instance
chatbot = Chatbot(questions)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    response = chatbot.handle_message(user_input)
    return jsonify(response)

@app.route('/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    if video_file:
        filename, error = upload_video(video_file)
        if error:
            return jsonify({'error': error}), 400
        
        video_path = os.path.join(UPLOAD_DIR, filename)
        result = process_frt(video_path)
        return jsonify({'filename': filename, 'result': result}), 200

    return jsonify({'error': 'File upload failed'}), 500

@app.route('/live_frt', methods=['GET'])
def live_frt_route():
    result = live_frt()
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)