import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, date
import streamlit as st
import json


def init_firebase():
    """Initialize Firebase Admin SDK using Streamlit secrets."""
    if not firebase_admin._apps:
        cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    return firestore.client()


def get_or_create_user(db, email: str) -> dict:
    """Get existing user or create a new one. Returns user data dict."""
    doc_ref = db.collection("equity_users").document(email)
    doc = doc_ref.get()

    if doc.exists:
        user_data = doc.to_dict()
        # Check if month needs resetting
        month_reset = user_data.get("month_reset", "")
        current_month = date.today().strftime("%Y-%m")
        if month_reset != current_month:
            doc_ref.update({
                "free_uses_this_month": 0,
                "month_reset": current_month,
            })
            user_data["free_uses_this_month"] = 0
            user_data["month_reset"] = current_month
        return user_data
    else:
        user_data = {
            "email": email,
            "free_uses_this_month": 0,
            "month_reset": date.today().strftime("%Y-%m"),
            "credits_remaining": 0,
            "created_at": datetime.utcnow().isoformat(),
        }
        doc_ref.set(user_data)
        return user_data


def check_can_analyze(db, email: str) -> dict:
    """
    Check if user can run an analysis.
    Returns: {"allowed": bool, "reason": str, "free_left": int, "credits": int}
    """
    user = get_or_create_user(db, email)
    free_used = user.get("free_uses_this_month", 0)
    credits = user.get("credits_remaining", 0)

    free_left = max(0, 3 - free_used)

    if free_left > 0:
        return {
            "allowed": True,
            "reason": "free",
            "free_left": free_left,
            "credits": credits,
        }
    elif credits > 0:
        return {
            "allowed": True,
            "reason": "credits",
            "free_left": 0,
            "credits": credits,
        }
    else:
        return {
            "allowed": False,
            "reason": "no_credits",
            "free_left": 0,
            "credits": 0,
        }


def use_one_report(db, email: str, reason: str):
    """Deduct one report usage — either from free tier or credits."""
    doc_ref = db.collection("equity_users").document(email)

    if reason == "free":
        doc_ref.update({
            "free_uses_this_month": firestore.Increment(1),
        })
    elif reason == "credits":
        doc_ref.update({
            "credits_remaining": firestore.Increment(-1),
        })


def add_credits(db, email: str, count: int):
    """Add purchased credits to user account."""
    user = get_or_create_user(db, email)
    doc_ref = db.collection("equity_users").document(email)
    doc_ref.update({
        "credits_remaining": firestore.Increment(count),
    })
    return user.get("credits_remaining", 0) + count