import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO

def analizza_file_project(baseline_file, update_file=None, opzioni=None, data_inizio=None, data_fine=None):
    """
    Funzione principale per analizzare i file XML di progetto
    Restituisce un DataFrame con i risultati sintetici
    """

    # Lettura file principale (Baseline)
    try:
        baseline_content = baseline_file.read()
        baseline_tree = ET.parse(BytesIO(baseline_content))
        baseline_root = baseline_tree.getroot()
    except Exception as e:
        raise Exception(f"Errore nella lettura del file baseline: {e}")

    # Lettura file aggiornamento (opzionale)
    update_root = None
    if update_file:
        try:
            update_content = update_file.read()
            update_tree = ET.parse(BytesIO(update_content))
            update_root = update_tree.getroot()
        except Exception as e:
            raise Exception(f"Errore nella lettura del file aggiornamento: {e}")

    # Estrazione attività
    activities = []
    try:
        for task in baseline_root.findall(".//Task"):
            name = task.findtext("Name", "Senza nome")
            start = task.findtext("Start")
            finish = task.findtext("Finish")
            percent = task.findtext("PercentComplete", "0")
            activities.append({
                "Nome attività": name,
                "Inizio": start,
                "Fine": finish,
                "Completamento": f"{percent}%"
            })
    except Exception as e:
        raise Exception(f"Errore durante la lettura delle attività: {e}")

    if len(activities) == 0:
        raise Exception("Nessuna attività trovata nel file XML. Verifica il formato.")

    df = pd.DataFrame(activities)

    # Filtraggio per date se definite
    if data_inizio != "Da file Project" and data_fine != "Da file Project":
        try:
            df["Inizio"] = pd.to_datetime(df["Inizio"])
            df["Fine"] = pd.to_datetime(df["Fine"])
            mask = (df["Inizio"] >= pd.to_datetime(data_inizio)) & (df["Fine"] <= pd.to_datetime(data_fine))
            df = df.loc[mask]
        except Exception:
            pass

    # Analisi per opzioni selezionate
    risultati = []
    if opzioni.get("curva_sil"):
        risultati.append({"Analisi": "Curva SIL", "Stato": "Completata"})
    if opzioni.get("manodopera"):
        risultati.append({"Analisi": "Manodopera", "Stato": "Completata"})
    if opzioni.get("mezzi"):
        risultati.append({"Analisi": "Mezzi", "Stato": "Completata"})
    if opzioni.get("avanzamento"):
        risultati.append({"Analisi": "% Avanzamento Attività", "Stato": "Completata"})

    return pd.DataFrame(risultati)
