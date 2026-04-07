#!/usr/bin/env python
# coding: utf-8
"""
Biometric Recognition System — Streamlit UI
=============================================
Face recognition  : LFW dataset  → PCA + Calibrated SVM
Voice recognition : Free Spoken Digit Dataset → MFCC + Calibrated SVM

Install:
    pip install streamlit librosa scikit-learn matplotlib joblib sounddevice scipy

Run locally:
    streamlit run biometric_recog_app.py

Deploy free & permanently (shareable on any device — phone/tablet/laptop):
    1. Push this file to a GitHub repo
    2. Go to https://streamlit.io/cloud → "New app" → point to your repo
    3. Get a permanent public URL — no install needed for viewers
"""

# ── Standard library ──────────────────────────────────────────────────────────
import os
import random
import tempfile
import urllib.request
import zipfile

# ── Third-party ───────────────────────────────────────────────────────────────
import joblib
import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wav
import streamlit as st

from sklearn.calibration import CalibratedClassifierCV
from sklearn.datasets import fetch_lfw_people
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

FSDD_URL         = "https://github.com/Jakobovski/free-spoken-digit-dataset/archive/refs/heads/master.zip"
FSDD_ZIP         = "fsdd.zip"
FSDD_DIR         = "fsdd/free-spoken-digit-dataset-master/recordings"
FACE_MODEL_PATH  = "face_model.pkl"
VOICE_MODEL_PATH = "voice_model.pkl"

FACE_THRESHOLD   = 0.70
VOICE_THRESHOLD  = 0.30
IMG_H, IMG_W     = 50, 37


# ══════════════════════════════════════════════════════════════════════════════
# CORE ML
# ══════════════════════════════════════════════════════════════════════════════

def load_face_data():
    lfw = fetch_lfw_people(min_faces_per_person=70, resize=0.4)
    X_train, X_test, y_train, y_test = train_test_split(
        lfw.data, lfw.target, test_size=0.2, random_state=42
    )
    return lfw, X_train, X_test, y_train, y_test


def train_face_model(X_train, y_train):
    pca   = PCA(n_components=150, whiten=True, random_state=42)
    svm   = CalibratedClassifierCV(SVC(kernel="rbf", class_weight="balanced"))
    model = make_pipeline(pca, svm)
    model.fit(X_train, y_train)
    return model


def download_fsdd():
    if not os.path.isdir(FSDD_DIR):
        urllib.request.urlretrieve(FSDD_URL, FSDD_ZIP)
        with zipfile.ZipFile(FSDD_ZIP, "r") as zf:
            zf.extractall("fsdd")


def extract_mfcc(file_path, n_mfcc=40):
    audio, sr = librosa.load(file_path, sr=None)
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
    return np.mean(mfcc.T, axis=0)


def load_voice_data():
    files = os.listdir(FSDD_DIR)
    X, y = [], []
    for fname in files:
        if not fname.endswith(".wav"):
            continue
        digit    = int(fname.split("_")[0])
        features = extract_mfcc(os.path.join(FSDD_DIR, fname))
        X.append(features)
        y.append(digit)
    return files, np.array(X), np.array(y)


def train_voice_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = CalibratedClassifierCV(SVC(kernel="rbf", class_weight="balanced"))
    model.fit(X_train, y_train)
    return model, X_test, y_test


def predict_face(model, lfw, image, threshold):
    proba    = model.predict_proba([image])[0]
    max_prob = proba.max()
    pred     = model.predict([image])[0]
    name     = lfw.target_names[pred] if max_prob >= threshold else "Unknown"
    return name, max_prob


def predict_voice(model, features, threshold):
    proba    = model.predict_proba([features])[0]
    max_prob = proba.max()
    pred     = model.predict([features])[0]
    digit    = str(pred) if max_prob >= threshold else "Unknown"
    return digit, max_prob


