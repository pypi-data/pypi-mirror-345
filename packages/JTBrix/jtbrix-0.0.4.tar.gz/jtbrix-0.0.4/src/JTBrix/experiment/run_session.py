from JTBrix.ui.main import ui, submitted_results
from flask import Flask
import os
import webbrowser
from pathlib import Path
import JTBrix
from JTBrix.questionnaire.screens import screens
from JTBrix.utils import find_free_port
from JTBrix import screen_config

jtbrix_root = Path(JTBrix.__file__).parent
template_path = jtbrix_root / "templates"  # Now points to JTBrix/templates

def run_entire_test_config(config: dict, static_folder: str):
    screen_config.flow_config = config

    # Setup Flask app
    app = Flask(__name__, static_folder=os.path.abspath(static_folder), template_folder = template_path)
    app.register_blueprint(ui)
    app.register_blueprint(screens)

    port = find_free_port()
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        webbrowser.open(f"http://127.0.0.1:{port}/experiment")

    app.run(port=port, debug=True)

    return submitted_results