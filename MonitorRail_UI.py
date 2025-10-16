import streamlit as st
import pandas as pd
import os
from MonitorRail_MVP import analizza_file_project_mpp

st.set_page_config(page_title="MonitorRail", layout="wide")
st.title("🚄 MonitorRail – Centrale di Controllo MPP")

st.markdown("**Versione con lettura diretta del file Microsoft Project (.MPP)**")

st.divider()
st.markdown("### 1️⃣ Caricamento File Project (.MPP)")
mpp_file = st.file_uploader("Carica file MPP", type=["mpp"])

st.divider()
st.markdown("### 2️⃣ Periodo da Analizzare")
col1, col2 = st.columns(2)
with col1:
    data_inizio = st.text_input("Data Inizio", value="Da file Project")
with col2:
    data_fine = st.text_input("Data Fine", value="Da file Project")

st.divider()
st.markdown("### 3️⃣ Elementi da Analizzare")
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

# --- Interroga Project ---
st.divider()
st.markdown("### 📅 Interroga Project")
if mpp_file:
    if st.button("🔍 Estrai attività previste nel periodo"):
        temp_path = os.path.join(os.getcwd(), "temp_file.mpp")
        with open(temp_path, "wb") as f:
            f.write(mpp_file.getvalue())

        df, risultati = analizza_file_project_mpp(
            mpp_file_path=temp_path,
            opzioni={
                "curva_sil": curva_sil,
                "manodopera": manodopera,
                "mezzi": mezzi,
                "avanzamento": avanzamento
            },
            data_inizio=data_inizio,
            data_fine=data_fine
        )

        st.success(f"✅ Totale attività trovate: {len(df)}")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Scarica attività (CSV)", csv, "attività_filtrate.csv", "text/csv")
else:
    st.info("Carica un file .MPP per iniziare l'analisi.")
