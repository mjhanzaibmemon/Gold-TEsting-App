from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from fpdf import FPDF
import qrcode
import os
import random

# Import database model
from database import Report, session

# Initialize app
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Constants
RATTI_GRAMS = 1.21
TOLA_GRAMS = 11.664
GOLD_DENSITY = 19.3

# Utility Functions
def generate_serial():
    return f"TGT-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"

def generate_pdf(data, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(255, 165, 0)
    pdf.cell(0, 10, "TEZAB GOLD TESTING - PREMIUM REPORT", ln=True, align="C")
    
    if os.path.exists("static/logo.png"):
        pdf.image("static/logo.png", 10, 10, 25)
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)
    pdf.set_font("Arial", "", 12)

    for key, value in data.items():
        if key.startswith("_"):
            pdf.ln(3)
        else:
            pdf.cell(60, 8, f"{key}:", 0)
            pdf.cell(0, 8, str(value), ln=True)

    # Watermark
    pdf.set_text_color(230, 230, 230)
    pdf.set_font("Arial", "B", 48)
    pdf.set_xy(40, 160)
    pdf.cell(0, 10, "TEZAB", align="C")

    # QR Code
    qr_path = f"static/{filename.replace('.pdf', '_qr.png')}"
    qr = qrcode.make(f"Tezab Gold Report - {data.get('Serial No', 'N/A')}")
    qr.save(qr_path)
    pdf.image(qr_path, 160, 240, 30)
    if os.path.exists(qr_path):
        os.remove(qr_path)

    pdf.output(f"static/{filename}")

# Lab calculation
def lab_gold_calculation(weight_air, weight_water):
    # Volume
    volume = weight_air - weight_water
    
    if volume <= 0:
        ratti_diff = 0.0
    else:
        # Specific Gravity
        density = weight_air / volume
        
        # Ratti Difference Formula: 96 - ((SG × 96) / 19.3)
        ratti_diff = 96 - ((density * 96) / GOLD_DENSITY)
        ratti_diff = abs(round(ratti_diff, 2))
    
    # Purity from Ratti Difference
    purity_fraction = 1 - (ratti_diff / 96)
    purity_fraction = max(0, min(purity_fraction, 1))
    
    # Pure gold
    pure_gold = weight_air * purity_fraction
    
    # Purity % and Karat
    purity = round(purity_fraction * 100, 2)
    karat = round((purity / 100) * 24, 2)
    
    return {
        "ratti_diff": ratti_diff,
        "pure_gold": pure_gold,
        "purity": purity,
        "karat": karat,
    }

# Routes
@app.get("/", response_class=HTMLResponse)
def form_page(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/submit", response_class=HTMLResponse)
def process_form(
    request: Request,
    client_name: str = Form("Walk-in Customer"),
    weight_air: float = Form(...),
    weight_water: float = Form(...),
    gold_rate_tola: float = Form(355000)
):
    now = datetime.now()
    serial = generate_serial()
    gold_rate_gram = gold_rate_tola / TOLA_GRAMS

    # Calculate
    calc = lab_gold_calculation(weight_air, weight_water)
    
    # Save in DB
    report = Report(
        serial_no=serial,
        client_name=client_name or "Walk-in Customer",
        date_time=now.strftime("%Y-%m-%d | %I:%M %p"),
        gold_rate_tola=gold_rate_tola,
        gold_rate_gram=round(gold_rate_gram, 2),
        weight_air=weight_air,
        weight_water=weight_water,
        purity=calc["purity"],
        karat=calc["karat"],
        pure_gold=round(calc["pure_gold"], 4),
        impurities=round(weight_air - calc["pure_gold"], 4),
        estimated_value=round(calc["pure_gold"] * gold_rate_gram, 2)
    )
    session.add(report)
    session.commit()

    # Display data
    extra_data = {
        "⚖️ Weight in Air": f"{weight_air:.3f} g",
        "💧 Weight in Water": f"{weight_water:.3f} g",
        "📊 Ratti Difference": f"{calc['ratti_diff']} ratti",
        "🥇 Pure Gold": f"{calc['pure_gold']:.4f} g",
        "💰 Estimated Value": f"Rs. {round(calc['pure_gold']*gold_rate_gram,2):,.2f}"
    }

    return templates.TemplateResponse("result.html", {
        "request": request,
        "data": report,
        "extra_data": extra_data
    })

@app.post("/generate", response_class=FileResponse)
async def generate(
    request: Request,
    client: str = Form(""),
    weight_air: float = Form(...),
    weight_water: float = Form(...),
    gold_rate: float = Form(...)
):
    serial = generate_serial()
    now = datetime.now().strftime("%Y-%m-%d | %I:%M %p (PKT)")
    client = client.strip() or "Walk-in Customer"
    gram_rate = round(gold_rate / TOLA_GRAMS, 2)

    # Calculate
    calc = lab_gold_calculation(weight_air, weight_water)
    
    # PDF data
    data = {
        "Serial No": serial,
        "Client": client,
        "Date & Time": now,
        "Gold Rate": f"Rs. {gold_rate:,.2f} per Tola (Rs. {gram_rate} per gram)",
        "_": "",
        "Weight in Air": f"{weight_air:.3f} grams",
        "Weight in Water": f"{weight_water:.3f} grams",
        "Ratti Difference": f"{calc['ratti_diff']} ratti",
        "_1": "",
        "Purity": f"{calc['purity']:.2f}%",
        "Karat": f"{calc['karat']:.2f}K / 24K",
        "Pure Gold": f"{calc['pure_gold']:.4f} g",
        "_2": "",
        "Estimated Value": f"Rs. {round(calc['pure_gold']*gram_rate,2):,.2f}",
        "Testing Fee": "Rs. 200",
        "_3": "",
        "Powered by": "Tezab Gold Testing Software"
    }

    filename = f"{serial}.pdf"
    generate_pdf(data, filename)

    return FileResponse(path=f"static/{filename}", filename=filename, media_type='application/pdf')

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
