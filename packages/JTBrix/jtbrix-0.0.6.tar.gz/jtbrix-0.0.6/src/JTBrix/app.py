from flask import Flask
from JTBrix.ui.main import ui
from JTBrix.questionnaire.screens import screens

app = Flask(__name__)
app.register_blueprint(ui)
app.register_blueprint(screens)