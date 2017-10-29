from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.secret_key = "SUPER SECRET KEY"
Bootstrap(app)

import Margatsni.views