import streamlit as st
from MonitorRail_MVP import analizza_file_project, estrai_date_progetto
import pandas as pd

st.set_page_config(page_title="MonitorRail CC", layout="wide")
st.title("🚄 MonitorRail - Centrale di Controllo")

if 'first_run' not in st.session_state:
    st.session_state.first_run = True

# ======================================
# Sidebar Capitoli Compatti
# ======================================
st.sidebar.header("⚙️ Parametri Analisi")

# 1. Primo File Project
st.sidebar.subheader("1️⃣ Baseline")
baseline_file = st.sidebar.file_uploader("Carica file (.xml)", type=["xml"])

# 2. Secondo File (Facoltativo)
st.sidebar.subheader("2️⃣ Aggiornamento")
with st.sidebar.expander("Facoltativo"):
    avanzamento_file = st.file_uploader("Carica file (.xml)", type=["xml"])

# 3. Periodo
st.sidebar.subheader("3️⃣ Periodo da analizzare")
start_def, end_def = estrai_date_progetto(baseline_file) if baseline_file else (pd.Timestamp.now(), pd.Timestamp.now())
start_date = st.sidebar.date_input("Data inizio", value=start_def)
end_date = st.sidebar.date_input("Data fine", value=end_def)
start_display = "Da file Project" if start_date == start_def else start_date.strftime("%d/%m/%Y")
end_display = "Da file Project" if end_date == end_def else end_date.strftime("%d/%m/%Y")
st.sidebar.markdown(f"**Periodo:** {start_display} → {end_display}")

# 4. Elementi da analizzare
st.sidebar.subheader("4️⃣ Elementi da analizzare")
analisi_sil = st.sidebar.checkbox("📊 SIL")
analisi_manodopera = st.sidebar.checkbox("👷 Manod.")
analisi_mezzi = st.sidebar.checkbox("🚜 Mezzi")
analisi_percentuale = st.sidebar.checkbox("📈 % Avanzamento")

# ======================================
# Pulsanti compatti
# ======================================
st.sidebar.markdown("---")
col1, col2 = st.sidebar.columns(2)
with col1:
    run_analysis = st.button("▶️ Avvia", use_container_width=True)
with col2:
    reset_analysis = st.button("🔄 Refresh", use_container_width=True)

# ======================================
# Funzioni pulsanti
# ======================================
if reset_analysis:
    st.session_state.first_run = True
    st.experimental_rerun()

if run_analysis:
    st.session_state.first_run = False
    if not baseline_file:
        st.error("⚠️ Carica almeno il file principale (.xml)")
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

        # Log
        with st.expander("📋 Log", expanded=True):
            for msg in risultati['log']:
                st.text(msg)

        # Tabella
        st.subheader("📊 Tabella Attività")
