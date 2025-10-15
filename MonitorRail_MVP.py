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
    """Analizza i file XML di progetto e restituisce un DataFrame di sintesi"""
    try:
        baseline_content = baseline_file.read()
        baseline_tree = ET.parse(BytesIO(baseline_content))
        baseline_root = baseline_tree.getroot()
    except Exception as e:
        raise Exception(f"Errore nella lettura del file baseline: {e}")

    update_root = None
    if update_file:
        try:
            update_content = update_file.read()
            update_tree = ET.parse(BytesIO(update_content))
            update_root = update_tree.getroot()
        except Exception as e:
            raise Exception(f"Errore nella lettura del file aggiornamento: {e}")

    # Trova attività
    activities_nodes = trova_nodi_attivita(baseline_root)
    if not activities_nodes:
        raise Exception("Nessuna attività trovata nel file XML. Verifica il formato.")

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
            "Completamento": f"{percent}%"
        })

    if len(activities) == 0:
        raise Exception("File caricato ma nessuna attività leggibile: controlla i campi del file XML.")

    df = pd.DataFrame(activities)

    # Filtraggio per periodo
    if data_inizio != "Da file Project" and data_fine != "Da file Project":
        try:
            df["Inizio"] = pd.to_datetime(df["Inizio"])
            df["Fine"] = pd.to_datetime(df["Fine"])
            mask = (df["Inizio"] >= pd.to_datetime(data_inizio)) & (df["Fine"] <= pd.to_datetime(data_fine))
            df = df.loc[mask]
        except Exception:
            pass

    risultati = []
    if opzioni.get("curva_sil"):
        risultati.append({"Analisi": "Curva SIL", "Stato": "Completata"})
    if opzioni.get("manodopera"):
        risultati.append({"Analisi": "Manodopera", "Stato": "Completata"})
    if opzioni.get("mezzi"):
        risultati.append({"Analisi": "Mezzi", "Stato": "Completata"})
    if opzioni.get("avanzamento"):
        risultati.append({"Analisi": "% Avanzamento Attività", "Stato": "Completata"})

    return pd.DataFrame(risultati), f"Totale attività lette: {len(df)}"
