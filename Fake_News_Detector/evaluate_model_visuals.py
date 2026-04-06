"""
Evaluate the fake news detector and generate labeled plots.

Outputs:
- evaluation_outputs/confusion_matrix.png
- evaluation_outputs/model_metrics.png
"""

import os
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(BASE_DIR / ".matplotlib"))

import matplotlib.pyplot as plt

OUTPUT_DIR = BASE_DIR / "evaluation_outputs"
CLASS_NAMES = ["Real News", "Fake News"]


def resolve_existing_path(candidates):
    """Return the first existing path from a list of candidates."""
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Could not find any of these paths:\n- "
        + "\n- ".join(str(path) for path in candidates)
    )


def load_dataset():
    """Load the dataset used by the project."""
    dataset_path = resolve_existing_path(
        [
            BASE_DIR / "data" / "fake_news_dataset.csv",
            BASE_DIR / "fake_news_dataset.csv",
        ]
    )

    df = pd.read_csv(dataset_path)
    required_columns = {"title", "text", "label"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(
            f"Dataset is missing required columns: {', '.join(sorted(missing_columns))}"
        )

    df["combined_text"] = df["title"].fillna("") + " " + df["text"].fillna("")
    return df, dataset_path


def load_model():
    """Load the trained model artifact."""
    model_path = resolve_existing_path(
        [
            BASE_DIR / "models" / "fake_news_detector.pkl",
            BASE_DIR / "fake_news_detector.pkl",
        ]
    )
    return joblib.load(model_path), model_path


def prepare_test_split(df):
    """Recreate the project's test split for consistent evaluation."""
    x = df["combined_text"]
    y = df["label"]

    _, x_test, _, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )
    return x_test, y_test


def create_confusion_matrix_plot(y_test, y_pred):
    """Save a labeled confusion matrix plot."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    cm = confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(7, 6))
    display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=CLASS_NAMES)
    display.plot(ax=ax, cmap="Blues", colorbar=False, values_format="d")

    ax.set_title("Confusion Matrix for Fake News Detector", fontsize=14, pad=16)
    ax.set_xlabel("Predicted Label", fontsize=12)
    ax.set_ylabel("Actual Label", fontsize=12)
    plt.tight_layout()

    output_path = OUTPUT_DIR / "confusion_matrix.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path, cm


def create_metrics_plot(metrics):
    """Save a labeled bar chart for model performance metrics."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    metric_names = list(metrics.keys())
    metric_values = list(metrics.values())
    colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.bar(metric_names, metric_values, color=colors, width=0.6)

    ax.set_title("Fake News Detector Performance Metrics", fontsize=14, pad=16)
    ax.set_xlabel("Evaluation Metrics", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_ylim(0, 1.05)
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    for bar, value in zip(bars, metric_values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.02,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    plt.tight_layout()

    output_path = OUTPUT_DIR / "model_metrics.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def main():
    """Run evaluation and generate plots."""
    df, dataset_path = load_dataset()
    model, model_path = load_model()
    x_test, y_test = prepare_test_split(df)
    y_pred = model.predict(x_test)

    metrics = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
        "F1 Score": f1_score(y_test, y_pred),
    }

    confusion_matrix_path, cm = create_confusion_matrix_plot(y_test, y_pred)
    metrics_plot_path = create_metrics_plot(metrics)

    print("=" * 60)
    print("MODEL EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Dataset used : {dataset_path}")
    print(f"Model used   : {model_path}")
    print()
    for metric_name, metric_value in metrics.items():
        print(f"{metric_name:<10}: {metric_value:.4f} ({metric_value * 100:.2f}%)")
    print()
    print("Confusion Matrix")
    print(cm)
    print()
    print(f"Saved confusion matrix plot to: {confusion_matrix_path}")
    print(f"Saved metrics graph to        : {metrics_plot_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