# ══════════════════════════════════════════════════════════════════════════════
# CACHED STARTUP  (runs once per session)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner="⏳ Loading datasets & training models — first run takes ~60s...")
def load_all():
    # Face
    lfw, X_train_face, X_test_face, y_train_face, y_test_face = load_face_data()
    if os.path.exists(FACE_MODEL_PATH):
        face_model = joblib.load(FACE_MODEL_PATH)
    else:
        face_model = train_face_model(X_train_face, y_train_face)
        joblib.dump(face_model, FACE_MODEL_PATH)

    # Voice
    download_fsdd()
    files, X_voice, y_voice = load_voice_data()
    if os.path.exists(VOICE_MODEL_PATH):
        voice_model = joblib.load(VOICE_MODEL_PATH)
        _, X_test_voice, _, y_test_voice = train_test_split(
            X_voice, y_voice, test_size=0.2, random_state=42
        )
    else:
        voice_model, X_test_voice, y_test_voice = train_voice_model(X_voice, y_voice)
        joblib.dump(voice_model, VOICE_MODEL_PATH)

    # Accuracies
    face_preds  = [predict_face(face_model, lfw, img, FACE_THRESHOLD)[0] for img in X_test_face]
    face_actual = [lfw.target_names[i] for i in y_test_face]
    face_acc    = sum(p == a for p, a in zip(face_preds, face_actual)) / len(face_actual) * 100

    voice_preds  = [predict_voice(voice_model, f, VOICE_THRESHOLD)[0] for f in X_test_voice]
    voice_actual = [str(i) for i in y_test_voice]
    voice_acc    = sum(p == a for p, a in zip(voice_preds, voice_actual)) / len(voice_actual) * 100

    return dict(
        lfw=lfw, face_model=face_model, voice_model=voice_model,
        files=files,
        X_test_face=X_test_face, y_test_face=y_test_face,
        X_test_voice=X_test_voice, y_test_voice=y_test_voice,
        face_acc=face_acc, voice_acc=voice_acc,
    )


# ══════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def result_box(correct, predicted, actual, confidence, threshold):
    color = "#2ecc71" if correct else "#e74c3c"
    icon  = "✅ CORRECT" if correct else "❌ WRONG"
    st.markdown(f"""
<div style="border-left:5px solid {color}; padding:12px 18px;
            border-radius:6px; background:#f9f9f9; margin-top:14px;">
    <b>🤖 Predicted :</b> {predicted}<br>
    <b>✅ Actual    :</b> {actual}<br>
    <b>💯 Confidence:</b> {confidence*100:.1f}%
    <span style="color:gray; font-size:0.9em;">(threshold {threshold*100:.0f}%)</span><br>
    <b>Result       :</b>
    <span style="color:{color}; font-weight:bold;">{icon}</span>
</div>
""", unsafe_allow_html=True)


