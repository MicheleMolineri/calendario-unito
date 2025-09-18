from flask import Flask
import os

print("Starting minimal Flask app...")

app = Flask(__name__)
print("Flask app created")

@app.route('/')
def index():
    return "<h1>Hello from Railway!</h1><p>Minimal app is working!</p>"

@app.route('/ping')
def ping():
    return 'pong', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)