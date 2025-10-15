import streamlit as st
import subprocess
import pandas as pd
import os

# ===========================================================
# MONITOR RAIL - INTERFACCIA STREAMLIT
# ===========================================================

st.set_page_config(page_title="MonitorRail Control Center", layout="wide")
st.title("🚄 MonitorRail - Centrale di Controllo")

st.sidebar.header("⚙️ Parametri di Analisi")

# --- Input file ---
mpp_file = st.sidebar.file_uploader("Carica il file Project principale (.xml o .mpp)", type=["xml", "mpp"])
progress_file = st.sidebar.file_uploader("(Facoltativo) Carica secondo file Project aggiornato", type=["xml", "mpp"])

# --- Filtri temporali ---
start_date = st.sidebar.date_input("Data inizio analisi")
end_date = st.sidebar.date_input("Data fine analisi")

# --- Parametri avanzati ---
float_threshold = st.sidebar.slider("Margine di flessibilità (giorni)", 0, 30, 5)

run_analysis = st.sidebar.button("▶️ Avvia Analisi")

# --- Output Directory ---
output_dir = "output_monitorrail"
os.makedirs(output_dir, exist_ok=True)

if run_analysis:
    st.info("Analisi in corso... Attendere il completamento.")

    # --- Salvataggio file caricati ---
    project_path = ""
    if mpp_file is not None:
        project_path = os.path.join(output_dir, mpp_file.name)
        with open(project_path, "wb") as f:
            f.write(mpp_file.getbuffer())
        if mpp_file.name.endswith('.mpp'):
            st.warning("File .mpp caricato: esporta in .xml da Project per un'analisi completa.")

    progress_path = ""
    if progress_file is not None:
        progress_path = os.path.join(output_dir, progress_file.name)
        with open(progress_path, "wb") as f:
            f.write(progress_file.getbuffer())
        if progress_file.name.endswith('.mpp'):
            st.warning("Secondo file .mpp caricato: esporta in .xml da Project per un'analisi completa.")

    # --- Esecuzione backend ---
    cmd = [
        "python", "MonitorRail_MVP.py",
        f"--project={project_path}",
        f"--progress={progress_path}",
        f"--start={start_date.strftime('%d/%m/%Y') if start_date else 'auto'}",
        f"--end={end_date.strftime('%d/%m/%Y') if end_date else 'auto'}",
        f"--float-threshold={float_threshold}"
    ]

    log_file_path = os.path.join(output_dir, "run_log.txt")
    with open(log_file_path, "w") as log:
        subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, text=True)

    # --- Mostra log direttamente nella UI ---
    if os.path.exists(log_file_path):
        with st.expander("📋 Log Analisi / Avvisi", expanded=True):
            with open(log_file_path, "r") as f:
                st.text(f.read())

    st.success("Analisi completata ✅")

    # --- Visualizza risultati ---
    summary_alert_path = os.path.join(output_dir, "summary_alerts.csv")
    if os.path.exists(summary_alert_path):
        st.subheader("🚨 Alert Attività Critiche e Sub-Critiche")
        df_alert = pd.read_csv(summary_alert_path)
        st.dataframe(df_alert, use_container_width=True)
        st.download_button("⬇️ Scarica summary_alerts.csv", summary_alert_path)

    mezzi_path = os.path.join(output_dir, "mezzi_distinti.csv")
    if os.path.exists(mezzi_path):
        st.subheader("🚜 Mezzi distinti per tipologia")
        df_mezzi = pd.read_csv(mezzi_path)
        st.dataframe(df_mezzi, use_container_width=True)
        st.download_button("⬇️ Scarica mezzi_distinti.csv", mezzi_path)

    curva_path = os.path.join(output_dir, "curva_SIL.png")
    if os.path.exists(curva_path):
        st.subheader("📈 Curva di Produzione SIL")
        st.image(curva_path)
        st.download_button("⬇️ Scarica curva_SIL.png", curva_path)

    diagramma_path = os.path.join(output_dir, "diagramma_reticolare.png")
    if os.path.exists(diagramma_path):
        st.subheader("🔗 Diagramma Reticolare (Percorso Critico)")
        st.image(diagramma_path)
        st.download_button("⬇️ Scarica diagramma_reticolare.png", diagramma_path)

st.sidebar.markdown("---")
st.sidebar.caption("💡 MonitorRail v1.0 - sviluppato per il controllo avanzato dei cantieri ferroviari.")

# ===========================================================
# GUIDA RAPIDA secondaria
# ===========================================================
st.markdown("""
### 🧭 Guida Rapida
- Carica il file di Project principale (.xml o .mpp)
- (Facoltativo) Carica un secondo file Project aggiornato con l'avanzamento attività
- Seleziona il periodo e la soglia del margine di flessibilità
  - Se non selezioni le date, verrà analizzato l'intero progetto
- Clicca **Avvia Analisi** per generare i grafici e gli alert
- I risultati saranno mostrati qui e salvati in `output_monitorrail/`
""")
