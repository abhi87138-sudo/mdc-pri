"""
predict.py
=============================================================================
Inference & Hybrid Threat Detection Engine
Brand: DEEPFAKE DEFENSE
Team: Sentinels (Vivek Sharma, Hitesh Brahmi, Akhil Kotwal)

Technical Overview:
1. Machine Learning Layer: Multinomial Naive Bayes with TF-IDF representation
   to compute statistical scam probabilities.
2. Threat Heuristic Layer: Pattern scanners detecting social engineering
   triggers (urgency pressure, financial bait, credential harvesting, URLs,
   electricity bill fraud, UPI scams, courier impersonation, Aadhaar/PAN scams).
3. Psychological Vector Profiling: Quantifies Urgency, Financial Bait, Credential
   Theft, and Authority Impersonation vectors.
4. Deep URL Security Diagnostics: Inspects embedded hyperlinks for obfuscation,
   shorteners, IP addresses, and risky TLDs.
5. Hybrid Risk Fusion: Fuses ML probability (60%) with heuristic indicators (40%)
   to generate an explainable 0-100 risk score and actionable safety recommendations.
=============================================================================
"""

import os
import re
import urllib.parse
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
            r"\b(last chance|action required|suspended immediately|security alert|deactivated today)\b",
            r"\b(tonight by \d+|power will be disconnected|electricity disconnected|last day)\b"
        ]

        self.financial_lure_patterns = [
            r"\b(win|winner|won|congratulations|prize|cash|lottery|claim now|reward|voucher)\b",
            r"\b(selected|million dollars?|refund|bonus|free gift|gift card|jackpot|pay|fee|payment|charge|unpaid|due)\b",
            r"\b(cashback|credited|refund approved|kbc|lucky draw|earn daily|part time job)\b",
            r"[$£€₹]"
        ]

        self.credential_harvest_patterns = [
            r"\b(verify your account|update your (kyc|pan|details|profile|password|aadhaar))\b",
            r"\b(enter (your )?otp|share (your )?pin|security code|login details|cvv|password)\b",
            r"\b(bank account|credit card|debit card|net banking|unauthorized transaction|card will be deactivated)\b",
            r"\b(link aadhaar|pan card blocked|kyc suspended|update kyc immediately)\b"
        ]

        self.authority_patterns = [
            r"\b(hdfc|sbi|icici|axis|pnb|bob|kotak|canara|union bank|paytm|phonepe|gpay|google pay)\b",
            r"\b(chase|wells fargo|bank of america|paypal|amazon|apple|microsoft|netflix)\b",
            r"\b(customs|income tax|police|cbi|fbi|irs|reserve bank|rbi|support desk|fraud prevention|electricity board|discom)\b"
        ]

        self.upi_patterns = [
            r"\b(upi pin|send money to receive|scan qr to receive|approve request in gpay|phonepe request)\b",
            r"\b(collect request|enter upi pin to get|credited via upi)\b"
        ]

        self.electricity_patterns = [
            r"\b(electricity|power|power supply|discom|bijli|cut off|bill unpaid|call electricity officer)\b"
        ]

        self.url_patterns = [
            r"https?://[^\s]+",
            r"www\.[^\s]+",
            r"\b[a-zA-Z0-9-]+\.(xyz|top|work|click|tk|ml|ga|cf|gq|link|buzz|live|support|club|cc|online|site|shop)\b(/[^\s]*)?",
            r"\b(bit\.ly|tinyurl\.com|t\.co|is\.gd|cutt\.ly|ow\.ly|shorturl\.at)/[^\s]+"
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

    def inspect_urls(self, text):
        """
        Extracts and deeply inspects embedded URLs for domain security risks.
        """
        urls_found = []
        raw_matches = re.findall(r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(?:com|org|net|xyz|top|work|click|tk|ml|ga|cf|gq|link|buzz|live|support|club|cc|online|site|shop|info)/[^\s]*)", text, re.IGNORECASE)
        
        seen = set()
        for raw_url in raw_matches:
            url_str = raw_url.rstrip('.,;!?"\')]}')
            if url_str in seen:
                continue
            seen.add(url_str)

            # Deep domain inspection
            is_shortener = any(s in url_str.lower() for s in ["bit.ly", "tinyurl", "t.co", "is.gd", "cutt.ly", "shorturl.at"])
            is_http = url_str.lower().startswith("http://")
            is_suspicious_tld = any(tld in url_str.lower() for tld in [".xyz", ".top", ".work", ".click", ".tk", ".ml", ".link", ".buzz", ".club", ".cc", ".site", ".online"])
            is_ip_address = bool(re.search(r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", url_str))
            
            # Risk assessment for URL
            risk_points = 0
            details = []
            if is_shortener:
                risk_points += 40
                details.append("URL Shortener used (hides the destination domain)")
            if is_suspicious_tld:
                risk_points += 35
                details.append("High-risk / free TLD frequently abused by scammers")
            if is_ip_address:
                risk_points += 45
                details.append("Raw IP address used instead of reputable domain name")
            if is_http:
                risk_points += 20
                details.append("Insecure HTTP protocol (unencrypted connection)")

            if risk_points >= 40:
                risk_badge = "High Risk"
            elif risk_points >= 20:
                risk_badge = "Medium Risk"
            else:
                risk_badge = "Low Risk"

            urls_found.append({
                "url": url_str,
                "is_shortener": is_shortener,
                "is_insecure_http": is_http,
                "is_suspicious_tld": is_suspicious_tld,
                "is_ip_address": is_ip_address,
                "risk_badge": risk_badge,
                "details": details
            })
        return urls_found

    def analyze_heuristics(self, text):
        """
        Inspects message for social engineering cues (urgency, lures, URLs, credentials).
        Returns reasons, heuristic penalty score, and psychological vector metrics.
        """
        reasons = []
        heuristic_score = 0
        text_lower = text.lower()

        # Vector scores (0 - 100 scale)
        vec_urgency = 0
        vec_financial = 0
        vec_credential = 0
        vec_authority = 0

        # 1. Urgency / Fear pressure
        urgency_matches = [p for p in self.urgency_patterns if re.search(p, text_lower)]
        if urgency_matches:
            reasons.append("High urgency or psychological pressure detected (attempts to force panic action).")
            heuristic_score += 25
            vec_urgency = min(100, 45 + len(urgency_matches) * 25)

        # 2. Financial or Prize Bait
        lure_matches = [p for p in self.financial_lure_patterns if re.search(p, text_lower)]
        if lure_matches:
            reasons.append("Financial lure, cashback bait, prize, or fee payment incentive detected.")
            heuristic_score += 25
            vec_financial = min(100, 45 + len(lure_matches) * 25)

        # 3. Sensitive Credential or Account Target (KYC, PAN, Aadhaar, OTP)
        cred_matches = [p for p in self.credential_harvest_patterns if re.search(p, text_lower)]
        if cred_matches:
            reasons.append("Solicitation of sensitive credentials (KYC, PAN, Aadhaar, PIN, or OTP) detected.")
            heuristic_score += 35
            vec_credential = min(100, 50 + len(cred_matches) * 25)

        # 4. Authority / Institution Spoof (SBI, HDFC, ICICI, Electricity Board, Govt)
        auth_matches = [p for p in self.authority_patterns if re.search(p, text_lower)]
        if auth_matches:
            reasons.append("Recognizable financial institution, public utility, or corporate brand spoofed.")
            heuristic_score += 20
            vec_authority = min(100, 50 + len(auth_matches) * 25)

        # 5. UPI / Payment Scams
        upi_matches = [p for p in self.upi_patterns if re.search(p, text_lower)]
        if upi_matches:
            reasons.append("UPI manipulation detected (PIN entry or QR scan requested to 'receive' money).")
            heuristic_score += 35
            vec_financial = max(vec_financial, 75)
            vec_credential = max(vec_credential, 60)

        # 6. Electricity Bill Disconnection Scams
        elec_matches = [p for p in self.electricity_patterns if re.search(p, text_lower)]
        if elec_matches:
            reasons.append("Electricity bill disconnection scare tactic detected (utility scam vector).")
            heuristic_score += 45
            vec_authority = max(vec_authority, 80)
            vec_urgency = max(vec_urgency, 70)

        # 7. Links / Suspicious URLs
        urls = self.inspect_urls(text)
        if urls:
            high_risk_urls = [u for u in urls if u["risk_badge"] == "High Risk"]
            if high_risk_urls:
                reasons.append(f"High-risk disguised URL identified ({high_risk_urls[0]['url']}).")
                heuristic_score += 30
            else:
                reasons.append("Embedded hyperlink or external redirect target identified.")
                heuristic_score += 15

        # 8. ALL-CAPS shout / aggressive punctuation
        caps_words = [w for w in text.split() if w.isupper() and len(w) > 2]
        if len(caps_words) >= 3 or "!!!" in text or "???" in text:
            reasons.append("Aggressive coercive formatting (excessive uppercase or exclamation points).")
            heuristic_score += 10
            vec_urgency = max(vec_urgency, 40)

        heuristic_score = min(heuristic_score, 100)
        
        vectors = {
            "urgency": int(vec_urgency),
            "financial": int(vec_financial),
            "credential": int(vec_credential),
            "authority": int(vec_authority)
        }
        return reasons, heuristic_score, vectors

    def classify_attack_vector(self, text, vectors, ml_prob):
        """
        Classifies the exact attack category and generates recommended safety actions.
        """
        t_low = text.lower()

        # Check for Benign
        if (ml_prob is not None and ml_prob < 0.25) and sum(vectors.values()) < 30:
            return {
                "name": "Benign Interpersonal Message",
                "badge": "Safe Message",
                "icon": "shield-check",
                "color": "#06B6D4",
                "summary": "Standard safe communication showing authentic conversational flow without deceptive coercion or credential harvesting markers.",
                "actions": [
                    "No immediate defensive action required.",
                    "Exercise standard general digital mindfulness."
                ]
            }

        # 1. Electricity Bill Scam
        if any(w in t_low for w in ["electricity", "power", "discom", "bijli"]) and ("disconnect" in t_low or "tonight" in t_low or "bill" in t_low):
            return {
                "name": "Electricity Bill Disconnection Fraud",
                "badge": "Utility Scam",
                "icon": "alert",
                "color": "#EF4444",
                "summary": "Criminals threaten immediate electricity cutoff tonight claiming unpaid bills, prompting victims to call fake helpline numbers and install remote-access apps.",
                "actions": [
                    "NEVER call phone numbers provided inside SMS alerts.",
                    "Official power boards never disconnect service at night without formal written physical notice.",
                    "Check your real electricity account status via your official state utility app or electricity board website."
                ]
            }

        # 2. Bank & KYC / PAN / Aadhaar Scam
        if any(w in t_low for w in ["kyc", "pan", "aadhaar", "deactivated", "blocked", "suspended"]) and any(b in t_low for b in ["sbi", "hdfc", "icici", "axis", "bank", "account", "debit"]):
            return {
                "name": "Bank & KYC / PAN / Aadhaar Impersonation",
                "badge": "Banking Smishing",
                "icon": "lock",
                "color": "#EF4444",
                "summary": "Spoofs prominent financial institutions (SBI, HDFC, ICICI, etc.) with urgent threats of account deactivation unless KYC/PAN/Aadhaar is immediately updated through a phishing link.",
                "actions": [
                    "Never click external links received via SMS claiming to be your bank.",
                    "Banks NEVER request KYC updates, PAN linking, or passwords through SMS links.",
                    "Login only through your official bank mobile app or verified banking portal."
                ]
            }

        # 3. UPI / QR Code / Payment Scam
        if any(w in t_low for w in ["upi pin", "gpay", "phonepe", "paytm", "scan qr", "collect request"]) or ("receive" in t_low and "pin" in t_low):
            return {
                "name": "UPI & QR Code Reverse Payment Trap",
                "badge": "Payment Fraud",
                "icon": "activity",
                "color": "#EF4444",
                "summary": "Attempts to trick the victim into entering their secret UPI PIN or scanning a merchant QR code under the guise of 'receiving' money or cashback.",
                "actions": [
                    "GOLDEN RULE: You NEVER enter your UPI PIN to RECEIVE money.",
                    "Entering your UPI PIN ALWAYS transfers money OUT of your account.",
                    "Decline any unknown collect requests in Google Pay, PhonePe, or Paytm."
                ]
            }

        # 4. Courier & Parcel Scam
        if any(w in t_low for w in ["customs", "parcel", "delivery", "courier", "shipment", "fedex", "dhl", "usps", "india post", "street number"]):
            return {
                "name": "Courier & Package Delivery Smishing",
                "badge": "Logistics Phish",
                "icon": "message",
                "color": "#F59E0B",
                "summary": "Claims an incoming package is detained at customs or cannot be delivered due to missing address details or a tiny unpaid fee ($1.50 / ₹25), stealing card details at checkout.",
                "actions": [
                    "Do not click the tracking link in the SMS.",
                    "Track packages only on official carrier websites using your original merchant tracking number.",
                    "Never pay small 'redelivery fees' on unfamiliar domains."
                ]
            }

        # 5. Cashback, Lottery & Prize Scam
        if vectors["financial"] >= 45 or any(w in t_low for w in ["winner", "prize", "cashback", "lottery", "kbc", "gift card", "reward"]):
            return {
                "name": "Advance-Fee & Lottery Reward Lure",
                "badge": "Prize Scam",
                "icon": "sparkles",
                "color": "#F59E0B",
                "summary": "Fabricates claims of massive cash prizes, KBC lottery wins, or shopping gift cards to induce the target into paying advance processing fees or divulging banking credentials.",
                "actions": [
                    "You cannot win a lottery or prize contest you never entered.",
                    "Never pay advance processing charges, GST, or fees to claim any prize.",
                    "Block the sender and report the message to national cybercrime authorities."
                ]
            }

        # 6. Urgent Psychological Panic Trap
        if vectors["urgency"] >= 50:
            return {
                "name": "Coercive Psychological Urgency Attack",
                "badge": "Cognitive Exploit",
                "icon": "alert",
                "color": "#EF4444",
                "summary": "Manufactures false emergency deadlines ('within 2 hours', 'final warning') to bypass logical skepticism and trigger hasty compliance.",
                "actions": [
                    "Pause and take a breath: Scammers intentionally fabricate high urgency to prevent you from thinking clearly.",
                    "Verify the claim independently through a trusted family member, colleague, or official institution phone number."
                ]
            }

        # General Phishing
        return {
            "name": "Suspicious Social Engineering Phishing",
            "badge": "Phishing Attempt",
            "icon": "alert",
            "color": "#EF4444",
            "summary": "Exhibits distinct statistical, linguistic, and structural hallmarks of phishing campaigns designed to compromise accounts or install malware.",
            "actions": [
                "Do not open embedded hyperlinks or download attachments.",
                "Verify the sender's identity through out-of-band communication.",
                "Forward suspicious SMS messages to your carrier's scam reporting number (e.g. 1909 in India)."
            ]
        }

    def generate_token_heatmap(self, text):
        """
        Splits text into tokens and assigns a threat tag for UI highlighting:
        - 'urgency': Red
        - 'financial': Amber
        - 'credential': Cyan
        - 'link': Bright Cyan
        - 'normal': Default text
        """
        words = text.split()
        annotated_tokens = []
        
        for w in words:
            clean_w = re.sub(r"[^\w]", "", w).lower()
            tag = "normal"
            
            if any(re.search(p, w, re.IGNORECASE) for p in self.url_patterns):
                tag = "link"
            elif any(re.search(p, clean_w) for p in [r"\b(otp|pin|cvv|kyc|pan|password|bank|account|card|login|aadhaar)\b"]):
                tag = "credential"
            elif any(re.search(p, clean_w) for p in [r"\b(urgent|urgently|immediately|suspended|locked|deactivated|expire|now|today|alert|disconnected)\b"]):
                tag = "urgency"
            elif any(re.search(p, clean_w) for p in [r"\b(prize|won|winner|cash|lottery|reward|gift|free|dollars?|pay|fee|payment|cashback|bill)\b"]) or any(c in w for c in "$£€₹"):
                tag = "financial"
                
            annotated_tokens.append((w, tag))
        return annotated_tokens

    def predict(self, text):
        """
        Performs hybrid classification of an input text message.
        Returns a rich diagnostics dictionary.
        """
        if not text or not str(text).strip():
            return {
                "risk_score": 0,
                "status": "Safe",
                "color": "cyan",
                "ml_probability": 0.0,
                "reasons": ["No message text was provided. Enter a message to begin analysis."],
                "vectors": {"urgency": 0, "financial": 0, "credential": 0, "authority": 0},
                "attack_vector": {
                    "name": "Ready for Analysis",
                    "badge": "Standby",
                    "icon": "shield-check",
                    "color": "#06B6D4",
                    "summary": "Paste any SMS, WhatsApp alert, or email above to initiate deep threat inspection.",
                    "actions": ["Enter or paste a message into the text area above."]
                },
                "urls": [],
                "tokens": [],
                "error": "empty_input"
            }

        cleaned_text = str(text).strip()
        reasons, heuristic_score, vectors = self.analyze_heuristics(cleaned_text)
        urls_inspected = self.inspect_urls(cleaned_text)
        tokens_heatmap = self.generate_token_heatmap(cleaned_text)

        # Evaluate ML model if loaded
        if self.is_model_ready():
            try:
                tfidf_vec = self.vectorizer.transform([cleaned_text])
                probabilities = self.model.predict_proba(tfidf_vec)[0]
                ml_prob_scam = float(probabilities[1])
                ml_score = ml_prob_scam * 100.0

                if ml_prob_scam >= 0.70:
                    reasons.insert(0, f"ML statistical model detected known scam patterns ({ml_prob_scam * 100:.1f}% confidence).")
                elif ml_prob_scam >= 0.35:
                    reasons.insert(0, f"ML model detected moderate statistical scam markers ({ml_prob_scam * 100:.1f}% confidence).")
                else:
                    if not reasons:
                        reasons.append("ML model identified natural conversational patterns consistent with authentic messaging.")
            except Exception as e:
                ml_prob_scam = 0.0
                ml_score = 0.0
                reasons.append(f"Model prediction notice: {e}")
        else:
            ml_prob_scam = None
            ml_score = heuristic_score
            reasons.insert(
                0,
                "Heuristic rule-based security engine active with Indian banking & scam rules."
            )

        # Hybrid Score Calculation
        if ml_prob_scam is not None:
            combined_score = (0.60 * ml_score) + (0.40 * heuristic_score)
            if heuristic_score >= 60 and ml_score < 30:
                # Strong heuristic indicators override standard Naive Bayes (which was trained on English spam corpus that lacks Indian SMS scam formats)
                combined_score = max(combined_score, heuristic_score * 0.85)
            if ml_score > 60 and heuristic_score > 40:
                combined_score = max(combined_score, 85)
        else:
            combined_score = float(heuristic_score)

        risk_score = int(round(max(0, min(100, combined_score))))

        # Determine status
        if risk_score >= 70:
            status = "Dangerous"
            color = "red"
        elif risk_score >= 35:
            status = "Suspicious"
            color = "orange"
        else:
            status = "Safe"
            color = "cyan"

        attack_info = self.classify_attack_vector(cleaned_text, vectors, ml_prob_scam)

        return {
            "risk_score": risk_score,
            "status": status,
            "color": color,
            "ml_probability": round(ml_prob_scam, 4) if ml_prob_scam is not None else None,
            "reasons": reasons,
            "vectors": vectors,
            "attack_vector": attack_info,
            "urls": urls_inspected,
            "tokens": tokens_heatmap,
            "error": None
        }


class DeepUrlScanner:
    """
    Dedicated Phishing URL & Domain Security Diagnostics Engine.
    Inspects URL structure, domain characteristics, TLD risk profiles,
    protocol security, and brand impersonation vectors.
    """

    KNOWN_BRANDS = [
        "sbi", "hdfc", "icici", "axis", "kotak", "pnb", "bob", "paytm",
        "phonepe", "gpay", "google", "paypal", "apple", "amazon", "netflix",
        "microsoft", "facebook", "instagram", "whatsapp", "fedex", "dhl", "usps"
    ]

    RISKY_TLDS = {
        "xyz": 35, "top": 40, "work": 35, "click": 40, "tk": 45, "ml": 45,
        "ga": 45, "cf": 45, "gq": 45, "link": 30, "buzz": 35, "club": 25,
        "cc": 30, "online": 25, "site": 25, "shop": 25, "cam": 40, "fit": 35
    }

    SHORTENERS = [
        "bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "ow.ly",
        "shorturl.at", "rebrand.ly", "rb.gy"
    ]

    def scan_url(self, raw_url: str):
        if not raw_url or not str(raw_url).strip():
            return {
                "url": "",
                "risk_score": 0,
                "status": "Safe",
                "color": "#06B6D4",
                "protocol": "N/A",
                "domain": "N/A",
                "tld": "N/A",
                "is_ip": False,
                "is_shortener": False,
                "brand_spoofed": None,
                "risk_factors": ["No URL provided for analysis."],
                "recommendations": ["Enter a URL to initiate deep security inspection."]
            }

        url = str(raw_url).strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        try:
            parsed = urllib.parse.urlparse(url)
            netloc = parsed.netloc.lower()
            path = parsed.path.lower()
        except Exception:
            netloc = url.lower()
            path = ""

        domain_parts = netloc.split(":")
        host = domain_parts[0]

        risk_score = 0
        risk_factors = []
        recommendations = []

        # 1. Protocol check
        is_http = parsed.scheme == "http"
        if is_http:
            risk_score += 25
            risk_factors.append("Insecure Protocol: Plain HTTP detected (no TLS encryption). Credentials can be intercepted.")
            recommendations.append("Never enter login credentials or personal information on non-HTTPS sites.")

        # 2. Raw IP address check
        is_ip = bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host))
        if is_ip:
            risk_score += 45
            risk_factors.append("Raw IPv4 Host: The link points directly to a server IP rather than a registered domain name.")
            recommendations.append("Legitimate institutions use registered domain names. Avoid opening raw IP addresses.")

        # 3. URL Shortener check
        is_shortener = any(host == s or host.endswith("." + s) for s in self.SHORTENERS)
        if is_shortener:
            risk_score += 35
            risk_factors.append("URL Shortener Detected: The real destination is intentionally masked behind an obfuscated redirect.")
            recommendations.append("Do not open shortened links from SMS or untrusted chats without expanding them first.")

        # 4. Risky TLD check
        tld = host.split(".")[-1] if "." in host else ""
        if tld in self.RISKY_TLDS:
            penalty = self.RISKY_TLDS[tld]
            risk_score += penalty
            risk_factors.append(f"Suspicious TLD: Top-level domain (.{tld}) is frequently leveraged by threat actors for zero-cost throwaway domains.")

        # 5. Brand Impersonation / Typosquatting in subdomain or domain
        brand_spoofed = None
        for brand in self.KNOWN_BRANDS:
            if brand in host:
                # Check if it's the legitimate domain (e.g. sbi.co.in or hdfcbank.com)
                legit_domains = [f"{brand}.com", f"{brand}.co.in", f"{brand}.org", f"{brand}bank.com"]
                if not any(host == ld or host.endswith("." + ld) for ld in legit_domains):
                    brand_spoofed = brand.upper()
                    risk_score += 40
                    risk_factors.append(f"Brand Impersonation Vector: Contains '{brand.upper()}' brand keyword inside an unverified domain name ({host}).")
                    recommendations.append(f"Verify this is an official {brand.upper()} portal. Official institutions never host services on third-party domains.")
                    break

        # 6. Sensitive credential path keywords
        sensitive_paths = ["login", "signin", "verify", "kyc", "update", "banking", "account", "secure", "otp", "password"]
        matched_paths = [p for p in sensitive_paths if p in path]
        if matched_paths:
            risk_score += 20
            risk_factors.append(f"Credential Harvesting Target: Path references sensitive operational endpoints: {', '.join(matched_paths)}.")

        # 7. Domain character anomalies (hyphens, excess subdomains)
        if host.count("-") >= 2:
            risk_score += 15
            risk_factors.append("Suspicious Hyphenation: Multiple hyphens detected, typical of phishing domain generation algorithms (DGA).")
        if host.count(".") >= 4:
            risk_score += 15
            risk_factors.append("Excessive Subdomains: Unusually deep subdomain structure used to obscure the true domain suffix.")

        risk_score = min(100, max(0, risk_score))

        if risk_score >= 65:
            status = "Dangerous"
            color = "#EF4444"
        elif risk_score >= 30:
            status = "Suspicious"
            color = "#F59E0B"
        else:
            status = "Safe"
            color = "#06B6D4"

        if not risk_factors:
            risk_factors.append("Standard domain structure observed with valid HTTPS encryption and standard TLD.")
        if not recommendations:
            recommendations.append("Domain appears structurally benign. Practice regular web navigation precautions.")

        return {
            "url": raw_url,
            "risk_score": risk_score,
            "status": status,
            "color": color,
            "protocol": parsed.scheme.upper(),
            "domain": host,
            "tld": f".{tld}" if tld else "N/A",
            "is_ip": is_ip,
            "is_shortener": is_shortener,
            "brand_spoofed": brand_spoofed,
            "risk_factors": risk_factors,
            "recommendations": recommendations
        }


class SecurityAssistant:
    """
    Intelligent Cybersecurity Knowledge & Defense Assistant.
    Provides verified, explainable guidance on social engineering,
    banking scams, KYC fraud, UPI traps, and deepfake incident response.
    """

    RESPONSES = {
        "sbi": (
            "🏦 **SBI / Banking KYC Alert Protocol:**\n\n"
            "• **Is the SMS real?** State Bank of India and other major banks **never** send SMS messages threatening deactivation within 24 hours with a link to update PAN or KYC.\n"
            "• **Sender Header:** Legitimate bank SMS alerts arrive from verified sender IDs like `VK-SBIINB`, `AD-HDFCBK`, or `JM-ICICIB`, **never** from standard 10-digit mobile numbers.\n"
            "• **Action Plan:** Never click the link. If you already submitted your password or OTP, immediately call the national cyber helpline **1930** and block your debit card via the official YONO / NetBanking app."
        ),
        "electricity": (
            "⚡ **Electricity Bill Disconnection Scam Guide:**\n\n"
            "• **How it works:** Attackers broadcast bulk SMS alerts claiming: *'Your power will be disconnected tonight at 9:30 PM due to unpaid bills. Call electricity officer at 98xxxxxx.'*\n"
            "• **The Trap:** When victims call, scammers instruct them to download a remote-access app (like AnyDesk, TeamViewer, or RustDesk) to pay a token ₹10 fee, which allows attackers to take over the phone and steal bank balances.\n"
            "• **Golden Rule:** Utility boards **never** disconnect electricity at night without multiple prior written physical notices. Never call numbers provided in SMS."
        ),
        "upi": (
            "📱 **UPI & QR Code Scam Defense:**\n\n"
            "• **The Golden Rule of UPI:** You **NEVER** need to enter your UPI PIN or scan a QR code to **RECEIVE** money. Entering your PIN **ALWAYS** debits funds from your account.\n"
            "• **Common Tactics:** Scammers on OLX or Facebook Marketplace claim they are sending an advance deposit and ask you to 'approve collect request' or 'scan QR' to receive cash.\n"
            "• **Action Plan:** Decline and report the collect request in your UPI app (Google Pay, PhonePe, Paytm). Never share screen during UPI transactions."
        ),
        "deepfake": (
            "🎭 **Deepfake Video & Audio Defense:**\n\n"
            "• **The Arup Incident ($25M Fraud):** In 2024, an employee was tricked into transferring $25M after a video conference where the CFO and all colleagues were AI-generated deepfakes.\n"
            "• **Real-Time Spotting Tips:**\n"
            "  1. *Turn sideways test:* Ask the caller to turn their face completely sideways (90 degrees). Generative models struggle with facial boundary profiles.\n"
            "  2. *Hand-wave test:* Ask them to slowly pass their hand across their face in front of the camera. Face-swap models fail and distort the hand edges.\n"
            "  3. *Out-of-band verification:* Always verify high-value requests via a separate known phone channel or pre-agreed secret passphrase."
        ),
        "otp": (
            "🔐 **Emergency Steps If You Shared an OTP or Password:**\n\n"
            "1. **Immediately Freeze Your Accounts:** Call your bank's 24x7 emergency helpline or use the mobile app to disable NetBanking and freeze debit/credit cards.\n"
            "2. **Call 1930 Immediately:** In India, call the **1930 Cyber Fraud Helpline** immediately. The first 2 hours are the 'Golden Hours' where stolen funds can be frozen in transit by the Indian Cyber Crime Coordination Centre (I4C).\n"
            "3. **File a Formal Complaint:** Register an incident on **cybercrime.gov.in** with screenshots and transaction reference numbers (UTR)."
        ),
        "courier": (
            "📦 **Courier & Delivery Smishing Defense:**\n\n"
            "• **The Tactic:** Scammers send SMS claiming an India Post, FedEx, or DHL package is stuck at customs due to a missing street address or an unpaid ₹25 / $1.50 customs fee.\n"
            "• **The Target:** The fake payment page steals full credit/debit card details (number, expiry, CVV) and immediately attempts large unauthorized transactions.\n"
            "• **Action Plan:** Track packages exclusively on the seller's official portal using your existing order history. Never pay small fees via unsolicited SMS links."
        )
    }

    def ask(self, user_query: str) -> str:
        q = str(user_query).lower()

        if any(w in q for w in ["sbi", "hdfc", "icici", "bank", "pan", "kyc", "aadhaar", "account locked"]):
            return self.RESPONSES["sbi"]
        elif any(w in q for w in ["electricity", "power", "bijli", "bill", "discom", "tonight"]):
            return self.RESPONSES["electricity"]
        elif any(w in q for w in ["upi", "qr", "gpay", "phonepe", "paytm", "receive money", "collect"]):
            return self.RESPONSES["upi"]
        elif any(w in q for w in ["deepfake", "video call", "voice clone", "face swap", "arup", "synthetic"]):
            return self.RESPONSES["deepfake"]
        elif any(w in q for w in ["shared otp", "give otp", "lost money", "scammed", "freeze", "compromised", "1930"]):
            return self.RESPONSES["otp"]
        elif any(w in q for w in ["courier", "parcel", "delivery", "customs", "fedex", "dhl", "india post"]):
            return self.RESPONSES["courier"]
        else:
            return (
                "🛡️ **DEEPFAKE DEFENSE Security Advisory:**\n\n"
                "I am your AI cybersecurity defense assistant. I can help evaluate:\n"
                "• **Banking & KYC fraud** (SBI, HDFC, ICICI, PAN/Aadhaar updates)\n"
                "• **Electricity bill & utility disconnection scams**\n"
                "• **UPI collect requests & QR code traps**\n"
                "• **Synthetic deepfakes in video calls** (the $25M Arup case & defense checks)\n"
                "• **Courier & customs duty delivery lures**\n"
                "• **Emergency incident steps** if credentials or OTPs were compromised.\n\n"
                "Try asking: *'Is this SBI KYC SMS real?'*, *'How do electricity bill scams work?'*, or *'What is the hand-wave test for deepfake video calls?'*"
            )

