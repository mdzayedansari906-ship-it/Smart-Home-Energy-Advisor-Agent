# Smart Home Energy Advisor

> Monitor energy usage, predict future consumption, and receive AI-powered recommendations to reduce electricity costs — powered by **IBM Watsonx.ai** and **AutoAI**.

---
![Uploading image.png…]()

## Project Structure

```
Smart Home Energy Advisor Agent/
├── static/                  # CSS, JS, images (served by Flask)
├── templates/
│   └── index.html           # Main dashboard (Jinja2 template)
├── venv/                    # Python virtual environment (git-ignored)
├── .env                     # Secret credentials (git-ignored)
├── .env.example             # Template — copy to .env and fill values
├── agent_config.py          # Watsonx.ai config, prompt templates
├── app.py                   # Flask app + API routes
├── gitignore.txt            # Files excluded from version control
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## Features

| Feature | Description |
|---|---|
| 📊 Dashboard | Live summary cards — current usage, predicted usage, monthly bill, savings |
| ⚡ Energy Prediction | AutoAI-deployed model predicts next-hour kWh consumption |
| 🤖 AI Recommendations | IBM Watsonx.ai LLM generates personalised energy-saving tips |
| 📈 Usage Chart | 24-hour energy consumption line chart |
| 💡 Appliance Tips | Scheduling recommendations for washing machine, AC, standby devices |
| 🔒 No login required | Public-facing dashboard, no authentication needed |

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/smart-home-energy-advisor.git
cd "Smart Home Energy Advisor Agent"
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Open .env and fill in your IBM Watsonx.ai credentials
```

| Variable | Description |
|---|---|
| `WATSONX_API_KEY` | IBM Cloud API key |
| `WATSONX_PROJECT_ID` | Watsonx.ai project ID |
| `WATSONX_URL` | Regional endpoint (e.g. `https://us-south.ml.cloud.ibm.com`) |
| `AUTOAI_DEPLOYMENT_ID` | AutoAI deployment ID for the energy model |
| `AUTOAI_SPACE_ID` | Deployment space ID |
| `DEFAULT_TARIFF` | Default electricity rate in ₹/kWh |

> **Note:** The app works without credentials using a built-in heuristic fallback model.

### 5. Run the application

```bash
python app.py
```

Open your browser at **http://localhost:5000**

---

## API Reference

### `POST /predict`

Predict energy usage and get AI recommendations.

**Request body (JSON):**
```json
{
  "usage": 8.42,
  "temperature": 32,
  "humidity": 65,
  "tariff": 6.50,
  "hour": 14,
  "ac_status": 1
}
```

**Response:**
```json
{
  "predicted_kwh": 10.55,
  "estimated_cost": 68.57,
  "currency": "INR",
  "tariff": 6.50,
  "recommendations": [
    "High usage expected — avoid heavy appliances until after 9 PM.",
    "Turn off AC in unoccupied rooms to reduce load.",
    "Consider switching remaining bulbs to LED lighting."
  ]
}
```

### `GET /health`

Returns `{"status": "ok"}` — useful for uptime monitoring.

---

## Deployment

### Production with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment variables for production

```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<strong-random-string>
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3.0 |
| AI / ML | IBM Watsonx.ai, AutoAI |
| LLM | IBM Granite 13B Instruct |
| Frontend | HTML5, CSS3, Vanilla JS, SVG charts |
| Config | python-dotenv |
| Deploy | Gunicorn |

---

## License

MIT License — see `LICENSE` for details.

---

*Built with IBM Watsonx.ai and AutoAI*
