
import webbrowser
import tempfile
import os
from urllib.parse import urlparse
from flask import Flask, request, render_template_string
import threading
import time
import webbrowser
import socket
from flask import request, render_template_string
 

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

  

def Play_video(app, video_path, done_flag):
    """
    Registers the /video route in the shared Flask app.
    Plays a video served from the static folder and redirects to /question on end.
    
    Args:
        app: Flask app instance.
        video_path: Path to the video inside the 'static' folder, e.g. 'static/FB.mp4'.
        done_flag: Shared dictionary to track video completion (not used in this version).
    """
    # Extract the filename (e.g., 'FB.mp4') to build a proper /static path
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
            <video id="videoPlayer" controls autoplay onended="window.location.href='/question/1'">
                <source src="/static/{video_filename}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <script>
                document.addEventListener('DOMContentLoaded', function () {{
                    var video = document.getElementById('videoPlayer');
                    video.requestFullscreen().catch(e => console.log("Fullscreen not supported:", e));
                }});
            </script>
        </body>
        </html>
        """



def questioner(app, question, option1, option2, color1, color2, image_path, result, index):
    """
    Registers /question/<index> and /submit/<index> routes with unique endpoint names.
    """
    import os
    from flask import request, render_template_string

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

    # Define question page handler
    def question_page():
        return render_template_string(html_template)
    
    app.add_url_rule(
        f'/question/{index}',
        endpoint=f'question_page_{index}',
        view_func=question_page
    )

    # Define submit handler
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


def run(port, *question_data_list):
    app = Flask(__name__)
    result = {'answers': [], 'times': [], 'expected': len(question_data_list)}
    done_flag = {'done': False}

    @app.route('/favicon.ico')
    def favicon():
        return '', 204
    
    Play_video(app, video_path="static/FB.mp4", done_flag=done_flag)

    for i, question_data in enumerate(question_data_list, start=1):
        question, option1, option2, color1, color2, image_path = question_data
        questioner(app, question, option1, option2, color1, color2, image_path, result, index=str(i))

    def start_flask():
        app.run(port=port, debug=False)

    threading.Thread(target=start_flask, daemon=True).start()
    webbrowser.open(f"http://127.0.0.1:{port}/video")

    while len(result['answers']) < result['expected']:
        time.sleep(0.1)

    return result['answers'], result['times']


if __name__ == "__main__":
    free_port = find_free_port()
    Q1 = ("Which fruit do you prefer?", "Apple", "Banana", "red", "goldenrod", "static/p.jpeg")
    Q2 = ("Which car do you prefer?", "Tesla", "Ford", "blue", "gray", "static/p.jpeg")
    answers, times = run(free_port, Q1, Q2)
    print("Answers:", answers)
    print("Times:", times)  





  