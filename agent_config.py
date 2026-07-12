"""
agent_config.py
───────────────
Configuration and initialisation for the IBM Watsonx.ai agent
and AutoAI-deployed energy prediction model.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Watsonx.ai credentials ────────────────────────────────────
WATSONX_API_KEY     = os.getenv("WATSONX_API_KEY", "")
WATSONX_PROJECT_ID  = os.getenv("WATSONX_PROJECT_ID", "")
WATSONX_URL         = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

# ── AutoAI deployment ─────────────────────────────────────────
AUTOAI_DEPLOYMENT_ID = os.getenv("AUTOAI_DEPLOYMENT_ID", "")
AUTOAI_SPACE_ID      = os.getenv("AUTOAI_SPACE_ID", "")

# ── App defaults ──────────────────────────────────────────────
DEFAULT_TARIFF = float(os.getenv("DEFAULT_TARIFF", 6.50))

# ── Watsonx.ai model settings ────────────────────────────────
WATSONX_MODEL_ID = "ibm/granite-13b-instruct-v2"   # LLM for recommendations
WATSONX_PARAMS = {
    "decoding_method": "greedy",
    "max_new_tokens": 300,
    "min_new_tokens": 30,
    "temperature": 0.7,
    "top_k": 50,
    "top_p": 1,
}

# ── Prompt template for AI recommendations ───────────────────
RECOMMENDATION_PROMPT_TEMPLATE = """You are a smart home energy advisor.
A user has the following energy usage data:
- Current Usage: {usage} kWh
- Temperature: {temperature}°C
- Humidity: {humidity}%
- Hour of Day: {hour}:00
- AC Status: {ac_status}
- Predicted Next Hour Usage: {predicted} kWh
- Electricity Tariff: ₹{tariff} per kWh

Provide 3 short, actionable energy-saving recommendations for this user.
Focus on cost savings and practical appliance scheduling.
Keep each recommendation to one sentence.
"""

def build_recommendation_prompt(usage, temperature, humidity, hour,
                                 ac_status, predicted, tariff):
    """Return a formatted prompt string for the Watsonx LLM."""
    return RECOMMENDATION_PROMPT_TEMPLATE.format(
        usage=usage,
        temperature=temperature,
        humidity=humidity,
        hour=hour,
        ac_status="On" if int(ac_status) == 1 else "Off",
        predicted=predicted,
        tariff=tariff,
    )
