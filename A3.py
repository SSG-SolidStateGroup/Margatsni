#submission by Aaron Reyes
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Welcome to Solid State Group-SSG!"

if __name__ == "__main__":
    app.run(debug=True)