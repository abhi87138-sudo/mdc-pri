"""
predict.py
=============================================================================
Inference & Hybrid Threat Detection Engine
Project: AI-Driven Social Engineering and Deepfake Defense Platform
Team: Sentinels (Vivek Sharma, Hitesh Brahmi, Akhil Kotwal)
=============================================================================
"""

import os
import re
import joblib


class ThreatDetector:
    """
    Hybrid Social Engineering & Phishing Message Detector.
    Integrates trained scikit-learn models with heuristic rule-based pattern checks
    and deep psychological vector diagnostics.
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
            r"\b(last chance|action required|suspended immediately|security alert|deactivated today)\b"
        ]

        self.financial_lure_patterns = [
            r"\b(win|winner|won|congratulations|prize|cash|lottery|claim now|reward|voucher)\b",
            r"\b(selected|million dollars?|refund|bonus|free gift|gift card|jackpot|pay|fee|payment|charge|unpaid|due)\b",
            r"[$£€₹]"
        ]

        self.credential_harvest_patterns = [
            r"\b(verify your account|update your (kyc|pan|details|profile|password))\b",
            r"\b(enter (your )?otp|share (your )?pin|security code|login details|cvv|password)\b",
            r"\b(confirm identity|unlock account|security check|authenticate|reactivate)\b"
        ]

        self.authority_patterns = [
            r"\b(hdfc|sbi|icici|paypal|bank|apple|google|microsoft|amazon|fedex|usps|dhl|support|admin|security team)\b"
        ]

        self.link_pattern = r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/[^\s]*)?)"

    def _load_artifacts(self):
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
            else:
                self.model = None
                self.vectorizer = None
        except Exception:
            self.model = None
            self.vectorizer = None

    def analyze_heuristics(self, text):
        reasons = []
        heuristic_score = 0
        vectors = {"urgency": 0, "financial": 0, "credential": 0, "authority": 0}

        text_lower = text.lower()

        # 1. Urgency Pressure
        urgency_hits = 0
        for pattern in self.urgency_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                urgency_hits += len(matches)
        if urgency_hits > 0:
            heuristic_score += min(35, 15 + urgency_hits * 10)
            vectors["urgency"] = min(100, 30 + urgency_hits * 25)
            reasons.append("High-pressure psychological urgency detected (triggers immediate panic action).")

        # 2. Financial Bait
        financial_hits = 0
        for pattern in self.financial_lure_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                financial_hits += len(matches)
        if financial_hits > 0:
            heuristic_score += min(30, 15 + financial_hits * 8)
            vectors["financial"] = min(100, 30 + financial_hits * 20)
            reasons.append("Financial bait/coercive lure detected (cash, reward, unexpected fee, or prize claim).")

        # 3. Credential Harvesting
        credential_hits = 0
        for pattern in self.credential_harvest_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                credential_hits += len(matches)
        if credential_hits > 0:
            heuristic_score += min(35, 20 + credential_hits * 10)
            vectors["credential"] = min(100, 40 + credential_hits * 30)
            reasons.append("Credential or identity harvesting solicitation (requests KYC, OTP, PIN, or login).")

        # 4. Authority Impersonation
        authority_hits = 0
        for pattern in self.authority_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                authority_hits += len(matches)
        if authority_hits > 0:
            heuristic_score += min(20, 10 + authority_hits * 5)
            vectors["authority"] = min(100, 25 + authority_hits * 25)
            reasons.append("Brand or institutional authority impersonation (mimics major bank, tech service, or courier).")

        # 5. Hyperlink Presence
        if re.search(self.link_pattern, text):
            heuristic_score += 15
            reasons.append("Embedded hyperlink or external redirect target identified.")

        heuristic_score = min(heuristic_score, 100)
        return reasons, heuristic_score, vectors

    def inspect_urls(self, text):
        raw_urls = re.findall(r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.(?:com|org|net|xyz|top|click|link|cc|biz)/[^\s]*)", text)
        results = []
        for url in raw_urls:
            url_clean = url.rstrip('.,;!?"\')]}')
            is_shortener = bool(re.search(r"\b(bit\.ly|tinyurl\.com|t\.co|goo\.gl|is\.gd|ow\.ly|buff\.ly|rebrand\.ly)\b", url_clean, re.I))
            is_suspicious_tld = bool(re.search(r"\.(xyz|top|click|cc|club|live|fit|online|cam|link|pw|work|surf)/?.*$", url_clean, re.I))
            is_insecure_http = url_clean.startswith("http://")
            
            risk_badge = "Low Risk"
            if is_shortener or is_suspicious_tld:
                risk_badge = "High Risk"
            elif is_insecure_http:
                risk_badge = "Medium Risk"

            results.append({
                "url": url_clean,
                "is_shortener": is_shortener,
                "is_suspicious_tld": is_suspicious_tld,
                "is_insecure_http": is_insecure_http,
                "risk_badge": risk_badge
            })
        return results

    def classify_attack_vector(self, text, vectors):
        t_low = text.lower()
        if vectors["credential"] >= 40 or "kyc" in t_low or "pan" in t_low or "otp" in t_low or "pin" in t_low or "bank" in t_low or "hdfc" in t_low or "sbi" in t_low:
            return {
                "name": "Banking & KYC Credential Harvesting (Smishing)",
                "icon": "lock",
                "color": "#EF4444",
                "badge": "CRITICAL RISK",
                "summary": "Impersonates legitimate financial institutions using synthetic urgency to coerce victim into submitting 2FA codes, account passwords, or identity documents via spoofed landing pages."
            }
        elif vectors["financial"] >= 40 or "winner" in t_low or "prize" in t_low or "lottery" in t_low or "gift card" in t_low or "reward" in t_low:
            return {
                "name": "Advance-Fee & Lottery Bait Scam",
                "icon": "sparkles",
                "color": "#F59E0B",
                "badge": "FINANCIAL FRAUD",
                "summary": "Fabricates substantial financial gains (prizes, vouchers, unclaimed funds) to prompt the victim to call premium-rate numbers or pay advance processing fees."
            }
        elif "parcel" in t_low or "usps" in t_low or "fedex" in t_low or "dhl" in t_low or "shipment" in t_low or "customs" in t_low or "duty" in t_low:
            return {
                "name": "Courier & Package Delivery Impersonation",
                "icon": "radar",
                "color": "#F97316",
                "badge": "LOGISTICS PHISH",
                "summary": "Claims a pending package delivery is detained due to address verification or a tiny unpaid duty fee, aiming to extract credit card details."
            }
        elif vectors["urgency"] >= 40:
            return {
                "name": "Coercive Panic / Account Suspension Threat",
                "icon": "alert",
                "color": "#EF4444",
                "badge": "COGNITIVE EXPLOIT",
                "summary": "Weaponizes immediate deadline pressure ('within 24 hours', 'immediate action required') to bypass rational critical thinking."
            }
        else:
            return {
                "name": "Benign / General Conversational Text",
                "icon": "shield-check",
                "color": "#10B981",
                "badge": "BENIGN TRAFFIC",
                "summary": "Standard interpersonal or business messaging showing no significant deceptive hallmarks or manipulation vectors."
            }

    def generate_token_heatmap(self, text):
        words = text.split()
        tagged_tokens = []
        for word in words:
            w_clean = re.sub(r"[^a-zA-Z0-9$€£₹]", "", word).lower()
            tag = "normal"
            if re.search(r"https?://|www\.|\.(com|org|xyz|net|top|click)", word, re.I):
                tag = "link"
            elif any(re.search(p, w_clean) for p in self.urgency_patterns):
                tag = "urgency"
            elif any(re.search(p, w_clean) for p in self.financial_lure_patterns) or re.search(r"[$€£₹]", word):
                tag = "financial"
            elif any(re.search(p, w_clean) for p in self.credential_harvest_patterns):
                tag = "credential"
            tagged_tokens.append((word, tag))
        return tagged_tokens

    def predict(self, text):
        if not text or not text.strip():
            return {
                "risk_score": 0,
                "status": "Safe",
                "ml_probability": 0.0,
                "reasons": ["Payload input is empty."],
                "vectors": {"urgency": 0, "financial": 0, "credential": 0, "authority": 0},
                "attack_vector": self.classify_attack_vector("", {"urgency": 0, "financial": 0, "credential": 0, "authority": 0}),
                "urls": [],
                "tokens": []
            }

        reasons, heuristic_score, vectors = self.analyze_heuristics(text)
        urls = self.inspect_urls(text)
        attack_vector = self.classify_attack_vector(text, vectors)
        tokens = self.generate_token_heatmap(text)

        ml_prob = None
        if self.model is not None and self.vectorizer is not None:
            try:
                features = self.vectorizer.transform([text])
                probs = self.model.predict_proba(features)[0]
                classes = list(self.model.classes_)
                
                if 1 in classes:
                    spam_index = classes.index(1)
                elif "spam" in classes:
                    spam_index = classes.index("spam")
                else:
                    spam_index = 1
                ml_prob = float(probs[spam_index])
            except Exception:
                ml_prob = None

        if ml_prob is not None:
            ml_score = ml_prob * 100
            hybrid_score = int(round(0.60 * ml_score + 0.40 * heuristic_score))
        else:
            hybrid_score = int(heuristic_score)

        hybrid_score = max(0, min(100, hybrid_score))

        if hybrid_score < 30:
            status = "Safe"
        elif hybrid_score <= 65:
            status = "Suspicious"
        else:
            status = "Dangerous"

        if not reasons:
            reasons.append("No active social engineering markers, urgency triggers, or scam patterns identified.")

        return {
            "risk_score": hybrid_score,
            "status": status,
            "ml_probability": ml_prob,
            "reasons": reasons,
            "vectors": vectors,
            "attack_vector": attack_vector,
            "urls": urls,
            "tokens": tokens
        }
