import pandas as pd
import jpype
import jpype.imports
from jpype.types import *
import os

# === CONFIGURAZIONE ===
MPXJ_JAR_PATH = os.path.join(os.getcwd(), "mpxj-all.jar")

def avvia_jvm():
    """Avvia la JVM se non è già in esecuzione"""
    if not jpype.isJVMStarted():
        jpype.startJVM(classpath=[MPXJ_JAR_PATH])

def leggi_mpp(file_path):
    """Legge un file MPP usando MPXJ"""
    from net.sf.mpxj.reader import UniversalProjectReader
    reader = UniversalProjectReader()
    project = reader.read(file_path)
    return project

def estrai_attivita_da_mpp(file_path):
    """Estrae le attività principali da un file MPP"""
    avvia_jvm()
    project = leggi_mpp(file_path)
    data = []

    for task in project.getTasks():
        if task.getName():
            data.append({
                "Nome attività": task.getName(),
                "Inizio": str(task.getStart()),
                "Fine": str(task.getFinish()),
                "Durata (giorni)": str(task.getDuration()),
                "% Completamento": float(task.getPercentageComplete()),
                "Costo previsto": float(task.getCost()),
                "Costo effettivo": float(task.getActualCost())
            })

    df = pd.DataFrame(data)
    return df

def filtra_attivita_per_periodo(df, data_inizio, data_fine):
    """Filtra le attività nel range di date selezionato"""
    try:
        if data_inizio and data_fine and data_inizio != "Da file Project" and data_fine != "Da file Project":
            df["Inizio"] = pd.to_datetime(df["Inizio"], errors="coerce")
            df["Fine"] = pd.to_datetime(df["Fine"], errors="coerce")
            mask = (df["Inizio"] >= pd.to_datetime(data_inizio)) & (df["Fine"] <= pd.to_datetime(data_fine))
            return df.loc[mask]
        else:
            return df
    except Exception:
        return df

def analizza_file_project_mpp(mpp_file_path, opzioni=None, data_inizio=None, data_fine=None):
    """Funzione principale di analisi"""
    df = estrai_attivita_da_mpp(mpp_file_path)
    df_filtrato = filtra_attivita_per_periodo(df, data_inizio, data_fine)

    risultati = []
    grafici = {}

    if opzioni.get("curva_sil"):
        risultati.append({"Analisi": "Curva SIL", "Stato": "Completata (placeholder)"})
    if opzioni.get("manodopera"):
        risultati.append({"Analisi": "Manodopera", "Stato": "Completata (placeholder)"})
    if opzioni.get("mezzi"):
        risultati.append({"Analisi": "Mezzi", "Stato": "Completata (placeholder)"})
    if opzioni.get("avanzamento"):
        risultati.append({"Analisi": "% Avanzamento Attività", "Stato": "Completata (placeholder)"})

    return df_filtrato, pd.DataFrame(risultati)
