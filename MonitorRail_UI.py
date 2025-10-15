import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import tempfile
import os

# ===========================================================
# MONITOR RAIL - CENTRALE DI CONTROLLO
# ===========================================================
st.set_page_config(page_title="MonitorRail Control Center", layout="wide")
st.title("🚄 MonitorRail - Centrale di Controllo")

st.markdown("""
Benvenuto nella **Centrale di Controllo MonitorRail**  
Gestisci il confronto tra la **baseline di progetto** e gli **avanzamenti lavori** esportati da MS Project.
""")

# ===========================================================
# SEZIONE 1 - CARICAMENTO FILE BASELINE
# ===========================================================
st.header("📘 Programma Lavori - Baseline")
baseline_file = st.file_uploader(
    "Carica il file di baseline (.mpp / .xml / .csv)",
    type=["mpp", "xml", "csv"],
    key="baseline"
)

# ===========================================================
# SEZIONE 2 - CARICAMENTO FILE AVANZAMENTO (FACOLTATIVO)
# ===========================================================
st.header("📗 Programma Lavori - Avanzamento (facoltativo)")
progress_file = st.file_uploader(
    "Carica il file di avanzamento (.mpp / .xml / .csv)",
    type=["mpp", "xml", "csv"],
    key="progress"
)

# ===========================================================
# SEZIONE 3 - PARAMETRI E AVVIO ANALISI
# ===========================================================
st.header("⚙️ Parametri di Analisi")
float_threshold = st.slider("Margine di flessibilità (giorni)", 0, 30, 5)
start_analysis = st.button("▶️ Avvia analisi del programma lavori")

# ===========================================================
# FUNZIONE DI LETTURA XML COMPLETA
# ===========================================================
def parse_xml(file):
    try:
        tree = ET.parse(file)
        root = tree.getroot()
        tasks = []
        for task in root.findall(".//Task"):
            data = {
                "ID": task.findtext("ID"),
                "WBS": task.findtext("WBS"),
                "Nome Attività": task.findtext("Name"),
                "Durata": task.findtext("Duration"),
                "Data Inizio": task.findtext("Start"),
                "Data Fine": task.findtext("Finish"),
                "% Completamento": task.findtext("PercentComplete"),
                "Predecessori": task.findtext("PredecessorLink/PredecessorUID"),
                "Assegnazioni Risorse": task.findtext("ResourceNames"),
                "Costo Totale": task.findtext("Cost"),
            }
            if data["Nome Attività"]:
                tasks.append(data)
        return pd.DataFrame(tasks)
    except Exception as e:
        st.error(f"Errore nel parsing XML: {e}")
        return None

# ===========================================================
# ESECUZIONE ANALISI
# ===========================================================
if start_analysis:
    if not baseline_file:
        st.error("⚠️ Carica almeno il file di baseline per procedere.")
    else:
        st.info("⏳ Analisi in corso...")

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(baseline_file.getbuffer())
            baseline_path = tmp.name

        df_baseline = None

        # --- Caso .MPP (non leggibile diretto) ---
        if baseline_file.name.endswith(".mpp"):
            st.warning("""
            ⚠️ Il formato `.mpp` non può essere letto direttamente per motivi tecnici.  
            Per procedere, esporta il file da **Microsoft Project** seguendo questi passaggi:

            1️⃣ Apri il tuo file `.mpp` in Microsoft Project.  
            2️⃣ Vai su **File → Salva con nome → Sfoglia**  
            3️⃣ Nel campo **Tipo file**, scegli: `XML Data (*.xml)`  
            4️⃣ Assegna un nome al file (es. `programma_baseline.xml`) e salvalo.  
            5️⃣ Ricarica qui il nuovo file `.xml`.

            💡 *Suggerimento:* il file XML mantiene WBS, durate, legami, risorse e costi senza perdita di dati.
            """)
        # --- Caso .XML ---
        elif baseline_file.name.endswith(".xml"):
            df_baseline = parse_xml(baseline_path)
        # --- Caso .CSV ---
        elif baseline_file.name.endswith(".csv"):
            df_baseline = pd.read_csv(baseline_path)

        if df_baseline is not None and not df_baseline.empty:
            st.success("✅ File baseline letto con successo.")
            st.dataframe(df_baseline.head(30), use_container_width=True)
            csv_path = os.path.join(tempfile.gettempdir(), "baseline_estratta.csv")
            df_baseline.to_csv(csv_path, index=False)
            st.download_button("⬇️ Scarica CSV estratto", data=open(csv_path, "rb").read(),
                               file_name="baseline_estratta.csv", mime="text/csv")

        # --- File di avanzamento (opzionale) ---
        if progress_file:
            with tempfile.NamedTemporaryFile(delete=False) as tmp2:
                tmp2.write(progress_file.getbuffer())
                progress_path = tmp2.name

            df_progress = None
            if progress_file.name.endswith(".xml"):
                df_progress = parse_xml(progress_path)
            elif progress_file.name.endswith(".csv"):
                df_progress = pd.read_csv(progress_path)
            elif progress_file.name.endswith(".mpp"):
                st.warning("⚠️ Esporta anche il file di avanzamento in formato `.xml` per poterlo leggere correttamente.")

            if df_progress is not None and not df_progress.empty:
                st.success("✅ File avanzamento letto con successo.")
                st.dataframe(df_progress.head(30), use_container_width=True)

# ===========================================================
# FOOTER
# ===========================================================
st.markdown("---")
st.caption("💡 MonitorRail v2.1 - Analisi avanzata dei programmi lavori ferroviari.")
