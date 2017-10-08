from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_tasks():
    return "team-SSG HTTP GET method"

if __name__ == "__main__":
	app.run(debug=True)