def voice_result_box(predicted, confidence, threshold):
    color = "#2ecc71" if predicted != "Unknown" else "#e67e22"
    st.markdown(f"""
<div style="border-left:5px solid {color}; padding:12px 18px;
            border-radius:6px; background:#f9f9f9; margin-top:14px;">
    <b>🤖 Predicted digit :</b> {predicted}<br>
    <b>💯 Confidence      :</b> {confidence*100:.1f}%
    <span style="color:gray; font-size:0.9em;">(threshold {threshold*100:.0f}%)</span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STREAMLIT APP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    st.set_page_config(
        page_title="Biometric Recognition System",
        page_icon="🤖",
        layout="wide",
    )

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#2E86AB; padding:22px 28px; border-radius:10px; margin-bottom:22px;">
        <h1 style="color:white; text-align:center; margin:0; font-family:Georgia;">
            🤖 Biometric Recognition System
        </h1>
        <p style="color:#E8F4F8; text-align:center; margin:6px 0 0;">
            Face &amp; Voice Recognition · PCA + SVM + MFCC · Built with Streamlit
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Load everything ───────────────────────────────────────────────────────
    S = load_all()
    lfw, face_model, voice_model = S["lfw"], S["face_model"], S["voice_model"]

    # ── Stats bar ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("😊 Face Accuracy",  f"{S['face_acc']:.2f}%")
    c2.metric("🎙️ Voice Accuracy", f"{S['voice_acc']:.2f}%")
    c3.metric("⚠️ Confidence Threshold", f"{FACE_THRESHOLD*100:.0f}% / {VOICE_THRESHOLD*100:.0f}%")
    c4.metric("👥 People in Dataset", len(lfw.target_names))

    st.divider()

    # ── Main tabs ─────────────────────────────────────────────────────────────
    tab_face, tab_voice, tab_report = st.tabs(
        ["😊  Face Recognition", "🎙️  Voice Recognition", "📋  Reports"]
    )

    # ════════════════════════════════════════════════════════════════
    # FACE TAB
    # ════════════════════════════════════════════════════════════════
    with tab_face:
        st.subheader("Face Recognition")
        st.caption("Select a person — a random test image is picked and identified.")

        col_ctrl, col_out = st.columns([1, 2])

        with col_ctrl:
            person_name = st.selectbox("👤 Person", list(lfw.target_names))
            threshold_f = st.slider(
                "Confidence threshold", 0.30, 0.99, FACE_THRESHOLD, 0.01, key="ft"
            )
            run_face  = st.button("🔍 Recognise Face", use_container_width=True, type="primary")
            show_grid = st.button("🖼️ Show Sample Grid", use_container_width=True)

        with col_out:
            if show_grid:
                fig, axes = plt.subplots(2, 5, figsize=(12, 5))
                for i, ax in enumerate(axes.flat):
                    ax.imshow(lfw.images[i], cmap="gray")
                    ax.set_title(lfw.target_names[lfw.target[i]], fontsize=8)
                    ax.axis("off")
                plt.suptitle("Sample Faces from LFW Dataset")
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)

            if run_face:
                person_idx = list(lfw.target_names).index(person_name)
                pool = [(img, lbl) for img, lbl in
                        zip(S["X_test_face"], S["y_test_face"]) if lbl == person_idx]

                if not pool:
                    st.warning("No test images available for this person.")
                else:
                    sample_img, actual = random.choice(pool)

                    fig, ax = plt.subplots(figsize=(3, 3.5))
                    ax.imshow(sample_img.reshape(IMG_H, IMG_W), cmap="gray")
                    ax.set_title("Input Face", fontsize=11)
                    ax.axis("off")
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close(fig)

                    name, conf = predict_face(face_model, lfw, sample_img, threshold_f)
                    result_box(
                        correct=name == lfw.target_names[actual],
                        predicted=name,
                        actual=lfw.target_names[actual],
                        confidence=conf,
                        threshold=threshold_f,
                    )

    # ════════════════════════════════════════════════════════════════
    # VOICE TAB
    # ════════════════════════════════════════════════════════════════
    with tab_voice:
        st.subheader("Voice Recognition")

        v_tab1, v_tab2 = st.tabs(["📂 From Dataset", "🎤 Upload a WAV File"])

        # ── Dataset sub-tab ───────────────────────────────────────
        with v_tab1:
            st.caption("Pick a digit — a random dataset sample is used for prediction.")
            col_vc, col_vo = st.columns([1, 2])

            with col_vc:
                digit       = st.selectbox("🔢 Digit (0–9)", list(range(10)))
                threshold_v = st.slider(
                    "Confidence threshold", 0.10, 0.99, VOICE_THRESHOLD, 0.01, key="vt"
                )
                run_voice = st.button(
                    "🎵 Recognise from Dataset", use_container_width=True, type="primary"
                )

            with col_vo:
                if run_voice:
                    wav_files = [
                        f for f in S["files"]
                        if f.startswith(str(digit)) and f.endswith(".wav")
                    ]
                    if not wav_files:
                        st.warning(f"No audio files found for digit {digit}.")
                    else:
                        sample      = random.choice(wav_files)
                        sample_path = os.path.join(FSDD_DIR, sample)

                        st.audio(sample_path, format="audio/wav")
                        st.caption(f"File: `{sample}`")

                        features   = extract_mfcc(sample_path)
                        pred, conf = predict_voice(voice_model, features, threshold_v)
                        result_box(
                            correct=pred == str(digit),
                            predicted=pred,
                            actual=str(digit),
                            confidence=conf,
                            threshold=threshold_v,
                        )

        # ── Upload sub-tab ────────────────────────────────────────
        with v_tab2:
            st.caption("Upload a `.wav` file of a spoken digit (0–9) to predict it.")
            threshold_u = st.slider(
                "Confidence threshold", 0.10, 0.99, VOICE_THRESHOLD, 0.01, key="ut"
            )
            uploaded  = st.file_uploader("📁 Upload WAV file", type=["wav"])
            run_upload = st.button("🤖 Predict Digit", use_container_width=True, type="primary")

            if uploaded and run_upload:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(uploaded.read())
                    tmp_path = tmp.name

                st.audio(tmp_path, format="audio/wav")
                features   = extract_mfcc(tmp_path)
                pred, conf = predict_voice(voice_model, features, threshold_u)
                os.remove(tmp_path)
                voice_result_box(pred, conf, threshold_u)

    # ════════════════════════════════════════════════════════════════
    # REPORTS TAB
    # ════════════════════════════════════════════════════════════════
    with tab_report:
        st.subheader("Full Classification Reports")

        r1, r2 = st.columns(2)

        with r1:
            st.markdown("#### 😊 Face Model")
            if st.button("Generate Face Report", use_container_width=True):
                y_pred = face_model.predict(S["X_test_face"])
                acc    = (y_pred == S["y_test_face"]).mean() * 100
                report = classification_report(
                    S["y_test_face"], y_pred, target_names=lfw.target_names
                )
                st.metric("Accuracy", f"{acc:.2f}%")
                st.code(report, language=None)

        with r2:
            st.markdown("#### 🎙️ Voice Model")
            if st.button("Generate Voice Report", use_container_width=True):
                y_pred = voice_model.predict(S["X_test_voice"])
                acc    = (y_pred == S["y_test_voice"]).mean() * 100
                report = classification_report(
                    S["y_test_voice"], y_pred,
                    labels=list(range(10)),
                    target_names=[str(i) for i in range(10)],
                )
                st.metric("Accuracy", f"{acc:.2f}%")
                st.code(report, language=None)


if __name__ == "__main__":
    main()
