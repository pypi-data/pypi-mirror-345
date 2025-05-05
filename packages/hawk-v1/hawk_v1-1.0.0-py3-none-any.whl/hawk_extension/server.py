"""
H.A.W.K - High-Accuracy Wordsmithing Kernel
Server module for extension installation
"""

import os
import sys
import webbrowser
import threading
import time
import socket
import tempfile
import platform
from pathlib import Path

try:
    from flask import Flask, render_template, send_from_directory, jsonify
    from waitress import serve
except ImportError:
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "waitress", "packaging"])
    from flask import Flask, render_template, send_from_directory, jsonify
    from waitress import serve

# Constants
PORT = 5000
HOST = "localhost"
SERVER_URL = f"http://{HOST}:{PORT}"

app = Flask(__name__, 
           template_folder=os.path.join(os.path.dirname(__file__), "templates"),
           static_folder=os.path.join(os.path.dirname(__file__), "static"))

def find_free_port():
    """Find a free port to use for the server"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 0))
        return s.getsockname()[1]

def create_template_dir():
    """Create templates directory and the installation page"""
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    os.makedirs(template_dir, exist_ok=True)
    
    # Create index.html template
    index_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>H.A.W.K Extension Installer</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                border-radius: 8px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
                font-size: 2.2em;
            }
            h2 {
                color: #3498db;
                font-size: 1.6em;
                margin-top: 30px;
            }
            .btn {
                display: inline-block;
                background-color: #3498db;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
                margin: 15px 0;
                border: none;
                cursor: pointer;
                font-size: 1em;
                transition: background-color 0.3s;
            }
            .btn:hover {
                background-color: #2980b9;
            }
            .btn-secondary {
                background-color: #95a5a6;
            }
            .btn-secondary:hover {
                background-color: #7f8c8d;
            }
            .installation-steps {
                margin: 30px 0;
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #3498db;
            }
            .step {
                margin-bottom: 20px;
            }
            .step-num {
                display: inline-block;
                background-color: #3498db;
                color: white;
                width: 25px;
                height: 25px;
                text-align: center;
                border-radius: 50%;
                margin-right: 10px;
            }
            code {
                background-color: #f8f9fa;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
                font-size: 0.9em;
            }
            footer {
                text-align: center;
                margin-top: 50px;
                color: #7f8c8d;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>H.A.W.K Extension Installer</h1>
            
            <div id="step1">
                <h2>Step 1: Manual Extension Setup</h2>
                <p>The H.A.W.K extension needs to be manually installed in Chrome:</p>
            </div>
            
            <div class="installation-steps">
                <h2>Installation Steps</h2>
                <div class="step">
                    <span class="step-num">1</span>
                    <span>Open Chrome and go to <code>chrome://extensions</code></span>
                </div>
                <div class="step">
                    <span class="step-num">2</span>
                    <span>Enable "Developer mode" using the toggle in the top-right corner</span>
                </div>
                <div class="step">
                    <span class="step-num">3</span>
                    <span>Create a folder called "hawk-extension" on your desktop</span>
                </div>
                <div class="step">
                    <span class="step-num">4</span>
                    <span>Download the extension files from our GitHub repository</span>
                </div>
                <div class="step">
                    <span class="step-num">5</span>
                    <span>Click "Load unpacked" in Chrome and select the folder</span>
                </div>
                <div class="step">
                    <span class="step-num">6</span>
                    <span>The H.A.W.K extension is now installed and ready to use!</span>
                </div>
            </div>
            
            <div id="help-section">
                <h2>Need Help?</h2>
                <p>Visit our repository for more detailed instructions and support.</p>
                <a href="https://github.com/hawk-team/hawk-extension" target="_blank" class="btn">GitHub Repository</a>
                <button class="btn btn-secondary" onclick="window.close()">Close Installer</button>
            </div>
            
            <footer>
                <p>H.A.W.K - High-Accuracy Wordsmithing Kernel v1.0</p>
                <p>© 2024 HAWK Team. All rights reserved.</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    with open(os.path.join(template_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_template)

def create_static_dir():
    """Create static directory"""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)

# Create the necessary directories and files
create_template_dir()
create_static_dir()

# Define routes for the Flask app
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

def start_server():
    """Start the Flask server using waitress"""
    print(f"Starting H.A.W.K installer server at {SERVER_URL}")
    serve(app, host=HOST, port=PORT)

def open_browser():
    """Open web browser after a short delay"""
    time.sleep(1.5)  # Give the server time to start
    webbrowser.open(SERVER_URL)
    print(f"If your browser doesn't open automatically, please visit: {SERVER_URL}")

def main():
    """Main entry point for the installer"""
    global PORT, SERVER_URL
    
    print("\n" + "="*80)
    print("H.A.W.K - High-Accuracy Wordsmithing Kernel - Installer")
    print("="*80 + "\n")
    
    # Try to use the default port or find a free one
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
    except socket.error:
        # Find a free port
        print(f"Port {PORT} is already in use. Finding a free port...")
        PORT = find_free_port()
        SERVER_URL = f"http://{HOST}:{PORT}"
    
    # Start the browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start the server
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nH.A.W.K installer server stopped.")
    
if __name__ == "__main__":
    main() 