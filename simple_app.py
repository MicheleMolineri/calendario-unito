from flask import Flask
import os

print("Starting minimal Flask app...")

app = Flask(__name__)
print("Flask app created")

@app.route('/')
def index():
    print("Request received on /")
    return "<h1>Hello from Railway!</h1><p>Minimal app is working!</p>"

@app.route('/ping')
def ping():
    print("Request received on /ping")
    return 'pong', 200

@app.route('/health')
def health():
    print("Request received on /health")
    return {'status': 'ok', 'timestamp': '2025-09-18'}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))  # Cambiamo porta default
    print(f"Starting server on port {port}")
    print(f"PORT env var: {os.environ.get('PORT')}")
    print(f"Binding to 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)