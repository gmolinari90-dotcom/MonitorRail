import streamlit as st
from MonitorRail_MVP import analizza_file_project, estrai_date_progetto
import pandas as pd

# --- Config pagina ---
st.set_page_config(page_title="MonitorRail", layout="wide")
st.title("🚄 MonitorRail - Centrale di Controllo")

if 'first_run' not in st.session_state:
    st.session_state.first_run = True

# ====================================================
# SIDEBAR STRUTTURATA
# ====================================================
st.sidebar.header("⚙️ Parametri Analisi")

# --- 1. Primo File Project (Baseline) ---
st.sidebar.subheader("1️⃣ Primo File Project (Baseline)")
baseline_file = st.sidebar.file_uploader("Carica file Project (.xml)", type=["xml"])

# --- 2. Secondo File Project (Facoltativo) ---
st.sidebar.subheader("2️⃣ (Facoltativo) Secondo File Project")
with st.sidebar.expander("Apri per caricare"):
    avanzamento_file = st.file_uploader("Carica file aggiornato (.xml)", type=["xml"])

# --- 3. Periodo da Analizzare ---
st.sidebar.subheader("3️⃣ Periodo da Analizzare")
if baseline_file:
    start_def, end_def = estrai_date_progetto(baseline_file)
else:
    start_def, end_def = pd.Timestamp.now(), pd.Timestamp.now()

start_placeholder = "Da file Project"
end_placeholder = "Da file Project"

start_date = st.sidebar.text_input("Data inizio (gg/mm/aaaa)", start_placeholder)
end_date = st.sidebar.text_input("Data fine (gg/mm/aaaa)", end_placeholder)

# --- 4. Elementi da Analizzare ---
st.sidebar.subheader("4️⃣ Elementi da Analizzare")
analisi_sil = st.sidebar.checkbox("Curva SIL")
analisi_manodopera = st.sidebar.checkbox("Manodopera")
analisi_mezzi = st.sidebar.checkbox("Mezzi")
analisi_percentuale = st.sidebar.checkbox("% Avanzamento Attività")

# ====================================================
# Pulsanti
# ====================================================
st.sidebar.markdown("---")
col1, col2 = st.sidebar.columns(2)
with col1:
    run_analysis = st.button("▶️ Avvia Analisi", use_container_width=True)
with col2:
    reset_analysis = st.button("🔄 Refresh", use_container_width=True)

# ====================================================
# Funzioni
# ====================================================
if reset_analysis:
    st.session_state.first_run = True
    st.experimental_rerun()

if run_analysis:
    st.session_state.first_run = False

    if not baseline_file:
        st.error("⚠️ Carica almeno il file Project principale.")
    else:
        risultati = analizza_file_project(
            baseline_file=baseline_file,
            avanzamento_file=avanzamento_file,
            start_date=start_date,
            end_date=end_date,
            analisi_sil=analisi_sil,
            analisi_manodopera=analisi_manodopera,
            analisi_mezzi=analisi_mezzi,
            analisi_percentuale=analisi_percentuale
        )

        st.subheader("📋 Log Analisi")
        for msg in risultati['log']:
            st.text(msg)

        st.subheader("📊 Tabella Attività")
        st.dataframe(risultati['df_finale'], use_container_width=True)

        for key, buf in risultati.get('csv_buffers', {}).items():
            st.download_button(
                f"⬇️ Scarica CSV {key.upper()}",
                data=buf.getvalue(),
                file_name=f"{key}.csv"
            )

# ====================================================
# Guida rapida (solo primo avvio)
# ====================================================
if st.session_state.first_run:
    st.markdown("""
    ### 🧭 Guida Rapida
    1️⃣ Carica il file Project principale (.xml)  
    2️⃣ (Facoltativo) Apri la tendina e carica un file aggiornato  
    3️⃣ Lascia "Da file Project" o imposta un periodo personalizzato  
    4️⃣ Seleziona gli elementi da analizzare  
    5️⃣ Premi **Avvia Analisi** o **Refresh** per ripartire
    """)
