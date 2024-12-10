import os
import sys
from subprocess import run, CalledProcessError
from pathlib import Path
from flask import Flask, request, render_template, send_from_directory, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

def compress_video(video_file):
    output_file = Path(COMPRESSED_FOLDER) / (video_file.stem + '-compressed.mp4')
    try:
        run(['ffmpeg', '-i', str(video_file), '-vcodec', 'h264', '-acodec', 'aac', str(output_file)], check=True)
        return output_file
    except CalledProcessError as e:
        print(f"Error compressing video: {e}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file:
        video_path = Path(UPLOAD_FOLDER) / file.filename
        file.save(video_path)
        compressed_file = compress_video(video_path)
        
        if compressed_file:
            return send_from_directory(COMPRESSED_FOLDER, compressed_file.name, as_attachment=True)
        else:
            flash('Error compressing video')
            return redirect(url_for('home'))

@app.errorhandler(404)
def not_found(error):
    return "404 Error: Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    return "500 Error: Internal server error", 500

if __name__ == '__main__':
    app.run(debug=True)