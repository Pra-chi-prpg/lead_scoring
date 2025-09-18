# Lead Scoring Backend – FastAPI + OpenAI

This project is a **FastAPI-based backend service** for **B2B lead scoring**.  
It allows you to:
- Upload an **offer** (value propositions & ideal use cases)
- Upload **leads** (CSV file)
- Automatically **score leads** using **rule-based logic + OpenAI AI scoring**
- View or **export scored leads** as CSV.

## Setup Steps
1️⃣ Clone Repository
git clone https://github.com/<your-username>/lead-scoring-backend.git
cd lead-scoring-backend

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Add Environment Variable

Create a file named .env (or set an environment variable) with:

OPENAI_API_KEY=your_openai_api_key_here


(Or directly replace openai.api_key in app.py with your key for quick testing)

5️⃣ Run FastAPI App
uvicorn app:app --reload


➡ The API will be live at:
https://lead-scoring-x2jt.onrender.com/

Interactive API docs:
https://lead-scoring-x2jt.onrender.com/docs

## API Usage Examples (cURL / Postman)
1️⃣ Upload Offer
curl -X POST "https://lead-scoring-x2jt.onrender.com/docs#/default/create_offer_offer_post" \
-H "Content-Type: application/json" \
-d '{
    "name": "AI CRM Suite",
    "value_props": ["Automates lead management", "Improves conversion rates"],
    "ideal_use_cases": ["SaaS", "E-commerce", "Marketing Agencies"]
}'


#### Response

{
  "status": "Offer saved",
  "offer": {
    "name": "AI CRM Suite",
    "value_props": [...],
    "ideal_use_cases": [...]
  }
}

2️⃣ Upload Leads CSV

Prepare a CSV file (leads.csv) with headers:

name,role,company,industry,location,linkedin_bio


Example:

John Doe,CEO,TechCorp,SaaS,New York,Experienced founder with 10 years in SaaS.
Jane Smith,Manager,ShopEasy,E-commerce,California,Marketing specialist with 5 years experience.


Upload:

curl -X POST "https://lead-scoring-x2jt.onrender.com/docs#/default/upload_leads_leads_upload_post" \
-F "file=@leads.csv"


#### Response

{"status": "Leads uploaded", "total": 2}

3️⃣ Score Leads
curl -X POST "https://lead-scoring-x2jt.onrender.com/docs#/default/score_leads_score_post"


Response

{
  "status": "Leads scored",
  "total": 2
}

4️⃣ View Results
curl "https://lead-scoring-x2jt.onrender.com/docs#/default/get_results_results_get"


Response Example

[
  {
    "name": "John Doe",
    "role": "CEO",
    "company": "TechCorp",
    "intent": "High",
    "score": 80,
    "reasoning": "High buying intent because SaaS company needs CRM automation."
  },
  ...
]

5️⃣ Export Results as CSV
curl -o results.csv https://lead-scoring-x2jt.onrender.com/docs#/default/export_results_results_export_get


Downloads a CSV file of all scored leads.

### Rule Logic & Prompts Used

The system calculates Total Lead Score = Rule-Based Score + AI Score.

✅ Rule-Based Scoring

Role Relevance

Decision makers (CEO, Founder, Head, VP, Director) → +20 points

Influencers (Manager, Team Lead, Specialist) → +10 points

Industry Match

Exact match with ideal_use_cases → +20 points

Different but present → +10 points

Data Completeness

All fields filled → +10 points

### AI Scoring (via OpenAI)

A ChatGPT prompt is sent:

Prospect: {lead}
Offer: {offer}
Question: Classify buying intent (High, Medium, Low) and explain in 1-2 sentences.


If AI says High → +50 points

If AI says Medium → +30 points

If AI says Low → +10 points

The intent label and reasoning text from the model are saved.

Example Final Output
Name	Role	Company	Intent	Score	Reasoning
John Doe	CEO	TechCorp	High	80	High buying intent because SaaS company needs CRM automation.
Jane Smith	Manager	ShopEasy	Medium	50	Medium intent as role is influencer.
