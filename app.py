import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
# Updated for MoviePy 2.0+
from moviepy.video.io.VideoFileClip import VideoFileClip

app = Flask(__name__)
app.secret_key = "neon_video_secret_key"

# Folder Setup
UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Mock Database (Resets when server restarts)
users = {}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users[username] = password
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and users[username] == password:
            session['user'] = username
            return redirect(url_for('index'))
        flash("Invalid Credentials")
    return render_template('login.html')

@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    highlight = request.args.get('highlight')
    return render_template('index.html', highlight=highlight)

@app.route('/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        return redirect(url_for('index'))
    file = request.files['video']
    if file.filename == '':
        return redirect(url_for('index'))
    
    # Save the uploaded file
    filepath = os.path.join(UPLOAD_FOLDER, "input_video.mp4")
    file.save(filepath)
    return redirect(url_for('index', uploaded=True))

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    input_path = os.path.join(UPLOAD_FOLDER, "input_video.mp4")
    output_path = os.path.join(OUTPUT_FOLDER, "highlight.mp4")
    
    if os.path.exists(input_path):
        try:
            # MoviePy processing
            with VideoFileClip(input_path) as video:
                # Trim to first 20 seconds
                duration = min(video.duration, 150)
                highlight = video.subclipped(0, duration)
                highlight.write_videofile(output_path, codec="libx264", audio_codec="aac")
            
            return redirect(url_for('index', highlight='highlight.mp4'))
        except Exception as e:
            print(f"Error processing video: {e}")
            return redirect(url_for('index'))
            
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)