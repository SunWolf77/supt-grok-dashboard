import requests
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# --- Stress Function ---
def stress(phi, C=1, D=100):
    return -C * (1 - np.exp(-D * (phi - 0.5)**2))

# --- Fetch NOAA Solar Wind ---
def fetch_noaa():
    url = "https://services.swpc.noaa.gov/json/solar-wind/propagated.json"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        times = pd.to_datetime([d["time_tag"] for d in data]).tz_localize(None)
        speeds = [d.get("speed", 400) for d in data]
        delta_phi = [0.5 - (s/2000) for s in speeds]
        return pd.DataFrame({"time": times, "delta_phi": delta_phi})
    except Exception as e:
        print("NOAA fetch failed, using stub data:", e)
        sample = {"time_tag": ["2025-09-01T00:00:00Z","2025-09-01T06:00:00Z","2025-09-01T12:00:00Z"],
                  "speed": [400,520,700]}
        times = pd.to_datetime(sample["time_tag"]).tz_localize(None)
        delta_phi = [0.5 - (s/2000) for s in sample["speed"]]
        return pd.DataFrame({"time": times, "delta_phi": delta_phi})

# --- Fetch USGS Quakes (Campi Flegrei region) ---
def fetch_usgs(lat=40.82, lon=14.13, radius=50, minmag=1.0, days=7):
    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(days=days)
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start:%Y-%m-%d}&endtime={end:%Y-%m-%d}&latitude={lat}&longitude={lon}&maxradiuskm={radius}&minmagnitude={minmag}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        times = pd.to_datetime([f["properties"]["time"] for f in data["features"]], unit="ms").tz_localize(None)
        mags = [f["properties"]["mag"] for f in data["features"]]
        return pd.DataFrame({"time": times, "magnitude": mags})
    except Exception as e:
        print("USGS fetch failed:", e)
        return pd.DataFrame(columns=["time","magnitude"])

# --- Build Dashboard ---
def build_dashboard():
    df_noaa = fetch_noaa()
    df_noaa["stress"] = df_noaa["delta_phi"].apply(stress)
    df_usgs = fetch_usgs()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # ΔΦ Drift
    fig.add_trace(go.Scatter(x=df_noaa["time"], y=df_noaa["delta_phi"], mode="lines+markers",
                             name="ΔΦ Drift", line=dict(color="orange")), secondary_y=False)
    # Stress
    fig.add_trace(go.Scatter(x=df_noaa["time"], y=df_noaa["stress"], mode="lines+markers",
                             name="Stress k(ΔΦ)", line=dict(color="red")), secondary_y=True)
    # Quakes
    if not df_usgs.empty:
        fig.add_trace(go.Scatter(x=df_usgs["time"], y=[0]*len(df_usgs),
                                 mode="markers+text",
                                 marker=dict(size=[max(5, m*4) for m in df_usgs["magnitude"]],
                                             color="blue", opacity=0.7),
                                 text=[f"M{m}" for m in df_usgs["magnitude"]],
                                 textposition="top center",
                                 name="Quakes"), secondary_y=False)

    # Threshold
    fig.add_hline(y=-1.0, line=dict(color="black", dash="dash"),
                  annotation_text="ZFCM Threshold", secondary_y=True)

    # Title with timestamp + alert check
    last_update = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    alert_triggered = (df_noaa["stress"].min() <= -1.0)
    title_text = f"SUPT ψ-Fold Dashboard (Live NOAA + USGS)<br><span style='font-size:14px'>Last update: {last_update}</span>"
    if alert_triggered:
        title_text = f"🚨 ALERT: ZFCM Threshold Breached 🚨<br>{title_text}"

    fig.update_layout(
        title=title_text,
        title_font=dict(color="red" if alert_triggered else "black", size=20),
        xaxis_title="Date/Time (UTC)",
        xaxis=dict(tickformat="%H:%M\n%b %d", tickangle=0, showgrid=True),
        yaxis=dict(title="ΔΦ Drift", side="left"),
        yaxis2=dict(title="Stress", side="right"),
        template="plotly_white",
        height=700
    )

    out_path = "/mnt/data/supt_dashboard.html"
    fig.write_html(out_path)
    print("Dashboard saved to", out_path)

if __name__ == "__main__":
    build_dashboard()
