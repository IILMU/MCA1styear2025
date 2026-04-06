"""
Fake News Detector Web Application
Main entry point for running the Flask server
"""
import os
import sys

# Add the app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("FAKE NEWS DETECTOR - Starting Server")
    print("=" * 60)
    print("\n[OK] Flask application initialized")
    print("[OK] Running on http://localhost:5000")
    print("[OK] Press CTRL+C to stop the server\n")
    print("=" * 60 + "\n")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=True,
    )
