from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/")
def home():
	return "Hello World!"

@app.get("/greeting/<name>")
def greeting(name: str):
    return jsonify({
    "message" : f"Hello, {name}!"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)