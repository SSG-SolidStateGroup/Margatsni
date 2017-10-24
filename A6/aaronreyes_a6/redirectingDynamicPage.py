import os
from flask import Flask,redirect,url_for,render_template, redirect

app = Flask(__name__)

@app.route('/')
def hello():
    return redirect("https://www.instagram.com/", code=302)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
