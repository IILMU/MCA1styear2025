import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib
import os
from nltk.corpus import stopwords
import nltk

# Download NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def build_and_train_model(dataset_path='data/fake_news_dataset.csv'):
    """Build and train a high-accuracy fake news detector model."""
    
    print("Loading dataset...")
    df = pd.read_csv(dataset_path)
    
    # Combine title and text for better feature extraction
    df['combined_text'] = df['title'] + ' ' + df['text']
    
    X = df['combined_text']
    y = df['label']
    
    # Split data
    print("Splitting data into train (80%) and test (20%)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Create TF-IDF vectorizer with optimized parameters
    print("Vectorizing text with TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=5,
        max_df=0.8,
        sublinear_tf=True,
        stop_words='english'
    )
    
    # Create ensemble model with multiple classifiers
    print("Training ensemble model...")
    
    # TF-IDF + Logistic Regression (fast and accurate)
    model = Pipeline([
        ('tfidf', vectorizer),
        ('classifier', LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced',
            solver='lbfgs'
        ))
    ])
    
    model.fit(X_train, y_train)
    
    # Make predictions
    print("Evaluating model on test set...")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print("\n" + "="*50)
    print("MODEL PERFORMANCE METRICS")
    print("="*50)
    print(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"Precision: {precision:.4f} ({precision*100:.2f}%)")
    print(f"Recall:    {recall:.4f} ({recall*100:.2f}%)")
    print(f"F1 Score:  {f1:.4f}")
    print("="*50 + "\n")
    
    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    print(f"True Negatives:  {tn}")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")
    print(f"True Positives:  {tp}\n")
    
    # Save the model
    print("Saving model...")
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/fake_news_detector.pkl')
    
    print("Model saved successfully to: models/fake_news_detector.pkl")
    
    return model, accuracy

if __name__ == "__main__":
    build_and_train_model()
