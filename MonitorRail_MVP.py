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
mpp_file = st.sidebar.file_uploader("Carica il file Project principale", type=["xml", "mpp"])
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

    # Esegui motore principale con parametri selezionati
    cmd = [
        "python", "MonitorRail_MVP.py",
        f"--project={mpp_file.name if mpp_file else ''}",
        f"--progress={progress_file.name if progress_file else ''}",
        f"--start={start_date.strftime('%d/%m/%Y') if start_date else 'auto'}",
        f"--end={end_date.strftime('%d/%m/%Y') if end_date else 'auto'}",
        f"--float-threshold={float_threshold}"
    ]

    # Log completo dell'esecuzione
    log_file_path = os.path.join(output_dir, "run_log.txt")
    with open(log_file_path, "w") as log:
        process = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, text=True)

    # Mostra log direttamente nella UI
    if os.path.exists(log_file_path):
        with st.expander("📋 Log Analisi / Avvisi"):
            with open(log_file_path, "r") as f:
                st.text(f.read())

    st.success("Analisi completata ✅")

    # Visualizza risultati se presenti
    if os.path.exists(os.path.join(output_dir, "summary_alerts.csv")):
        st.subheader("🚨 Alert Attività Critiche e Sub-Critiche")
        df_alert = pd.read_csv(os.path.join(output_dir, "summary_alerts.csv"))
        st.dataframe(df_alert, use_container_width=True)
        st.download_button("⬇️ Scarica summary_alerts.csv", os.path.join(output_dir, "summary_alerts.csv"))

    if os.path.exists(os.path.join(output_dir, "mezzi_distinti.csv")):
        st.subheader("🚜 Mezzi distinti per tipologia")
        df_mezzi = pd.read_csv(os.path.join(output_dir, "mezzi_distinti.csv"))
        st.dataframe(df_mezzi, use_container_width=True)
        st.download_button("⬇️ Scarica mezzi_distinti.csv", os.path.join(output_dir, "mezzi_distinti.csv"))

    if os.path.exists(os.path.join(output_dir, "curva_SIL.png")):
        st.subheader("📈 Curva di Produzione SIL")
        st.image(os.path.join(output_dir, "curva_SIL.png"))
        st.download_button("⬇️ Scarica curva_SIL.png", os.path.join(output_dir, "curva_SIL.png"))

    if os.path.exists(os.path.join(output_dir, "diagramma_reticolare.png")):
        st.subheader("🔗 Diagramma Reticolare (Percorso Critico)")
        st.image(os.path.join(output_dir, "diagramma_reticolare.png"))
        st.download_button("⬇️ Scarica diagramma_reticolare.png", os.path.join(output_dir, "diagramma_reticolare.png"))

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
