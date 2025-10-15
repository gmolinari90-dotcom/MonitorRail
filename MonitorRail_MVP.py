import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO

def trova_nodi_attivita(root):
    """Tenta di trovare i nodi attività anche con namespace diversi"""
    possibili_tag = ["Task", "Activity", "Tasks/Task"]
    for tag in possibili_tag:
        tasks = root.findall(f".//{tag}")
        if tasks:
            return tasks
    # Se ci sono namespace, li cattura
    for elem in root.iter():
        if "Task" in elem.tag or "Activity" in elem.tag:
            return list(root.iter(elem.tag))
    return []

def analizza_file_project(baseline_file, update_file=None, opzioni=None, data_inizio=None, data_fine=None):
    """Analizza i file XML di progetto e restituisce una tabella di sintesi"""
    try:
        baseline_content = baseline_file.read()
        baseline_tree = ET.parse(BytesIO(baseline_content))
        baseline_root = baseline_tree.getroot()
    except Exception as e:
        raise Exception(f"Errore nella lettura del file baseline: {e}")

    # Trova attività
    activities_nodes = trova_nodi_attivita(baseline_root)
    if not activities_nodes:
        raise Exception("Nessuna attività trovata nel file XML. Verifica il formato.")

    # Estrazione base attività
    activities = []
    for task in activities_nodes:
        name = task.findtext("Name") or task.findtext("TaskName") or "Senza nome"
        start = task.findtext("Start") or task.findtext("StartDate")
        finish = task.findtext("Finish") or task.findtext("FinishDate")
        percent = task.findtext("PercentComplete") or task.findtext("PercentDone") or "0"
        activities.append({
            "Nome attività": name,
            "Inizio": start,
            "Fine": finish,
            "Completamento": float(percent)
        })

    df = pd.DataFrame(activities)
    if df.empty:
        raise Exception("File caricato ma nessuna attività leggibile: controlla i campi XML.")

    # Converte le date
    for col in ["Inizio", "Fine"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Filtraggio per periodo (solo se impostato)
    if data_inizio != "Da file Project" and data_fine != "Da file Project":
        mask = (df["Inizio"] >= pd.to_datetime(data_inizio)) & (df["Fine"] <= pd.to_datetime(data_fine))
        df = df.loc[mask]

    risultati = []
    grafici = {}

    # --- Curva SIL (S-Curve) ---
    if opzioni.get("curva_sil"):
        df = df.dropna(subset=["Fine"])
        df = df.sort_values("Fine")
        df["Cumulativo"] = df["Completamento"].cumsum() / df["Completamento"].sum() * 100
        grafici["Curva SIL"] = df[["Fine", "Cumulativo"]]
        risultati.append({"Analisi": "Curva SIL", "Stato": "Completata"})

    if opzioni.get("manodopera"):
        risultati.append({"Analisi": "Manodopera", "Stato": "Completata (placeholder)"})
    if opzioni.get("mezzi"):
        risultati.append({"Analisi": "Mezzi", "Stato": "Completata (placeholder)"})
    if opzioni.get("avanzamento"):
        risultati.append({"Analisi": "% Avanzamento Attività", "Stato": "Completata (placeholder)"})

    return pd.DataFrame(risultati), grafici, f"Totale attività lette: {len(df)}"
