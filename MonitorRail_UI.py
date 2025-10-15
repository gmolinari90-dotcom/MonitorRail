import streamlit as st
from MonitorRail_MVP import analizza_file_project

st.set_page_config(page_title="MonitorRail Control Center", layout="wide")
st.title("🚄 MonitorRail - Centrale di Controllo")

# --- Sessione Streamlit ---
if 'first_run' not in st.session_state:
    st.session_state.first_run = True

st.sidebar.header("⚙️ Parametri di Analisi")

# --- Input file ---
baseline_file = st.sidebar.file_uploader(
    "Carica il file Project principale (baseline) (.xml)", type=["xml"])
avanzamento_file = st.sidebar.file_uploader(
    "(Facoltativo) Carica secondo file Project aggiornato (.xml)", type=["xml"])

# --- Filtri temporali ---
start_date = st.sidebar.date_input("Data inizio analisi")
end_date = st.sidebar.date_input("Data fine analisi")
float_threshold = st.sidebar.slider("Margine di flessibilità (giorni)", 0, 30, 5)

# --- Pulsanti ---
run_analysis = st.sidebar.button("▶️ Avvia Analisi")
reset_analysis = st.sidebar.button("🔄 Refresh / Riavvia Analisi")

if reset_analysis:
    st.session_state.first_run = True
    st.experimental_rerun()

if run_analysis:
    st.session_state.first_run = False

    if not baseline_file and not avanzamento_file:
        st.error("Devi caricare almeno un file Project .xml per procedere")
    else:
        risultati = analizza_file_project(
            baseline_file=baseline_file,
            avanzamento_file=avanzamento_file,
            start_date=start_date,
            end_date=end_date,
            float_threshold=float_threshold
        )

        # Mostra log
        with st.expander("📋 Log Verifica File", expanded=True):
            for msg in risultati['log']:
                st.text(msg)

        # Tabella attività
        st.subheader("📊 Tabella Attività")
        st.dataframe(risultati['df_tasks'], use_container_width=True)
        st.download_button(
            "⬇️ Scarica attività CSV",
            data=risultati['csv_buffer'].getvalue(),
            file_name="attivita_analisi.csv"
        )

        # Grafico PercentComplete
        if risultati['fig']:
            st.subheader("📈 Avanzamento Percentuale Attività")
            st.pyplot(risultati['fig'])
            st.download_button(
                "⬇️ Scarica grafico PNG",
                data=risultati['img_buffer'].getvalue(),
                file_name="grafico_avanzamento.png"
            )
        else:
            st.warning("⚠️ Percentuale completamento non disponibile per le attività.")

# Guida rapida solo se first_run
if st.session_state.first_run:
    st.markdown("""
    ### 🧭 Guida Rapida
    - Carica il file di Project principale (.xml)
    - (Facoltativo) Carica un secondo file Project aggiornato con l'avanzamento attività
    - Seleziona il periodo e la soglia del margine di flessibilità
      - Se non selezioni le date, verrà analizzato l'intero progetto
    - Clicca **Avvia Analisi** per generare i grafici e gli alert
    - I risultati saranno mostrati direttamente nella UI e scaricabili come CSV o PNG
    """)
