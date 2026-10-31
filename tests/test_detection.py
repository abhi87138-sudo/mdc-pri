"""
test_detection.py
Unit and validation test suite for ThreatDetector.
Runs 3 scam messages and 3 normal messages, printing predictions,
risk scores, and rule triggers.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.predict import ThreatDetector

def run_tests():
    detector = ThreatDetector()
    print("============================================================")
    print(" AI-Driven Social Engineering Platform - Test Suite")
    print("============================================================")

    scam_messages = [
        "URGENT: Your bank account is locked! Click http://bit.ly/bank-verify to update OTP immediately.",
        "WINNER!! As a valued customer you have been selected to receive a £900 cash prize reward! Call 09061701461 to claim your reward. Claim code KL341. Valid 12 hours only.",
        "Your package delivery is held at terminal due to unpaid duty. Pay $2.99 fee immediately at https://parcel-track-update.xyz to avoid parcel return."
    ]

    normal_messages = [
        "Hey Alex, are we still meeting in the college library at 4 PM to work on the computer science assignment?",
        "Mom, I finished my classes for today and I'm heading home on the metro. See you soon!",
        "Can you please email me the lecture notes from today's Operating Systems class when you get a chance? Thanks!"
    ]

    print("\n--- [TEST 1] EVALUATING 3 SCAM / PHISHING MESSAGES ---")
    for i, msg in enumerate(scam_messages, 1):
        res = detector.predict(msg)
        print(f"\n[Scam Test #{i}]")
        print(f"Message   : \"{msg}\"")
        print(f"Verdict   : {res['status'].upper()} (Color: {res['color']})")
        print(f"Risk Score: {res['risk_score']} / 100")
        print(f"ML Prob   : {res['ml_probability'] * 100:.2f}%" if res['ml_probability'] is not None else "ML Prob   : N/A")
        print("Reasons:")
        for r in res['reasons']:
            print(f"  * {r}")

    print("\n--- [TEST 2] EVALUATING 3 NORMAL / LEGITIMATE MESSAGES ---")
    for i, msg in enumerate(normal_messages, 1):
        res = detector.predict(msg)
        print(f"\n[Normal Test #{i}]")
        print(f"Message   : \"{msg}\"")
        print(f"Verdict   : {res['status'].upper()} (Color: {res['color']})")
        print(f"Risk Score: {res['risk_score']} / 100")
        print(f"ML Prob   : {res['ml_probability'] * 100:.2f}%" if res['ml_probability'] is not None else "ML Prob   : N/A")
        print("Reasons:")
        for r in res['reasons']:
            print(f"  * {r}")
    print("\n============================================================")

if __name__ == "__main__":
    run_tests()
