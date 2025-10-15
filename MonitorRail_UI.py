import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import tempfile
import os

# ===========================================================
# MONITOR RAIL - CENTRALE DI CONTROLLO
# ===========================================================

st.set_page_config(page_title="MonitorRail Control Center", layout="wide")
st.title("🚄 MonitorRail - Centrale di Controllo")

st.markdown("""
Benvenuto nella **Centrale di Controllo MonitorRail**.  
Carica i due file di programma lavori (baseline e avanzamento) in formato **MS Project (.mpp, .xml, .csv)**  
per avviare l’analisi e confrontare le informazioni.
""")

# ===========================================================
# SEZIONE 1 - CARICAMENTO FILE BASELINE
# ===========================================================
st.header("📘 Programma Lavori - Baseline")
baseline_file = st.file_uploader(
    "Carica file di baseline (.mpp / .xml / .csv)",
    type=["mpp", "xml", "csv"],
    key="baseline"
)

# ===========================================================
# SEZIONE 2 - CARICAMENTO FILE AVANZAMENTO (FACOLTATIVO)
# ===========================================================
st.header("📗 Programma Lavori - Avanzamento (facoltativo)")
progress_file = st.file_uploader(
    "Carica file di avanzamento (.mpp / .xml / .csv)",
    type=["mpp", "xml", "csv"],
    key="progress"
)

# ===========================================================
# SEZIONE 3 - PARAMETRI E AVVIO ANALISI
# ===========================================================
st.header("⚙️ Parametri di Analisi")

float_threshold = st.slider("Margine di flessibilità (giorni)", 0, 30, 5)
start_analysis = st.button("▶️ Avvia analisi del programma lavori")

# ===========================================================
# FUNZIONE DI LETTURA XML DI TEST
# ===========================================================
def parse_xml(file):
    try:
        tree = ET.parse(file)
        root = tree.getroot()
        tasks = []
        for task in root.findall(".//Task"):
            name = task.findtext("Name")
            duration = task.findtext("Duration")
            start = task.findtext("Start")
            finish = task.findtext("Finish")
            if name:
                tasks.append({
                    "Nome Attività": name,
                    "Durata": duration,
                    "Data Inizio": start,
                    "Data Fine": finish
                })
        return pd.DataFrame(tasks)
    except Exception as e:
        st.error(f"Errore nel parsing XML: {e}")
        return None

# ===========================================================
# ESECUZIONE ANALISI
# ===========================================================
if start_analysis:
    if not baseline_file:
        st.error("⚠️ Carica almeno il file di baseline per procedere.")
    else:
        st.info("⏳ Analisi in corso...")

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(baseline_file.getbuffer())
            baseline_path = tmp.name

        df_baseline = None
        if baseline_file.name.endswith(".xml"):
            df_baseline = parse_xml(baseline_path)
        elif baseline_file.name.endswith(".csv"):
            df_baseline = pd.read_csv(baseline_path)
        else:
            st.warning("🟡 File .mpp non leggibile direttamente, per ora carica un .xml esportato da Project.")
        
        if df_baseline is not None and not df_baseline.empty:
            st.success("✅ File baseline caricato e letto con successo.")
            st.dataframe(df_baseline.head(20), use_container_width=True)

        # Lettura file avanzamento se fornito
        if progress_file:
            with tempfile.NamedTemporaryFile(delete=False) as tmp2:
                tmp2.write(progress_file.getbuffer())
                progress_path = tmp2.name

            df_progress = None
            if progress_file.name.endswith(".xml"):
                df_progress = parse_xml(progress_path)
            elif progress_file.name.endswith(".csv"):
                df_progress = pd.read_csv(progress_path)
            else:
                st.warning("🟡 File .mpp non leggibile direttamente, per ora carica un .xml esportato da Project.")
            
            if df_progress is not None and not df_progress.empty:
                st.success("✅ File avanzamento caricato e letto con successo.")
                st.dataframe(df_progress.head(20), use_container_width=True)

        st.info("Analisi completata. I prossimi step includeranno calcolo percorsi critici, ritardi e risorse.")

# ===========================================================
# FOOTER
# ===========================================================
st.markdown("---")
st.caption("💡 MonitorRail v2.0 - sviluppo in corso per controllo avanzato appalti ferroviari.")
