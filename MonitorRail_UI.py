import streamlit as st
from MonitorRail_MVP import analizza_file_project, estrai_date_progetto
import pandas as pd

st.set_page_config(page_title="MonitorRail Control Center", layout="wide")
st.title("🚄 MonitorRail - Centrale di Controllo")

if 'first_run' not in st.session_state:
    st.session_state.first_run = True

st.sidebar.header("⚙️ Parametri di Analisi")

# --- Input file baseline ---
baseline_file = st.sidebar.file_uploader(
    "Carica il file Project principale (baseline) (.xml)", type=["xml"]
)

# --- Input file opzionale (tendina) ---
with st.sidebar.expander("Secondo file Project aggiornato (facoltativo)"):
    avanzamento_file = st.file_uploader(
        "Carica secondo file Project aggiornato (.xml)", type=["xml"]
    )

# --- Estrazione date default dal progetto ---
if baseline_file:
    start_def, end_def = estrai_date_progetto(baseline_file)
else:
    start_def, end_def = pd.Timestamp.now(), pd.Timestamp.now()

# --- Filtri temporali con formato gg/mm/aaaa ---
start_date = st.sidebar.date_input("Data inizio analisi", value=start_def)
end_date = st.sidebar.date_input("Data fine analisi", value=end_def)

# --- Checkbox analisi ---
st.sidebar.markdown("### Seleziona analisi da eseguire")
analisi_sil = st.sidebar.checkbox("Curva SIL")
analisi_manodopera = st.sidebar.checkbox("Manodopera")
analisi_mezzi = st.sidebar.checkbox("Mezzi")
analisi_percentuale = st.sidebar.checkbox("% Avanzamento attività")

# --- Pulsanti ---
run_analysis = st.sidebar.button("▶️ Avvia Analisi")
reset_analysis = st.sidebar.button("🔄 Refresh / Riavvia Analisi")

if reset_analysis:
    st.session_state.first_run = True
    st.experimental_rerun()

if run_analysis:
    st.session_state.first_run = False

    if not baseline_file:
        st.error("Devi caricare almeno il file Project principale (.xml)")
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

        # Mostra log
        with st.expander("📋 Log Verifica File", expanded=True):
            for msg in risultati['log']:
                st.text(msg)

        # Tabella finale
        st.subheader("📊 Tabella Attività")
        st.dataframe(risultati['df_finale'], use_container_width=True)

        # Download CSV per ogni analisi selezionata
        for key, buf in risultati.get('csv_buffers', {}).items():
            st.download_button(f"⬇️ Scarica CSV {key.upper()}", data=buf.getvalue(), file_name=f"{key}.csv")

        # Visualizzazione grafico avanzamento
        if 'percentuale' in risultati.get('figures', {}):
            st.subheader("📈 Grafico % Avanzamento Attività")
            st.image(risultati['figures']['percentuale'].getvalue())
        elif analisi_percentuale:
            st.warning("⚠️ Percentuale completamento non disponibile")
            
# Guida rapida solo al primo avvio
if st.session_state.first_run:
    st.markdown("""
    ### 🧭 Guida Rapida
    - Carica il file di Project principale (.xml)
    - (Facoltativo) Apri il menu tendina e carica un secondo file Project aggiornato
    - Seleziona il periodo se vuoi analizzare un intervallo specifico (default: intero progetto)
    - Seleziona le tipologie di analisi da eseguire
    - Clicca **Avvia Analisi** per generare grafici e CSV
    """)
