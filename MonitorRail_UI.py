import streamlit as st
import pandas as pd
import os

# ==============================================
# MONITORRAIL - CENTRALE DI CONTROLLO
# ==============================================
st.set_page_config(page_title="MonitorRail Control Center", layout="wide")
st.title("🚄 MonitorRail - Centrale di Controllo Cantieri Ferroviari")
st.markdown("### Sistema integrato per il monitoraggio fisico ed economico dei lavori")

st.sidebar.header("⚙️ Pannello di Configurazione")

# --- SEZIONE UPLOAD FILE ---
st.markdown("## 📂 Caricamento dei Dati")

col1, col2, col3 = st.columns(3)

with col1:
    project_file = st.file_uploader(
        "📘 Carica il file di **MS Project** (.xml o .csv)", 
        type=["xml", "csv"], 
        key="proj"
    )

with col2:
    progress_file = st.file_uploader(
        "📊 Carica il file di **avanzamento fisico** (.csv o .xlsx)", 
        type=["csv", "xlsx"], 
        key="prog"
    )

with col3:
    mezzi_file = st.file_uploader(
        "🚜 Carica il file **mezzi e attrezzature** (facoltativo)", 
        type=["csv", "xlsx"], 
        key="mezzi"
    )

st.divider()

# --- SELEZIONE PARAMETRI ---
st.markdown("## ⏱️ Parametri di Analisi")

colA, colB, colC = st.columns(3)

with colA:
    start_date = st.date_input("Data inizio periodo di analisi")
with colB:
    end_date = st.date_input("Data fine periodo di analisi")
with colC:
    float_threshold = st.slider("Margine di flessibilità totale (giorni)", 0, 30, 5)

st.divider()

# --- PULSANTE AVVIO ANALISI ---
st.markdown("## 🚀 Avvio Analisi")

if st.button("▶️ Esegui Analisi"):
    if not project_file:
        st.warning("Devi caricare almeno il file di MS Project.")
    else:
        st.success("Analisi avviata correttamente ✅")
        st.info("⏳ Elaborazione in corso... (i risultati saranno mostrati qui sotto)")

        # QUI andrà inserita la logica del motore principale (MonitorRail_MVP.py)
        st.write("📈 Analisi simulata: risultati di esempio...")
        st.dataframe(pd.DataFrame({
            "Attività": ["Scavo", "Armamento", "Opere Civili"],
            "Avanzamento (%)": [45, 20, 60],
            "Flessibilità (giorni)": [0, 3, 7]
        }))

        st.markdown("### 📊 Curva SIL (esempio)")
        st.line_chart(pd.DataFrame({
            "Data": pd.date_range(start="2025-01-01", periods=5, freq="M"),
            "Avanzamento SIL (%)": [5, 18, 37, 55, 72]
        }).set_index("Data"))

st.sidebar.markdown("---")
st.sidebar.caption("💡 MonitorRail v1.0 - powered by Streamlit Cloud")

