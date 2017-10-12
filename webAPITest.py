#Author: Ismail A.
from flask import Flask
app = Flask(__name__)

@app.route("/")
def webAPITest():
    return "This is a working example of the ssg HTTP API code"

if __name__ == "__main__":
    app.run(debug = True)
