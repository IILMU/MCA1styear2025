from datetime import datetime
import os

import joblib
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "fake_news_detector.pkl")

try:
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None


def predict_news(title, text):
    """Predict if news is fake or real."""
    if model is None:
        return None, None, "Model not loaded"

    try:
        combined_text = title + " " + text
        prediction = model.predict([combined_text])[0]
        confidence = model.predict_proba([combined_text])[0]

        is_fake = bool(prediction == 1)
        confidence_score = float(max(confidence) * 100)

        return is_fake, confidence_score, None
    except Exception as e:
        return None, None, str(e)


@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """API endpoint for fake news prediction."""
    try:
        data = request.get_json()

        title = data.get("title", "").strip()
        text = data.get("text", "").strip()

        if not title or not text:
            return jsonify({
                "error": "Both title and text are required",
                "success": False,
            }), 400

        is_fake, confidence, error = predict_news(title, text)

        if error:
            return jsonify({
                "error": error,
                "success": False,
            }), 500

        return jsonify({
            "success": True,
            "title": title,
            "is_fake": is_fake,
            "confidence": confidence,
            "prediction": "FAKE NEWS" if is_fake else "REAL NEWS",
            "message": f"This news is {'likely FAKE' if is_fake else 'likely REAL'} with {confidence:.1f}% confidence",
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        return jsonify({
            "error": f"Prediction error: {str(e)}",
            "success": False,
        }), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat(),
    })


@app.route("/api/info", methods=["GET"])
def app_info():
    """Get application information."""
    return jsonify({
        "app_name": "Fake News Detector",
        "version": "1.0.0",
        "description": "AI-powered fake news detection system using machine learning",
        "model_status": "loaded" if model is not None else "not_loaded",
        "accuracy": "94%",
        "features": ["Title analysis", "Content analysis", "Confidence scoring"],
        "timestamp": datetime.now().isoformat(),
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
