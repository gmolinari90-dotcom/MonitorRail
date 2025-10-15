import streamlit as st
import subprocess
import pandas as pd
import os
import time

# ===========================================================
# MONITOR RAIL - INTERFACCIA STREAMLIT
# ===========================================================

st.set_page_config(page_title="MonitorRail Control Center", layout="wide")
st.title("🚄 MonitorRail - Centrale di Controllo")

# Sidebar
st.sidebar.header("⚙️ Parametri di Analisi")
project_file = st.sidebar.file_uploader("Carica file di Project (formato .xml o .mpp)", type=["xml", "mpp"])
progress_file = st.sidebar.file_uploader("Carica file Project aggiornato con avanzamento (facoltativo)", type=["xml", "mpp"])

st.sidebar.markdown("ℹ️ Se non selezioni le date, verrà analizzato l'intero progetto")

def default_start_date():
    return None

def default_end_date():
    return None

start_date = st.sidebar.date_input("Data inizio analisi (gg/mm/aaaa)", value=default_start_date())
end_date = st.sidebar.date_input("Data fine analisi (gg/mm/aaaa)", value=default_end_date())

float_threshold = st.sidebar.slider("Margine di flessibilità (giorni)", 0, 30, 5)

run_analysis = st.sidebar.button("▶️ Avvia Analisi")

# Output Directory
output_dir = "output_monitorrail"
os.makedirs(output_dir, exist_ok=True)

# Sezione Info/Guida secondaria
with st.expander("ℹ️ Info / Guida Rapida", expanded=False):
    st.markdown("""
    ### Guida Rapida
    1️⃣ Carica il file di Project (.xml esportato o .mpp originale)
    2️⃣ (Facoltativo) Carica un secondo file Project aggiornato con l'avanzamento attività.
    3️⃣ Seleziona il periodo e la soglia del margine di flessibilità.
       - Se non selezioni le date, verrà analizzato l'intero progetto.
    4️⃣ Clicca **Avvia Analisi** per generare i grafici e gli alert.
    5️⃣ I risultati saranno mostrati qui e salvati in `output_monitorrail/`.
    """)

# ===========================================================
# Analisi
# ===========================================================
if run_analysis:
    if project_file is None:
        st.warning("⚠️ Carica almeno un file Project (.xml o .mpp) per avviare l'analisi.")
    else:
        st.info("🔍 Analisi in corso... Attendere il completamento.")

        # Barra di avanzamento simulata
        progress_text = "Elaborazione dati..."
        progress_bar = st.progress(0, text=progress_text)
        for i in range(100):
            time.sleep(0.05)
            progress_bar.progress(i + 1, text=f"Elaborazione dati... {i + 1}% completato")

        # Controllo tipo file
        if project_file.name.endswith('.mpp'):
            st.warning("📁 Il file .mpp non può essere letto direttamente. Apri il file in Microsoft Project e usa **File > Esporta > XML** per salvarlo in formato compatibile.")
        else:
            # Preparazione parametri date
            start_param = start_date.strftime('%d/%m/%Y') if start_date else 'auto'
            end_param = end_date.strftime('%d/%m/%Y') if end_date else 'auto'

            # Esecuzione motore principale
            cmd = [
                "python", "MonitorRail_MVP.py",
                f"--project={project_file.name if project_file else ''}",
                f"--progress={progress_file.name if progress_file else ''}",
                f"--start={start_param}",
                f"--end={end_param}",
                f"--float-threshold={float_threshold}"
            ]

            with open(os.path.join(output_dir, "run_log.txt"), "w") as log:
                process = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, text=True)

            progress_bar.progress(100, text="Analisi completata ✅")
            st.success("Analisi completata con successo!")

            # Sezione Risultati
            st.header("📊 Risultati Analisi")

            # Alert attività critiche
            alert_path = os.path.join(output_dir, "summary_alerts.csv")
            if os.path.exists(alert_path):
                st.subheader("🚨 Alert Attività Critiche e Sub-Critiche")
                df_alert = pd.read_csv(alert_path)
                st.dataframe(df_alert, use_container_width=True)
                st.download_button("⬇️ Scarica CSV", data=df_alert.to_csv(index=False), file_name="summary_alerts.csv", mime="text/csv")

            # Mezzi distinti
            mezzi_path = os.path.join(output_dir, "mezzi_distinti.csv")
            if os.path.exists(mezzi_path):
                st.subheader("🚜 Mezzi distinti per tipologia")
                df_mezzi = pd.read_csv(mezzi_path)
                st.dataframe(df_mezzi, use_container_width=True)
                st.download_button("⬇️ Scarica CSV", data=df_mezzi.to_csv(index=False), file_name="mezzi_distinti.csv", mime="text/csv")

            # Curva SIL
            sil_path = os.path.join(output_dir, "curva_SIL.png")
            if os.path.exists(sil_path):
                st.subheader("📈 Curva di Produzione SIL")
                st.image(sil_path)
                with open(sil_path, "rb") as f:
                    st.download_button("⬇️ Scarica PNG", data=f, file_name="curva_SIL.png", mime="image/png")

            # Diagramma reticolare
            diagram_path = os.path.join(output_dir, "diagramma_reticolare.png")
            if os.path.exists(diagram_path):
                st.subheader("🔗 Diagramma Reticolare (Percorso Critico)")
                st.image(diagram_path)
                with open(diagram_path, "rb") as f:
                    st.download_button("⬇️ Scarica PNG", data=f, file_name="diagramma_reticolare.png", mime="image/png")

st.sidebar.markdown("---")
st.sidebar.caption("💡 MonitorRail v2.3 - Analisi avanzata dei programmi lavori ferroviari.")
