from flask import Flask
app = Flask(__name__)

@app.route("/")
def webApp():
    return "SSG HTTP API Controller Example!"

if __name__ == "__main__":
    app.run(debug = True)