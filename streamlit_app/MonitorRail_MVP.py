# MonitorRail_MVP.py (client che chiama il microservizio)
import requests
import pandas as pd
from datetime import datetime
import io

# CONFIG — imposta l'URL del servizio e la chiave API (env o fixta durante test)
SERVICE_URL = "https://your-mpp-service.example.com"  # cambia con il tuo endpoint
API_KEY = "metti_la_tua_chiave_api"

def convert_mpp_to_json(mpp_bytes):
    url = f"{SERVICE_URL}/api/parse-mpp"
    headers = {"X-API-KEY": API_KEY}
    files = {"file": ("project.mpp", mpp_bytes)}
    r = requests.post(url, headers=headers, files=files, timeout=300)
    r.raise_for_status()
    return r.json()

def build_scurve_from_json(parsed_json, period="M"):
    """
    parsed_json: dict come restituito dal servizio
    period: 'M' per mese, 'W' per settimana
    """
    tasks = parsed_json.get("tasks", [])
    # collect timephased rows: periodStart, periodEnd, planned or value
    rows = []
    for t in tasks:
        t_id = t.get("id")
        for tp in t.get("timephased", []):
            start = tp.get("start")
            finish = tp.get("finish")
            value = tp.get("value") or 0.0
            # convert to pandas period (monthly)
            # we will bucket by month of period start
            try:
                dt = pd.to_datetime(start)
                period_label = dt.to_period(period).to_timestamp()
                rows.append({"period": period_label, "value": float(value)})
            except Exception:
                continue
    if not rows:
        return pd.DataFrame(columns=["period", "value", "cumulative"])
    df = pd.DataFrame(rows)
    df = df.groupby("period", as_index=False).sum()
    df = df.sort_values("period")
    df["cumulative"] = df["value"].cumsum()
    return df

def extract_tasks_in_period(parsed_json, start_date=None, end_date=None):
    tasks = parsed_json.get("tasks", [])
    rows = []
    for t in tasks:
        start = t.get("start")
        finish = t.get("finish")
        try:
            s = pd.to_datetime(start) if start else None
            f = pd.to_datetime(finish) if finish else None
        except Exception:
            s = f = None
        include = True
        if start_date and start_date != "Da file Project":
            try:
                sd = pd.to_datetime(start_date, dayfirst=True)
                if not s or s < sd:
                    include = False
            except Exception:
                pass
        if end_date and end_date != "Da file Project":
            try:
                ed = pd.to_datetime(end_date, dayfirst=True)
                if not f or f > ed:
                    include = False
            except Exception:
                pass
        if include:
            rows.append({
                "id": t.get("id"),
                "name": t.get("name"),
                "start": start,
                "finish": finish,
                "percentComplete": t.get("percentComplete"),
                "cost": t.get("cost"),
                "actualCost": t.get("actualCost")
            })
    return pd.DataFrame(rows)

