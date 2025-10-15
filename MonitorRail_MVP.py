import xml.etree.ElementTree as ET
import pandas as pd
import io
from datetime import datetime

def get_namespace(element):
    """Estrae automaticamente il namespace XML del file Project"""
    if element.tag[0] == "{":
        return element.tag[1:].split("}")[0]
    return ""

def estrai_date_progetto(xml_file):
    """Estrae le date inizio/fine dal file XML"""
    try:
        xml_bytes = xml_file.read()
        tree = ET.parse(io.BytesIO(xml_bytes))
        root = tree.getroot()
        ns = {'ns': get_namespace(root)}

        start = root.find('.//ns:StartDate', ns)
        finish = root.find('.//ns:FinishDate', ns)

        start_date = pd.to_datetime(start.text) if start is not None else pd.Timestamp.now()
        finish_date = pd.to_datetime(finish.text) if finish is not None else pd.Timestamp.now()

        return start_date, finish_date
    except Exception as e:
        print(f"[Errore estrai_date_progetto] {e}")
        return pd.Timestamp.now(), pd.Timestamp.now()

def analizza_file_project(baseline_file, avanzamento_file=None,
                          start_date=None, end_date=None,
                          analisi_sil=False, analisi_manodopera=False,
                          analisi_mezzi=False, analisi_percentuale=False):

    log = []
    df_finale = pd.DataFrame()
    csv_buffers = {}

    try:
        xml_bytes = baseline_file.read()
        tree = ET.parse(io.BytesIO(xml_bytes))
        root = tree.getroot()
        ns_uri = get_namespace(root)
        ns = {'ns': ns_uri}

        log.append(f"✅ File XML caricato correttamente: {baseline_file.name}")
        log.append(f"Namespace rilevato: {ns_uri}")

        # Estrai attività
        tasks = []
        for t in root.findall('.//ns:Task', ns):
            name = t.find('ns:Name', ns)
            start = t.find('ns:Start', ns)
            finish = t.find('ns:Finish', ns)
            duration = t.find('ns:Duration', ns)
            percent_complete = t.find('ns:PercentComplete', ns)

            if name is not None and name.text and "Project Summary" not in name.text:
                tasks.append({
                    "Nome": name.text,
                    "Inizio": start.text if start is not None else None,
                    "Fine": finish.text if finish is not None else None,
                    "Durata": duration.text if duration is not None else None,
                    "% Completamento": percent_complete.text if percent_complete is not None else None
                })

        if len(tasks) == 0:
            log.append("⚠️ Nessuna attività trovata nel file XML. Verifica l'esportazione da Project in formato XML (File → Salva con nome → XML).")
        else:
            log.append(f"📋 Totale attività lette: {len(tasks)}")

        df_finale = pd.DataFrame(tasks)

        # Filtro periodo
        if start_date and "Da file" not in start_date:
            try:
                start_dt = datetime.strptime(start_date, "%d/%m/%Y")
                end_dt = datetime.strptime(end_date, "%d/%m/%Y")
                df_finale["Inizio_dt"] = pd.to_datetime(df_finale["Inizio"], errors="coerce")
                df_finale = df_finale[(df_finale["Inizio_dt"] >= start_dt) & (df_finale["Inizio_dt"] <= end_dt)]
                log.append(f"📆 Filtro applicato: {start_date} → {end_date}")
            except Exception as e:
                log.append(f"⚠️ Errore filtro temporale: {e}")

        # Analisi richieste
        if analisi_sil:
            log.append("🔹 Analisi Curva SIL — simulazione placeholder.")
        if analisi_manodopera:
            log.append("🔹 Analisi Manodopera — simulazione placeholder.")
        if analisi_mezzi:
            log.append("🔹 Analisi Mezzi — simulazione placeholder.")
        if analisi_percentuale:
            log.append("🔹 Analisi Avanzamento — simulazione placeholder.")

        # CSV in memoria
        if not df_finale.empty:
            buffer = io.StringIO()
            df_finale.to_csv(buffer, index=False)
            csv_buffers["attività"] = buffer

    except Exception as e:
        log.append(f"❌ Errore durante l'analisi: {e}")

    return {"log": log, "df_finale": df_finale, "csv_buffers": csv_buffers}
