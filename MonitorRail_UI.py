import streamlit as st
from MonitorRail_MVP import analizza_file_project
import time

st.set_page_config(page_title="MonitorRail", layout="wide")

if "first_run" not in st.session_state:
    st.session_state.first_run = True

st.title("🚄 MonitorRail – Analisi Avanzamento Progetto")

st.divider()
st.markdown("### 1️⃣ Primo File Project (Baseline)")
baseline_file = st.file_uploader("Carica il file XML del progetto principale", type=["xml"])

st.divider()
with st.expander("### 2️⃣ Secondo File Project (Aggiornamento Mensile/Trimestrale) (Facoltativo)"):
    update_file = st.file_uploader("Carica il file XML di aggiornamento", type=["xml"])

st.divider()
st.markdown("### 3️⃣ Periodo da Analizzare")
col1, col2 = st.columns(2)
with col1:
    data_inizio = st.text_input("Data Inizio", value="Da file Project", max_chars=20)
with col2:
    data_fine = st.text_input("Data Fine", value="Da file Project", max_chars=20)

st.divider()
st.markdown("### 4️⃣ Elementi da Analizzare")

col1, col2 = st.columns(2)
with col1:
    curva_sil = st.checkbox("Curva SIL")
    manodopera = st.checkbox("Manodopera")
with col2:
    mezzi = st.checkbox("Mezzi")
    avanzamento = st.checkbox("% Avanzamento Attività")

analisi_scelte = any([curva_sil, manodopera, mezzi, avanzamento])

st.divider()
colA, colB = st.columns([3, 1])
colB.button("🔄 Refresh", key="refresh_button", on_click=lambda: st.rerun())
run_analysis = colA.button("🚀 Avvia Analisi", disabled=not analisi_scelte)

# Variabili di log
log_text = ""
show_log = False

if run_analysis:
    st.session_state.first_run = False
    if not baseline_file:
        st.error("⚠️ Carica almeno il file principale (.xml)")
    else:
        with st.spinner("Analisi in corso..."):
            progress_text = "Analisi dei dati in corso..."
            progress_bar = st.progress(0, text=progress_text)

            for percent in range(0, 101, 25):
                time.sleep(0.2)
                progress_bar.progress(percent, text=f"{progress_text} ({percent}%)")

            try:
                risultati, log_text = analizza_file_project(
                    baseline_file=baseline_file,
                    update_file=update_file,
                    opzioni={
                        "curva_sil": curva_sil,
                        "manodopera": manodopera,
                        "mezzi": mezzi,
                        "avanzamento": avanzamento
                    },
                    data_inizio=data_inizio,
                    data_fine=data_fine
                )

                st.success("✅ Analisi completata con successo!")
                st.dataframe(risultati, width="stretch")

                if log_text:
                    st.markdown("🔺 **Log analisi dettagliato disponibile**")
                    with st.expander("🩶 Log Analisi Dettagliata"):
                        st.info(log_text)

            except Exception as e:
                st.error(f"❌ Errore durante l’analisi: {e}")
                st.markdown("🔺 **Log analisi dettagliato disponibile**")
                with st.expander("🩶 Log Analisi Dettagliata"):
                    st.code(str(e))
