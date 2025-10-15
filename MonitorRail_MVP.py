import streamlit as st
import pandas as pd
from io import BytesIO
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

st.set_page_config(page_title="MonitorRail Control Center", layout="wide")
st.title("🚄 MonitorRail - Centrale di Controllo")

st.sidebar.header("⚙️ Parametri di Analisi")

# --- Input file ---
mpp_file = st.sidebar.file_uploader("Carica il file Project principale (.xml)", type=["xml"])
progress_file = st.sidebar.file_uploader("(Facoltativo) Carica secondo file Project aggiornato (.xml)", type=["xml"])

# --- Filtri temporali ---
start_date = st.sidebar.date_input("Data inizio analisi")
end_date = st.sidebar.date_input("Data fine analisi")
float_threshold = st.sidebar.slider("Margine di flessibilità (giorni)", 0, 30, 5)

run_analysis = st.sidebar.button("▶️ Avvia Analisi")

if run_analysis:
    if not mpp_file:
        st.error("Devi caricare almeno un file Project .xml per procedere")
    else:
        log_messages = []
        try:
            # ================================
            # Step 1: Verifica caricamento file
            # ================================
            tree = ET.parse(mpp_file)
            root = tree.getroot()
            log_messages.append(f"File XML caricato correttamente: {mpp_file.name}")

            tasks = []
            for t in root.findall('.//Task'):
                uid = t.find('UID').text if t.find('UID') is not None else None
                name = t.find('Name').text if t.find('Name') is not None else None
                start = t.find('Start').text if t.find('Start') is not None else None
                finish = t.find('Finish').text if t.find('Finish') is not None else None
                percent = t.find('PercentComplete').text if t.find('PercentComplete') is not None else None
                total_slack = t.find('TotalSlack').text if t.find('TotalSlack') is not None else None

                tasks.append({
                    'UID': uid,
                    'Name': name,
                    'Start': start,
                    'Finish': finish,
                    'PercentComplete': percent,
                    'TotalSlack': total_slack
                })

            df_tasks = pd.DataFrame(tasks)

            # Verifica campi mancanti
            missing_fields = df_tasks.isnull().sum()
            log_messages.append(f"Totale attività lette: {len(df_tasks)}")
            for col, val in missing_fields.items():
                if val > 0:
                    log_messages.append(f"⚠️ {val} valori mancanti nella colonna '{col}'")

            # ================================
            # Step 2: Mostra log e tabella preliminare
            # ================================
            with st.expander("📋 Log Verifica File", expanded=True):
                for msg in log_messages:
                    st.text(msg)

            st.subheader("📊 Tabella preliminare attività")
            st.dataframe(df_tasks, use_container_width=True)

            csv_buffer = BytesIO()
            df_tasks.to_csv(csv_buffer, index=False)
            st.download_button("⬇️ Scarica attività preliminare CSV", data=csv_buffer.getvalue(), file_name="attivita_preliminare.csv")

            # ================================
            # Step 3: Grafico avanzamento percentuale
            # ================================
            if 'PercentComplete' in df_tasks.columns and df_tasks['PercentComplete'].notnull().any():
                df_plot = df_tasks.dropna(subset=['PercentComplete'])
                df_plot['PercentComplete'] = df_plot['PercentComplete'].astype(float)

                fig, ax = plt.subplots()
                ax.bar(df_plot['Name'], df_plot['PercentComplete'], color='skyblue')
                ax.set_ylabel('Percentuale completamento')
                ax.set_xlabel('Attività')
                ax.set_xticklabels(df_plot['Name'], rotation=90)
                st.subheader("📈 Avanzamento Percentuale Attività")
                st.pyplot(fig)

                img_buffer = BytesIO()
                fig.savefig(img_buffer, format='png', bbox_inches='tight')
                st.download_button("⬇️ Scarica grafico avanzamento", data=img_buffer.getvalue(), file_name="grafico_avanzamento.png")
            else:
                st.warning("⚠️ Percentuale completamento non disponibile per le attività.")

            st.success("Analisi completata con successo ✅")

        except ET.ParseError:
            st.error("Errore: il file XML non è leggibile o è corrotto.")
        except Exception as e:
            st.error(f"Errore inatteso durante l'analisi: {e}")

st.sidebar.markdown("---")
st.sidebar.caption("💡 MonitorRail v1.0 - sviluppato per il controllo avanzato dei cantieri ferroviari.")

# ===========================================================
# GUIDA RAPIDA secondaria
# ===========================================================
st.markdown("""
### 🧭 Guida Rapida
- Carica il file di Project principale (.xml)
- (Facoltativo) Carica un secondo file Project aggiornato con l'avanzamento attività
- Seleziona il periodo e la soglia del margine di flessibilità
  - Se non selezioni le date, verrà analizzato l'intero progetto
- Clicca **Avvia Analisi** per generare i grafici e gli alert
- I risultati saranno mostrati direttamente nella UI e scaricabili come CSV o PNG
""")
