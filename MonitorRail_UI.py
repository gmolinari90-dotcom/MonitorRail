import streamlit as st
import pandas as pd
from MonitorRail_MVP import analizza_file_project

st.set_page_config(page_title="MonitorRail - Centrale di Controllo", layout="centered")

st.title("🚄 MonitorRail - Centrale di Controllo")
st.markdown("---")

if "first_run" not in st.session_state:
    st.session_state.first_run = True

# === 1. File Project Principale (Baseline) ===
st.subheader("1️⃣ Primo File Project (Baseline)")
baseline_file = st.file_uploader("Carica file XML esportato da Microsoft Project", type=["xml"])

# === 2. Secondo File Project (Aggiornamento) (Facoltativo) ===
with st.expander("2️⃣ Secondo File Project (Aggiornamento Mensile/Trimestrale) (Facoltativo)"):
    avanzamento_file = st.file_uploader("Carica file XML aggiornato", type=["xml"])

# === 3. Periodo da Analizzare ===
st.subheader("3️⃣ Periodo da Analizzare")
col1, col2 = st.columns(2)
with col1:
    start_date = st.text_input("Data Inizio", "Da file Project", placeholder="gg/mm/aaaa")
with col2:
    end_date = st.text_input("Data Fine", "Da file Project", placeholder="gg/mm/aaaa")

# === 4. Elementi da Analizzare ===
st.subheader("4️⃣ Elementi da Analizzare")
col1, col2 = st.columns(2)
with col1:
    analisi_sil = st.checkbox("Curva SIL")
    analisi_mezzi = st.checkbox("Mezzi")
with col2:
    analisi_manodopera = st.checkbox("Manodopera")
    analisi_percentuale = st.checkbox("Avanzamento Attività")

# === Bottone Avvio / Refresh ===
st.markdown("---")
colA, colB = st.columns(2)

if not any([analisi_sil, analisi_manodopera, analisi_mezzi, analisi_percentuale]):
    colA.button("🚫 Seleziona almeno un'analisi", disabled=True)
else:
    run_analysis = colA.button("▶️ Avvia Analisi")
    if run_analysis:
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

            st.subheader("📜 Log Analisi")
            for r in risultati["log"]:
                st.markdown(f"- {r}")

            if not risultati["df_finale"].empty:
                st.subheader("📊 Tabella Attività Estratte")
                st.dataframe(risultati["df_finale"], use_container_width=True)
                csv_data = risultati["csv_buffers"]["attività"].getvalue()
                st.download_button("⬇️ Scarica CSV", data=csv_data, file_name="attivita_estratte.csv", mime="text/csv")
            else:
                st.warning("⚠️ Nessuna attività trovata.")

colB.button("🔄 Refresh", on_click=lambda: st.experimental_rerun())
