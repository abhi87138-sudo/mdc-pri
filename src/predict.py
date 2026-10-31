"""
predict.py
=============================================================================
Inference & Hybrid Threat Detection Engine
Project: AI-Driven Social Engineering and Deepfake Defense Platform
Team: Sentinels (Vivek Sharma, Hitesh Brahmi, Akhil Kotwal)
Academic: IIIrd Sem.

Technical Overview:
1. Machine Learning Layer: Multinomial Naive Bayes with TF-IDF representation
   to compute statistical scam probabilities.
2. Threat Heuristic Layer: Pattern scanners detecting social engineering
   triggers (urgency pressure, financial bait, credential harvesting, URLs).
3. Hybrid Risk Fusion: Fuses ML probability (60%) with heuristic indicators (40%)
   to generate an explainable 0-100 risk score and clear breakdown reasons.
=============================================================================
"""

import os
import re
import joblib


class ThreatDetector:
    """
    Hybrid Social Engineering & Phishing Message Detector.
    Integrates trained scikit-learn models with rule-based heuristic checks.
    """

    def __init__(self, model_path=None, vectorizer_path=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_dir = os.path.join(base_dir, "models")
        
        self.model_path = model_path or os.path.join(models_dir, "model.pkl")
        self.vectorizer_path = vectorizer_path or os.path.join(models_dir, "vectorizer.pkl")
        
        self.model = None
        self.vectorizer = None
        self._load_artifacts()

        # Rule-based threat indicators (Social Engineering psychological triggers)
        self.urgency_patterns = [
            r"\b(urgent|urgently|immediately|act now|limited time|expire[sd]?|expires today)\b",
            r"\b(within \d+ hours?|final notice|immediate response|account suspended|blocked)\b",
            r"\b(last chance|action required|suspended immediately|security alert)\b"
        ]

        self.financial_lure_patterns = [
            r"\b(win|winner|won|congratulations|prize|cash|lottery|claim now|reward)\b",
            r"\b(selected|million dollars?|refund|bonus|free gift|jackpot|pay|fee|payment|charge|unpaid|due)\b",
            r"[$£€₹]"
        ]

        self.credential_harvest_patterns = [
            r"\b(verify your account|update your (kyc|pan|details|profile|password))\b",
            r"\b(enter (your )?otp|share (your )?pin|security code|login details|cvv)\b",
            r"\b(bank account|credit card|debit card|net banking|unauthorized transaction)\b"
        ]

        self.url_patterns = [
            r"https?://[^\s]+",
            r"www\.[^\s]+",
            r"\b[a-zA-Z0-9-]+\.(xyz|top|work|click|tk|ml|ga|cf|gq|link|buzz|live|support)\b",
            r"\b(bit\.ly|tinyurl\.com|t\.co|is\.gd|cutt\.ly|ow\.ly)/[^\s]+"
        ]

    def _load_artifacts(self):
        """Loads serialized model and vectorizer artifacts if available."""
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            try:
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
            except Exception as e:
                self.model = None
                self.vectorizer = None
                print(f"[!] Warning: Could not load model artifacts: {e}")
        else:
            self.model = None
            self.vectorizer = None

    def is_model_ready(self):
        """Returns True if the ML model artifacts are loaded and ready."""
        return self.model is not None and self.vectorizer is not None

    def analyze_heuristics(self, text):
        """
        Inspects message for social engineering cues (urgency, lures, URLs, credentials).
        Returns a list of triggered reasons and a heuristic penalty score (0 to 100).
        """
        reasons = []
        heuristic_score = 0
        text_lower = text.lower()

        # 1. Urgency / Fear pressure
        urgency_matches = [p for p in self.urgency_patterns if re.search(p, text_lower)]
        if urgency_matches:
            reasons.append("High urgency or psychological pressure detected (attempts to force impulsive action).")
            heuristic_score += 25

        # 2. Financial or Prize Bait
        lure_matches = [p for p in self.financial_lure_patterns if re.search(p, text_lower)]
        if lure_matches:
            reasons.append("Financial lure, prize, or payment fee incentive detected.")
            heuristic_score += 25

        # 3. Sensitive Credential or Account Target
        cred_matches = [p for p in self.credential_harvest_patterns if re.search(p, text_lower)]
        if cred_matches:
            reasons.append("Solicitation of sensitive credentials, account verification, or banking info detected.")
            heuristic_score += 30

        # 4. Links / Suspicious URLs
        url_matches = [p for p in self.url_patterns if re.search(p, text_lower)]
        if url_matches:
            reasons.append("Suspicious external web link or shortened URL embedded in message.")
            heuristic_score += 20

        # 5. ALL-CAPS shout / aggressive punctuation
        caps_words = [w for w in text.split() if w.isupper() and len(w) > 2]
        if len(caps_words) >= 3 or "!!!" in text or "???" in text:
            reasons.append("Aggressive formatting (excessive uppercase or exclamation points).")
            heuristic_score += 10

        # Cap heuristic score at 100
        heuristic_score = min(heuristic_score, 100)
        return reasons, heuristic_score

    def predict(self, text):
        """
        Performs hybrid classification of an input text message.
        Returns a dictionary with:
        - risk_score: 0 to 100
        - status: 'Safe', 'Suspicious', or 'Dangerous'
        - color: 'green', 'orange', or 'red'
        - ml_probability: 0.0 to 1.0 (or None if model missing)
        - reasons: list of human-readable explanations
        """
        if not text or not str(text).strip():
            return {
                "risk_score": 0,
                "status": "Safe",
                "color": "green",
                "ml_probability": 0.0,
                "reasons": ["No message text was provided. Enter a message to begin analysis."],
                "error": "empty_input"
            }

        cleaned_text = str(text).strip()
        reasons, heuristic_score = self.analyze_heuristics(cleaned_text)

        # Evaluate ML model if loaded
        if self.is_model_ready():
            try:
                tfidf_vec = self.vectorizer.transform([cleaned_text])
                probabilities = self.model.predict_proba(tfidf_vec)[0]
                ml_prob_scam = float(probabilities[1])
                ml_score = ml_prob_scam * 100.0

                if ml_prob_scam >= 0.70:
                    reasons.insert(0, f"ML classifier identified strong scam language patterns ({ml_prob_scam * 100:.1f}% confidence).")
                elif ml_prob_scam >= 0.35:
                    reasons.insert(0, f"ML classifier identified moderate suspicious language patterns ({ml_prob_scam * 100:.1f}% confidence).")
                else:
                    if not reasons:
                        reasons.append("ML classifier analyzed standard conversational patterns consistent with normal safe communication.")
            except Exception as e:
                ml_prob_scam = 0.0
                ml_score = 0.0
                reasons.append(f"Model prediction notice: {e}")
        else:
            ml_prob_scam = None
            ml_score = heuristic_score
            reasons.insert(
                0,
                "Notice: Trained model file not found in 'models/'. Operating in heuristic rule-based fallback mode. Please run 'python src/train.py'."
            )

        # Hybrid Score Calculation
        if ml_prob_scam is not None:
            combined_score = (0.60 * ml_score) + (0.40 * heuristic_score)
            if ml_score > 60 and heuristic_score > 50:
                combined_score = max(combined_score, 85)
        else:
            combined_score = float(heuristic_score)

        risk_score = int(round(max(0, min(100, combined_score))))

        # Determine colored category status
        if risk_score >= 70:
            status = "Dangerous"
            color = "red"
        elif risk_score >= 35:
            status = "Suspicious"
            color = "orange"
        else:
            status = "Safe"
            color = "green"

        return {
            "risk_score": risk_score,
            "status": status,
            "color": color,
            "ml_probability": round(ml_prob_scam, 4) if ml_prob_scam is not None else None,
            "reasons": reasons,
            "error": None
        }


if __name__ == "__main__":
    detector = ThreatDetector()
    test_msgs = [
        "URGENT: Your bank account is locked! Click http://bit.ly/bank-verify to update OTP immediately.",
        "Congratulations! You won a £1000 Walmart gift card! Call 0800123456 now to claim.",
        "Hey Mom, I will be home around 6 PM for dinner. Love you!"
    ]
    print("\n--- Testing ThreatDetector CLI ---")
    for msg in test_msgs:
        res = detector.predict(msg)
        print(f"\nMessage: {msg}")
        print(f"Result : [{res['status'].upper()}] - Risk Score: {res['risk_score']}/100 ({res['color']})")
        print("Reasons:")
        for r in res["reasons"]:
            print(f"  - {r}")
