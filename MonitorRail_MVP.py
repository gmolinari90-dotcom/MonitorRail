import xml.etree.ElementTree as ET
import pandas as pd
import io
from datetime import datetime

def estrai_date_progetto(xml_file):
    """Estrae le date di inizio/fine del progetto"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        ns = {'ns': 'http://schemas.microsoft.com/project'}

        start = root.find('.//ns:StartDate', ns)
        finish = root.find('.//ns:FinishDate', ns)

        start_date = pd.to_datetime(start.text) if start is not None else pd.Timestamp.now()
        finish_date = pd.to_datetime(finish.text) if finish is not None else pd.Timestamp.now()

        return start_date, finish_date
    except Exception:
        return pd.Timestamp.now(), pd.Timestamp.now()


def analizza_file_project(baseline_file, avanzamento_file=None,
                          start_date=None, end_date=None,
                          analisi_sil=False, analisi_manodopera=False,
                          analisi_mezzi=False, analisi_percentuale=False):

    log = []
    df_finale = pd.DataFrame()
    csv_buffers = {}

    try:
        # 1️⃣ Legge il file XML caricato da Streamlit (BytesIO)
        xml_bytes = baseline_file.read()
        tree = ET.parse(io.BytesIO(xml_bytes))
        root = tree.getroot()
        ns = {'ns': 'http://schemas.microsoft.com/project'}
        log.append(f"✅ File XML caricato correttamente: {baseline_file.name}")

        # 2️⃣ Estrae le attività principali
        tasks = []
        for t in root.findall('.//ns:Task', ns):
            name = t.find('ns:Name', ns)
            start = t.find('ns:Start', ns)
            finish = t.find('ns:Finish', ns)
            duration = t.find('ns:Duration', ns)
            percent_complete = t.find('ns:PercentComplete', ns)

            if name is not None:
                tasks.append({
                    "Nome": name.text,
                    "Inizio": start.text if start is not None else None,
                    "Fine": finish.text if finish is not None else None,
                    "Durata": duration.text if duration is not None else None,
                    "% Completamento": percent_complete.text if percent_complete is not None else None
                })

        if len(tasks) == 0:
            log.append("⚠️ Nessuna attività trovata nel file XML.")
        else:
            log.append(f"📋 Totale attività lette: {len(tasks)}")

        df_finale = pd.DataFrame(tasks)

        # 3️⃣ Filtro periodo
        if start_date and "Da file" not in start_date:
            try:
                start_dt = datetime.strptime(start_date, "%d/%m/%Y")
                end_dt = datetime.strptime(end_date, "%d/%m/%Y")
                df_finale["Inizio_dt"] = pd.to_datetime(df_finale["Inizio"], errors="coerce")
                df_finale = df_finale[(df_finale["Inizio_dt"] >= start_dt) & (df_finale["Inizio_dt"] <= end_dt)]
                log.append(f"📆 Filtro applicato: {start_date} → {end_date}")
            except Exception:
                log.append("⚠️ Formato date non valido, salto il filtro temporale.")

        # 4️⃣ Analisi richieste
        if analisi_sil:
            log.append("🔹 Analisi Curva SIL richiesta — (simulazione placeholder).")
        if analisi_manodopera:
            log.append("🔹 Analisi Manodopera richiesta — (simulazione placeholder).")
        if analisi_mezzi:
            log.append("🔹 Analisi Mezzi richiesta — (simulazione placeholder).")
        if analisi_percentuale:
            log.append("🔹 Analisi Avanzamento Attività richiesta — (simulazione placeholder).")

        # 5️⃣ CSV export in memoria
        if not df_finale.empty:
            buffer = io.StringIO()
            df_finale.to_csv(buffer, index=False)
            csv_buffers["attività"] = buffer

    except Exception as e:
        log.append(f"❌ Errore durante analisi: {e}")

    return {"log": log, "df_finale": df_finale, "csv_buffers": csv_buffers}
