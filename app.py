"""
app.py
──────
Flask application entry point for the Smart Home Energy Advisor.
Serves the frontend dashboard and exposes a /predict API endpoint
that calls the IBM Watsonx.ai AutoAI-deployed model.
"""

import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from agent_config import (
    WATSONX_API_KEY,
    WATSONX_URL,
    WATSONX_PROJECT_ID,
    AUTOAI_DEPLOYMENT_ID,
    AUTOAI_SPACE_ID,
    DEFAULT_TARIFF,
    build_recommendation_prompt,
    WATSONX_MODEL_ID,
    WATSONX_PARAMS,
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")


# ── Helper: get IBM IAM token ─────────────────────────────────
def get_iam_token(api_key: str) -> str:
    """Exchange an IBM Cloud API key for a short-lived IAM bearer token."""
    resp = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={
            "apikey": api_key,
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


# ── Helper: call AutoAI deployed model ───────────────────────
def call_autoai_model(features: dict) -> float:
    """
    Send input features to the AutoAI deployment endpoint
    and return the predicted energy usage (kWh).
    Falls back to a local heuristic when credentials are not set.
    """
    if not AUTOAI_DEPLOYMENT_ID or not WATSONX_API_KEY:
        return _local_heuristic(features)

    try:
        token = get_iam_token(WATSONX_API_KEY)
        url = (
            f"{WATSONX_URL}/ml/v4/deployments/"
            f"{AUTOAI_DEPLOYMENT_ID}/predictions?version=2021-05-01"
        )
        payload = {
            "input_data": [
                {
                    "fields": [
                        "current_usage", "temperature", "humidity",
                        "tariff", "hour", "ac_status"
                    ],
                    "values": [[
                        features["usage"],
                        features["temperature"],
                        features["humidity"],
                        features["tariff"],
                        features["hour"],
                        features["ac_status"],
                    ]],
                }
            ]
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=20)
        resp.raise_for_status()
        result = resp.json()
        predicted = result["predictions"][0]["values"][0][0]
        return round(float(predicted), 2)

    except Exception:
        # Graceful fallback to heuristic if API unavailable
        return _local_heuristic(features)


def _local_heuristic(f: dict) -> float:
    """Simple rule-based fallback prediction (used when model is unavailable)."""
    base   = float(f.get("usage", 8))
    temp_f = 1 + (float(f.get("temperature", 30)) - 30) * 0.03 if float(f.get("temperature", 30)) > 30 else 1
    hum_f  = 1.06 if float(f.get("humidity", 60)) > 70 else 1
    hour   = int(f.get("hour", 12))
    peak_f = 1.15 if 18 <= hour <= 22 else (1.10 if 6 <= hour <= 9 else 1)
    ac_f   = 1.20 if int(f.get("ac_status", 0)) == 1 else 1
    return round(base * temp_f * hum_f * peak_f * ac_f, 2)


# ── Helper: get LLM recommendation ──────────────────────────
def get_ai_recommendation(prompt: str) -> list[str]:
    """
    Call Watsonx.ai text generation endpoint and parse bullet points.
    Falls back to rule-based recommendations if unavailable.
    """
    if not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
        return _rule_based_recommendation(prompt)

    try:
        token = get_iam_token(WATSONX_API_KEY)
        url = f"{WATSONX_URL}/ml/v1/text/generation?version=2023-05-29"
        payload = {
            "model_id": WATSONX_MODEL_ID,
            "input": prompt,
            "parameters": WATSONX_PARAMS,
            "project_id": WATSONX_PROJECT_ID,
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=20)
        resp.raise_for_status()
        text = resp.json()["results"][0]["generated_text"].strip()
        lines = [l.lstrip("•-123. ").strip() for l in text.split("\n") if l.strip()]
        return [l for l in lines if len(l) > 10][:3]

    except Exception:
        return _rule_based_recommendation(prompt)


def _rule_based_recommendation(prompt: str) -> list[str]:
    """Fallback recommendations based on keywords in the prompt."""
    if "High" in prompt or "13" in prompt or "14" in prompt:
        return [
            "High usage expected — avoid heavy appliances until after 9 PM.",
            "Turn off AC in unoccupied rooms to reduce load.",
            "Consider switching remaining bulbs to LED lighting.",
        ]
    elif "Moderate" in prompt or "10" in prompt or "11" in prompt:
        return [
            "Moderate usage — you are within a normal range.",
            "Keep AC at 24°C and unplug standby devices.",
            "Shift dishwasher use to off-peak hours (after 10 PM).",
        ]
    else:
        return [
            "Low energy usage today — excellent efficiency!",
            "Keep unused lights and chargers unplugged.",
            "Your current habits could save ₹200+ this month.",
        ]


# ── Routes ───────────────────────────────────────────────────

@app.route("/")
def index():
    """Render the main dashboard."""
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """
    Accepts JSON with energy input features.
    Returns predicted kWh, estimated cost, and AI recommendations.

    Request body:
    {
        "usage": 8.42,
        "temperature": 32,
        "humidity": 65,
        "tariff": 6.50,
        "hour": 14,
        "ac_status": 1
    }
    """
    data = request.get_json(force=True)

    required = ["usage", "temperature", "humidity", "tariff", "hour", "ac_status"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    predicted_kwh = call_autoai_model(data)
    estimated_cost = round(predicted_kwh * float(data["tariff"]), 2)

    prompt = build_recommendation_prompt(
        usage=data["usage"],
        temperature=data["temperature"],
        humidity=data["humidity"],
        hour=data["hour"],
        ac_status=data["ac_status"],
        predicted=predicted_kwh,
        tariff=data["tariff"],
    )
    recommendations = get_ai_recommendation(prompt)

    return jsonify({
        "predicted_kwh": predicted_kwh,
        "estimated_cost": estimated_cost,
        "currency": "INR",
        "tariff": data["tariff"],
        "recommendations": recommendations,
    })


@app.route("/health")
def health():
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "service": "Smart Home Energy Advisor"})


# ── Entry point ──────────────────────────────────────────────
if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=debug)
