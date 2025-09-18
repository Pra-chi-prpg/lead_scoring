from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
import csv, io
import openai
from fastapi.responses import StreamingResponse

app = FastAPI(title="Lead Scoring Backend")

# --- Global storage ---
offer_data = None
leads = []
results = []

# --- OpenAI API key ---
openai.api_key = "YOUR_OPENAI_API_KEY"

# Offer Input API

class Offer(BaseModel):
    name: str
    value_props: List[str]
    ideal_use_cases: List[str]

@app.post("/offer")
async def create_offer(offer: Offer):
    global offer_data
    offer_data = offer
    return {"status": "Offer saved", "offer": offer}


#Leads Upload API

@app.post("/leads/upload")
async def upload_leads(file: UploadFile = File(...)):
    global leads
    leads = []
    content = await file.read()
    decoded = content.decode('utf-8').splitlines()
    reader = csv.DictReader(decoded)
    for row in reader:
        leads.append(row)
    return {"status": "Leads uploaded", "total": len(leads)}

#  Scoring Functions

def rule_score(lead, offer):
    score = 0
    # Role relevance
    decision_makers = ["CEO", "Founder", "Head", "VP", "Director"]
    influencers = ["Manager", "Team Lead", "Specialist"]
    role_lower = lead['role'].lower()
    if any(dm.lower() in role_lower for dm in decision_makers):
        score += 20
    elif any(inf.lower() in role_lower for inf in influencers):
        score += 10
    
    # Industry match
    industry_lower = lead['industry'].lower()
    ideal_use_cases_lower = [i.lower() for i in offer.ideal_use_cases]
    if industry_lower in ideal_use_cases_lower:
        score += 20
    elif industry_lower != "":
        score += 10

    # Data completeness
    if all(lead[field] for field in ['name','role','company','industry','location','linkedin_bio']):
        score += 10

    return score

def ai_score(lead, offer):
    prompt = f"""
    Prospect: {lead}
    Offer: {offer.dict()}
    Question: Classify buying intent (High, Medium, Low) and explain in 1-2 sentences.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            temperature=0
        )
        text = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        text = "High"  # fallback in case of API failure

    # Map AI intent to points
    if "High" in text:
        points = 50
        label = "High"
    elif "Medium" in text:
        points = 30
        label = "Medium"
    else:
        points = 10
        label = "Low"

    return points, label, text

#  Score Leads API

@app.post("/score")
def score_leads():
    global results
    if not offer_data or not leads:
        return {"status": "Please upload offer and leads first."}

    results = []
    for lead in leads:
        r_score = rule_score(lead, offer_data)
        a_points, intent_label, reasoning = ai_score(lead, offer_data)
        total_score = r_score + a_points
        results.append({
            "name": lead['name'],
            "role": lead['role'],
            "company": lead['company'],
            "intent": intent_label,
            "score": total_score,
            "reasoning": reasoning
        })
    return {"status": "Leads scored", "total": len(results)}


#  Get Results API

@app.get("/results")
def get_results():
    return results

#  Export Results as CSV

@app.get("/results/export")
def export_results():
    if not results:
        return {"status": "No results to export."}
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["name","role","company","intent","score","reasoning"])
    writer.writeheader()
    writer.writerows(results)
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=results.csv"})

