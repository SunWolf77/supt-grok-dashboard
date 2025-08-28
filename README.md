# SUPT-Grok Dashboard v1.0

Baseline implementation of the SUPT ψ-Fold Dashboard for Grok / SuperGrok validation.

## 📦 Contents
- `dashboard.py` — main dashboard script (NOAA + USGS + SUPT stress)
- `requirements.txt` — dependencies list
- `run-dashboard.bat` — Windows launcher

## 🚀 Setup
1. Unzip the package anywhere (e.g., Desktop).
2. Open a terminal in that folder and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Usage
- On Windows: double-click `run-dashboard.bat`
- Or run manually:
   ```bash
   python dashboard.py
   ```

## 🔍 Features
- Live **NOAA Solar Wind** data (ΔΦ drift proxy)
- Live **USGS Earthquake** data (Campi Flegrei region, past 7 days)
- SUPT **stress k(ΔΦ)** overlay
- **ZFCM Threshold** marker (-1.0)
- Auto UTC timestamp in chart title
- 🚨 **ALERT banner** when stress crosses threshold

## 📘 Notes
- Requires Python 3.9+
- Internet connection needed for live NOAA/USGS feeds (falls back to stubs if offline)
- Output is written to `supt_dashboard.html` and opened in your browser
