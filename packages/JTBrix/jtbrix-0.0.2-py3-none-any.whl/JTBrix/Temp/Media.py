import sys
import os
import threading
import time
import socket
from flask import Flask, request, render_template_string
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt, QTimer
from waitress import serve

# Configure Qt application attributes before creating QApplication
QApplication.setAttribute(Qt.AA_DisableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, True)

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def Play_video(app, video_path, done_flag):
    video_filename = os.path.basename(video_path)

    @app.route('/video')
    def serve_video():
        return f"""
        <html>
        <head>
            <title>Video</title>
            <style>
                body, html {{
                    margin: 0;
                    padding: 0;
                    height: 100%;
                    background-color: black;
                }}
                video {{
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                }}
            </style>
        </head>
        <body>
            <video id="videoPlayer" autoplay muted playsinline onended="window.location.href='/question/1'">
                <source src="/static/{video_filename}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <script>
                document.addEventListener('DOMContentLoaded', function () {{
                    var video = document.getElementById('videoPlayer');
                    video.play().catch(error => console.log('Auto-play failed:', error));
                }});
            </script>
        </body>
        </html>
        """

def questioner(app, question, option1, option2, color1, color2, image_path, result, index):
    image_filename = os.path.basename(image_path)
    image_url = f"/static/{image_filename}"

    html_template = f"""
    <!doctype html>
    <html lang="en">
    <head>
        <title>Question {index}</title>
        <style>
            body {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                height: 100vh;
                margin: 0;
            }}
            h2 {{
                margin-bottom: 30px;
                text-align: center;
            }}
            .option {{
                width: 300px;
                height: 60px;
                margin: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                cursor: pointer;
                border-radius: 10px;
                color: white;
            }}
            img {{
                margin-top: 30px;
                max-width: 80%;
                max-height: 300px;
                object-fit: contain;
            }}
        </style>
    </head>
    <body>
        <h2>{question}</h2>
        <div class="option" style="background-color: {color1};" onclick="submitAnswer('{option1}')">{option1}</div>
        <div class="option" style="background-color: {color2};" onclick="submitAnswer('{option2}')">{option2}</div>
        <img src="{image_url}" alt="Image">
        
        <script>
            const startTime = Date.now();
            function submitAnswer(answer) {{
                const elapsed = (Date.now() - startTime) / 1000;
                fetch('/submit/{index}', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{answer: answer, time: elapsed}})
                }}).then(() => {{
                    {f'window.location.href="/question/{int(index) + 1}";' if int(index) < result["expected"] else 'document.body.innerHTML = "<h2>Thank you!</h2>";'}
                }});
            }}
        </script>
    </body>
    </html>
    """

    def question_page():
        return render_template_string(html_template)
    
    app.add_url_rule(
        f'/question/{index}',
        endpoint=f'question_page_{index}',
        view_func=question_page
    )

    def submit_answer():
        data = request.get_json()
        result['answers'].append(data['answer'])
        result['times'].append(data['time'])

        if int(index) < result['expected']:
            return f"<script>window.location.href='/question/{int(index) + 1}'</script>"
        else:
            return "<h2>Thank you!</h2>"

    app.add_url_rule(
        f'/submit/{index}',
        endpoint=f'submit_answer_{index}',
        view_func=submit_answer,
        methods=['POST']
    )

class MediaBox(QMainWindow):
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.initUI()
        
    def initUI(self):
        # Configure WebEngine profile to disable storage
        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        profile.setCachePath("")
        profile.setPersistentStoragePath("")

        # Configure web settings
        self.web = QWebEngineView()
        settings = self.web.settings()
        settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        
        self.setCentralWidget(self.web)
        self.showFullScreen()
        
        # Add slight delay to ensure server is ready
        QTimer.singleShot(500, self.load_initial_url)

    def load_initial_url(self):
        self.web.load(QUrl(f"http://127.0.0.1:{self.port}/video"))

def run(port, *question_data_list):
    app = Flask(__name__)
    result = {'answers': [], 'times': [], 'expected': len(question_data_list)}
    done_flag = {'done': False}

    # Add static file route explicitly
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return app.send_static_file(filename)

    Play_video(app, video_path="static/FB.mp4", done_flag=done_flag)

    for i, question_data in enumerate(question_data_list, start=1):
        question, option1, option2, color1, color2, image_path = question_data
        questioner(app, question, option1, option2, color1, color2, image_path, result, index=str(i))

    # Start production server in background thread
    flask_thread = threading.Thread(target=serve, kwargs={'app': app, 'port': port})
    flask_thread.daemon = True
    flask_thread.start()

    # Create Qt application
    qt_app = QApplication(sys.argv)
    window = MediaBox(port)
    
    # Main execution loop
    timer = time.time()
    while len(result['answers']) < result['expected']:
        qt_app.processEvents()
        if time.time() - timer > 300:  # 5-minute timeout
            break
        time.sleep(0.1)

    window.close()
    return result['answers'], result['times']

if __name__ == "__main__":
    free_port = find_free_port()
    Q1 = ("Which fruit do you prefer?", "Apple", "Banana", "red", "goldenrod", "static/p.jpeg")
    Q2 = ("Which car do you prefer?", "Tesla", "Ford", "blue", "gray", "static/p.jpeg")
    answers, times = run(free_port, Q1, Q2)
    print("Answers:", answers)
    print("Times:", times)