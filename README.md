# 🤖 Agentic Car Search Engine

> **Built by [Ran Eliahu](https://github.com/Eliahur7) via [Google AntiGravity](https://deepmind.google/) — 🚧 Work in Progress**

An AI-powered car search assistant that lets you describe what you want in plain English and instantly finds, evaluates, and compares vehicles across multiple listing platforms — all within a sleek conversational chat interface.

---

## ✨ How It Works

Unlike traditional car search platforms where you manually set filters, this app uses an **AI agent** to understand your intent and translate it into search criteria automatically.

### 1. 🧠 Natural Language Understanding
Type anything — the agent interprets it:
> *"Looking for a sporty car with a luxury interior, preferably under 20,000 miles"*

The AI agent extracts structured parameters from your prompt:
- **Body style** → Sports Car
- **Features** → Leather interior
- **Mileage cap** → 20,000 miles

It also understands synonyms: `"sporty"` → Sports Car, `"luxury"` → Leather interior, `"all wheel drive"` → AWD, etc.

### 2. 🔄 Conversational Follow-Ups
The agent **remembers your previous search context**, so you can refine results naturally:
> 💬 *"Looking for a sporty car with a luxury interior"*
> 💬 *"Actually, make the budget under $80k"*

The second message updates only the budget — your body style and features carry over automatically.

### 3. 🔍 Multi-Source Inventory Search
The agent scans simulated listings from:
- **CarGurus** — value-focused listings with market analysis
- **Autotrader** — broad national inventory
- **Cars.com** — regional dealer listings
- **Dealer Direct** — local dealership inventory
- **Manufacturer CPO** — factory-certified pre-owned vehicles

### 4. 📊 Intelligent Deal Evaluation
Every result is automatically tagged:
- 🔥 **Great Deal** — priced significantly below market value
- 🟢 **Fair Price** — priced around market value
- ⚠️ **Overpriced** — priced above market value

### 5. 💰 5-Year Total Cost of Ownership
Each vehicle comes with a breakdown of estimated ownership costs:
- Depreciation
- Maintenance & Repairs
- Fuel / Energy
- Insurance

### 6. 🔗 Direct Source Links
Every result card links directly to the source platform, filtered by year, make, model, price, and mileage — so one click takes you to the exact search results on CarGurus, Autotrader, or Cars.com.

### 7. ❤️ Save to Favorites
Click **Save** on any car to pin it to your sidebar for easy reference throughout your session.

### 8. 📋 Dealer Negotiation Agent
Each listing includes auto-generated, high-leverage questions tailored to the specific vehicle to ask the dealer before visiting.

---

## 🚀 Local Setup

### Prerequisites
- Python 3.8+
- pip
- Git

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/Eliahur7/agentic-car-search.git
cd agentic-car-search
```

**2. Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. (Optional) Enable the AI Agent**

By default, the app uses a smart rule-based parser. To enable the full Claude LLM agent for more nuanced natural language understanding:

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key:
# ANTHROPIC_API_KEY=sk-ant-...
```

Get an API key at [console.anthropic.com](https://console.anthropic.com)

**5. Run the app**
```bash
streamlit run app.py
```

The app will open automatically at [http://localhost:8501](http://localhost:8501)

---

## 🏗️ Project Structure

```
agentic-car-search/
├── app.py                  # Main Streamlit app — chat UI, session state, rendering
├── requirements.txt        # Python dependencies
├── .env                    # Your API keys (not committed)
└── src/
    ├── database.py         # Simulated multi-source vehicle inventory + listing URL generator
    ├── ai_search.py        # Natural language parser — LLM agent + regex fallback
    ├── deal_evaluator.py   # Market value heuristics + deal rating engine
    ├── cost_estimator.py   # 5-year total cost of ownership calculator
    └── dealer_advisor.py   # Dealer question generator + history summarizer
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI / Frontend | [Streamlit](https://streamlit.io) + Glassmorphism CSS |
| AI Agent | [Anthropic Claude](https://www.anthropic.com) (with regex fallback) |
| Data | Simulated inventory (pandas DataFrame) |
| Charts | [Plotly Express](https://plotly.com/python/plotly-express/) |
| Language | Python 3.8+ |

---

## 🚧 Roadmap (Coming Soon)

- [ ] Real-time scraping / API integration with CarGurus, Autotrader, Cars.com
- [ ] VIN-based vehicle history report summarization
- [ ] Price alert monitoring — notify when a match drops in price
- [ ] Saved sessions — persist favorites across browser sessions
- [ ] Mobile-responsive layout
- [ ] Comparison mode — side-by-side vehicle analysis
- [ ] AI-generated negotiation scripts

---

## 👤 Author

**Ran Eliahu** — Built via **Google AntiGravity**

> *"The future of car buying isn't more filters — it's a smarter agent."*

---

*🚧 This project is actively under development. Features, data sources, and UI are subject to change.*
