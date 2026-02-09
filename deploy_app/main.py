from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Satyam Gangwar from Cloud Run."

@app.route("/analyze")
def analyze():
    return "Hello new route"

if __name__ == "__main__":
    print("Starting server...")
    app.run(host="0.0.0.0", port=8080)

