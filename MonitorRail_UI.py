import streamlit as st
from MonitorRail_MVP import analizza_file_project, estrai_date_progetto
import pandas as pd

# --- Configurazione pagina ---
st.set_page_config(page_title="MonitorRail Control Center", layout="wide")
st.title("🚄 MonitorRail - Centrale di Controllo")

if 'first_run' not in st.session_state:
    st.session_state.first_run = True

# ====================================================
# SIDEBAR: Parametri Analisi strutturati a capitoli
# ====================================================
st.sidebar.header("⚙️ Parametri di Analisi")

# ---------- 1. Primo File Project (Baseline) ----------
st.sidebar.subheader("1️⃣ Primo File Project (Baseline)")
baseline_file = st.sidebar.file_uploader(
    "Carica file Project principale (.xml)", type=["xml"]
)

# ---------- 2. Secondo File Project (Aggiornamento) ----------
st.sidebar.subheader("2️⃣ Secondo File Project (Aggiornamento Mensile/Trimestrale) (Facoltativo)")
with st.sidebar.expander("Carica secondo file Project (facoltativo)"):
    avanzamento_file = st.file_uploader(
        "Secondo file Project aggiornato (.xml)", type=["xml"]
    )

# ---------- 3. Periodo da Analizzare ----------
st.sidebar.subheader("3️⃣ Periodo da Analizzare")
if baseline_file:
    start_def, end_def = estrai_date_progetto(baseline_file)
else:
    start_def, end_def = pd.Timestamp.now(), pd.Timestamp.now()

start_date = st.sidebar.date_input(
    "Data inizio", value=start_def, key="start_date"
)
end_date = st.sidebar.date_input(
    "Data fine", value=end_def, key="end_date"
)

# Se l'utente non modifica, testo "da programma"
if start_date == start_def:
    start_display = "da programma"
else:
    start_display = start_date.strftime("%d/%m/%Y")

if end_date == end_def:
    end_display = "da programma"
else:
    end_display = end_date.strftime("%d/%m/%Y")

st.sidebar.markdown(f"**Periodo selezionato:** {start_display} → {end_display}")

# ---------- 4. Elementi da Analizzare ----------
st.sidebar.subheader("4️⃣ Elementi da Analizzare")
analisi_sil = st.sidebar.checkbox("📊 Curva SIL")
analisi_manodopera = st.sidebar.checkbox("👷 Manodopera")
analisi_mezzi = st.sidebar.checkbox("🚜 Mezzi")
analisi_percentuale = st.sidebar.checkbox("📈 % Avanzamento attività")

# ====================================================
# Pulsanti separati
# ====================================================
st.sidebar.markdown("---")
col1, col2 = st.sidebar.columns(2)
with col1:
    run_analysis = st.button("▶️ Avvia Analisi", key="run", use_container_width=True)
with col2:
    reset_analysis = st.button("🔄 Refresh / Riavvia", key="reset", use_container_width=True)

# ====================================================
# Funzioni pulsanti
# ====================================================
if reset_analysis:
    st.session_state.first_run = True
    st.experimental_rerun()

if run_analysis:
    st.session_state.first_run = False

    if not baseline_file:
        st.error("⚠️ Devi caricare almeno il file Project principale (.xml)")
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

        # ---------- Log Verifica File ----------
        with st.expander("📋 Log Verifica File", expanded=True):
            for msg in risultati['log']:
                st.text(msg)

        # ---------- Tabella Attività ----------
        st.subheader("📊 Tabella Attività")
        st.dataframe(risultati['df_finale'], use_container_width=True)

        # ---------- Download CSV per analisi selezionata ----------
        for key, buf in risultati.get('csv_buffers', {}).items():
            st.download_button(
                f"⬇️ Scarica CSV {key.upper()}",
                data=buf.getvalue(),
                file_name=f"{key}.csv"
            )

        # ---------- Grafico percentuale avanzamento ----------
        if 'percentuale' in risultati.get('figures', {}):
            st.subheader("📈 Grafico % Avanzamento Attività")
            st.image(risultati['figures']['percentuale'].getvalue())
        elif analisi_percentuale:
            st.warning("⚠️ Percentuale completamento non disponibile")

# ====================================================
# Guida rapida solo al primo avvio
# ====================================================
if st.session_state.first_run:
    st.markdown("""
    ### 🧭 Guida Rapida
    1️⃣ Carica il file di Project principale (.xml)  
    2️⃣ (Facoltativo) Apri il menu tendina e carica un secondo file Project aggiornato  
    3️⃣ Seleziona il periodo se vuoi analizzare un intervallo specifico (default: intero progetto)  
    4️⃣ Seleziona le tipologie di analisi da eseguire  
    5️⃣ Clicca **Avvia Analisi** per generare grafici e CSV
    """)
