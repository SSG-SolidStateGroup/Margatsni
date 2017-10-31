import os
from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.secret_key = os.urandom(32)
Bootstrap(app)

import Margatsni.views