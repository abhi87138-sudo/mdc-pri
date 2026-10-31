"""
train.py
=============================================================================
Model Training Script for SMS Scam / Phishing Detection
Project: AI-Driven Social Engineering and Deepfake Defense Platform
Team: Sentinels (Vivek Sharma, Hitesh Brahmi, Akhil Kotwal)
Academic: IIIrd Sem.

Pipeline Overview:
1. TF-IDF (Term Frequency - Inverse Document Frequency):
   Converts raw text into numerical feature vectors by weighting words that
   are frequent in a specific message but rare across the entire dataset.
2. Multinomial Naive Bayes (MNB):
   A fast, reliable probabilistic classifier applying Bayes' Theorem for text
   categorization with Laplace smoothing.
=============================================================================
"""

import os
import json
import joblib
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


def load_dataset():
    """
    Locates and loads the SMS Spam Collection dataset from the data directory.
    Supports tab-separated SMSSpamCollection and comma-separated spam.csv.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    tsv_path = os.path.join(data_dir, "SMSSpamCollection")
    csv_path = os.path.join(data_dir, "spam.csv")
    
    if os.path.exists(tsv_path):
        print(f"[*] Loading dataset from: {tsv_path}")
        df = pd.read_csv(tsv_path, sep="\t", header=None, names=["label", "message"], encoding="utf-8")
    elif os.path.exists(csv_path):
        print(f"[*] Loading dataset from: {csv_path}")
        df = pd.read_csv(csv_path, encoding="utf-8")
        if "label" not in df.columns and "v1" in df.columns:
            df = df.rename(columns={"v1": "label", "v2": "message"})
    else:
        raise FileNotFoundError(
            f"Dataset not found in '{data_dir}'. Please provide 'SMSSpamCollection' or 'spam.csv'."
        )
    
    # Drop empty or malformed rows
    df = df.dropna(subset=["label", "message"]).copy()
    # Normalize labels: ham -> 0 (safe), spam -> 1 (scam/phishing)
    df["label"] = df["label"].astype(str).str.strip().str.lower()
    df["target"] = df["label"].map(lambda x: 1 if "spam" in x else 0)
    
    return df


def train():
    """
    Trains the TF-IDF Vectorizer and Multinomial Naive Bayes classifier,
    evaluates performance on a holdout test split, prints real metrics,
    and serializes the trained artifacts and evaluation metrics.
    """
    print("=" * 60)
    print(" AI-Driven Social Engineering Defense - Training Pipeline ")
    print("=" * 60)
    
    df = load_dataset()
    total_samples = len(df)
    spam_count = int(df["target"].sum())
    ham_count = total_samples - spam_count
    
    print(f"[*] Total dataset samples : {total_samples}")
    print(f"    - Safe messages (ham) : {ham_count} ({ham_count / total_samples * 100:.1f}%)")
    print(f"    - Scam messages (spam): {spam_count} ({spam_count / total_samples * 100:.1f}%)")
    
    # Split into 80% train and 20% test sets with fixed random seed for reproducibility
    X_train, X_test, y_train, y_test = train_test_split(
        df["message"],
        df["target"],
        test_size=0.20,
        random_state=42,
        stratify=df["target"]
    )
    
    print(f"[*] Training samples: {len(X_train)} | Test samples: {len(X_test)}")
    
    # TF-IDF Vectorization: extract unigrams and bigrams, lowercase, remove English stop words
    print("[*] Vectorizing text messages using TF-IDF...")
    vectorizer = TfidfVectorizer(
        stop_words="english",
        lowercase=True,
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    # Train Multinomial Naive Bayes Classifier
    print("[*] Training Multinomial Naive Bayes classifier...")
    model = MultinomialNB(alpha=0.1)  # Laplace smoothing parameter
    model.fit(X_train_tfidf, y_train)
    
    # Evaluate model predictions
    y_pred = model.predict(X_test_tfidf)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)
    
    tn, fp, fn, tp = cm.ravel()
    
    print("\n" + "=" * 60)
    print(" REAL EVALUATION RESULTS (Test Set)")
    print("=" * 60)
    print(f" Accuracy        : {acc:.4f} ({acc * 100:.2f}%)")
    print(f" Precision (Spam): {prec:.4f} ({prec * 100:.2f}%)")
    print(f" Recall (Spam)   : {rec:.4f} ({rec * 100:.2f}%)")
    print(f" F1-Score (Spam) : {f1:.4f} ({f1 * 100:.2f}%)")
    print("-" * 60)
    print(" Confusion Matrix:")
    print(f"   True Negatives  (Ham correctly identified)  : {tn}")
    print(f"   False Positives (Ham mistaken for scam)     : {fp}")
    print(f"   False Negatives (Scam missed by model)      : {fn}")
    print(f"   True Positives  (Scam correctly identified) : {tp}")
    print("-" * 60)
    print(" Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Safe", "Scam/Spam"]))
    print("=" * 60)
    
    # Save artifacts to models directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, "model.pkl")
    vectorizer_path = os.path.join(models_dir, "vectorizer.pkl")
    metrics_path = os.path.join(models_dir, "metrics.json")
    
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    
    metrics_payload = {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": [
            [int(tn), int(fp)],
            [int(fn), int(tp)]
        ],
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "total_samples": int(total_samples),
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "algorithm": "Multinomial Naive Bayes + TF-IDF (Unigram + Bigram)",
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=4)
        
    print(f"[+] Model saved to       : {model_path}")
    print(f"[+] Vectorizer saved to  : {vectorizer_path}")
    print(f"[+] Real metrics saved to: {metrics_path}")
    print("[*] Pipeline completed successfully!\n")
    
    return metrics_payload


if __name__ == "__main__":
    train()
