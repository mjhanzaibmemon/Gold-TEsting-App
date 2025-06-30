from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from fpdf import FPDF
import qrcode
import os
import random

# Import database model
from database import Report, session

# Initialize app (only once)
app = FastAPI()

# Mount static files (only once)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates (only once)
templates = Jinja2Templates(directory="templates")

# Utility Functions
def generate_serial():
    return f"TGT-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"

def calculate_density(w_air, w_water):
    if w_water >= w_air:
        raise ValueError("Weight in water must be less than weight in air")
    return w_air / (w_air - w_water)

def estimate_purity(density):
    gold_density = 19.32
    purity = min((density / gold_density) * 100, 100.0)
    karat = (purity / 100) * 24
    return round(purity, 2), round(karat, 2)

def generate_pdf(data, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(255, 165, 0)
    pdf.cell(0, 10, "✨ TEZAB GOLD TESTING — PREMIUM REPORT ✨", ln=True, align="C")
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
    qr = qrcode.make(f"Tezab Gold Report - {data['🧾 Serial No']}")
    qr.save(qr_path)
    pdf.image(qr_path, 160, 240, 30)
    os.remove(qr_path)

    pdf.output(f"static/{filename}")

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
    serial = f"TGT-{now.strftime('%Y%m%d')}-{random.randint(1000,9999)}"
    gold_rate_gram = gold_rate_tola / 11.664

    # Density and purity calculation
    volume = weight_air - weight_water
    density = weight_air / volume if volume else 0
    gold_density = 19.32
    purity = min((density / gold_density) * 100, 100)
    karat = round((purity / 100) * 24, 2)
    pure_gold = (purity / 100) * weight_air
    impurities = weight_air - pure_gold
    estimated_value = round(pure_gold * gold_rate_gram, 2)

    # Save in DB
    report = Report(
        serial_no=serial,
        client_name=client_name or "Walk-in Customer",
        date_time=now.strftime("%Y-%m-%d | %I:%M %p"),
        gold_rate_tola=gold_rate_tola,
        gold_rate_gram=gold_rate_gram,
        weight_air=weight_air,
        weight_water=weight_water,
        purity=round(purity, 2),
        karat=karat,
        pure_gold=round(pure_gold, 4),
        impurities=round(impurities, 4),
        estimated_value=estimated_value
    )
    session.add(report)
    session.commit()

    return templates.TemplateResponse("result.html", {
        "request": request,
        "data": report
    })

@app.post("/generate", response_class=FileResponse)
async def generate(
    request: Request,
    client: str = Form(""),
    weight_air: float = Form(...),
    weight_water: float = Form(...),
    gold_rate: float = Form(...),
):
    serial = generate_serial()
    now = datetime.now().strftime("%Y-%m-%d | %I:%M %p (PKT)")
    client = client.strip() or "Walk-in Customer"
    gram_rate = round(gold_rate / 11.664, 2)
    density = calculate_density(weight_air, weight_water)
    purity, karat = estimate_purity(density)
    pure_gold = round((purity / 100) * weight_air, 4)
    impurity = round(weight_air - pure_gold, 4)
    value = round(pure_gold * gram_rate, 2)

    data = {
        "🧾 Serial No": serial,
        "👤 Client": client,
        "📆 Date & Time": now,
        "💰 Gold Rate": f"Rs. {gold_rate:.2f} per Tola ({gram_rate} per gram)",
        "_": "",
        "⚖️ Sample Weight": f"{weight_air:.3f} grams",
        "🌟 Purity": f"{purity:.2f}%",
        "👑 Karat": f"{karat:.2f}K / 24K",
        "🥇 Pure Gold": f"{pure_gold:.4f} g ({pure_gold*1000:.1f} mg)",
        "🔬 Impurities": f"{impurity:.4f} g ({impurity*1000:.1f} mg)",
        "_1": "",
        "💰 Estimated Value": f"Rs. {value}",
        "🧾 Testing Fee": "Rs. 200",
        "_2": "",
        "✨ Powered by": "Tezab Gold Testing Software"
    }

    filename = f"{serial}.pdf"
    generate_pdf(data, filename)

    return FileResponse(path=f"static/{filename}", filename=filename, media_type='application/pdf')

# Run the app when directly executed
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)