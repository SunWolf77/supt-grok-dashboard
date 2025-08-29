import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime, timezone

def stress(phi, C=1, D=100):
    return -C * (1 - np.exp(-D * (phi - 0.5)**2))

times = pd.date_range(datetime.now(timezone.utc).replace(microsecond=0), periods=50, freq="min")
delta_phi = np.linspace(0.3, 0.35, len(times)) + 0.02*np.sin(np.linspace(0, 6, len(times)))
stress_vals = [stress(p) for p in delta_phi]

df = pd.DataFrame({"time": times, "delta_phi": delta_phi, "stress": stress_vals})

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["time"], y=df["delta_phi"], mode="lines+markers",
                         name="ΔΦ Drift", line=dict(color="orange")))
fig.add_trace(go.Scatter(x=df["time"], y=df["stress"], mode="lines+markers",
                         name="Stress k(ΔΦ)", line=dict(color="red")))
fig.add_hline(y=-1.0, line=dict(color="black", dash="dash"), annotation_text="ZFCM Threshold")

fig.update_layout(
    title=f"SUPT ψ-Fold Dashboard (Mini Baseline)\nLast update: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
    xaxis_title="Date/Time (UTC)",
    yaxis_title="ΔΦ Drift",
    yaxis2=dict(title="Stress", overlaying="y", side="right"),
    template="plotly_white"
)

out_path = "index.html"
fig.write_html(out_path)
print(f"Dashboard built: {out_path}")
