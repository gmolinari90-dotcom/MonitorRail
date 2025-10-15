import pandas as pd
import io
import xml.etree.ElementTree as ET

def estrai_date_progetto(xml_file):
    """Estrae data inizio e fine progetto dal file XML Project."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        ns = {'ns': root.tag.split('}')[0].strip('{')}

        start = root.find('ns:Project/ns:StartDate', ns)
        finish = root.find('ns:Project/ns:FinishDate', ns)

        start_date = pd.to_datetime(start.text) if start is not None else pd.Timestamp.now()
        end_date = pd.to_datetime(finish.text) if finish is not None else pd.Timestamp.now()

        return start_date, end_date
    except Exception:
        return pd.Timestamp.now(), pd.Timestamp.now()


def analizza_file_project(
    baseline_file,
    avanzamento_file=None,
    start_date=None,
    end_date=None,
    analisi_sil=False,
    analisi_manodopera=False,
    analisi_mezzi=False,
    analisi_percentuale=False
):
    """Analizza file Project XML e restituisce log, dataframe e CSV/grafici."""
    log = []
    df_finale = pd.DataFrame()
    csv_buffers = {}
    figures = {}

    try:
        # --- Caricamento file principale ---
        tree = ET.parse(baseline_file)
        root = tree.getroot()
        ns = {'ns': root.tag.split('}')[0].strip('{')}
        log.append(f"✅ File XML caricato: {baseline_file.name}")

        # --- Estrazione attività ---
        tasks = []
        for task in root.findall('ns:Tasks/ns:Task', ns):
            name = task.find('ns:Name', ns)
            start = task.find('ns:Start', ns)
            finish = task.find('ns:Finish', ns)
            percent = task.find('ns:PercentComplete', ns)

            if name is not None:
                tasks.append({
                    'Attività': name.text,
                    'Inizio': pd.to_datetime(start.text) if start is not None else None,
                    'Fine': pd.to_datetime(finish.text) if finish is not None else None,
                    '% Completamento': float(percent.text) if percent is not None else None
                })

        df_finale = pd.DataFrame(tasks)
        log.append(f"📄 Attività lette: {len(df_finale)}")

        # --- Gestione date personalizzate ---
        if start_date and end_date and start_date != "Da file Project" and end_date != "Da file Project":
            df_finale = df_finale[
                (df_finale['Inizio'] >= pd.to_datetime(start_date)) &
                (df_finale['Fine'] <= pd.to_datetime(end_date))
            ]
            log.append(f"📅 Analisi periodo: {start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')}")
        else:
            log.append("📅 Analisi periodo: Da file Project")

        # --- Analisi selezionate ---
        if analisi_percentuale:
            if df_finale['% Completamento'].notna().any():
                media = df_finale['% Completamento'].mean()
                log.append(f"📈 % medio completamento: {media:.2f}%")
            else:
                log.append("⚠️ Nessun dato di completamento trovato")

        if analisi_sil:
            log.append("📊 Analisi curva SIL (placeholder simulato)")
        if analisi_manodopera:
            log.append("👷 Analisi manodopera (placeholder simulato)")
        if analisi_mezzi:
            log.append("🚜 Analisi mezzi (placeholder simulato)")

        # --- CSV export ---
        if not df_finale.empty:
            csv_buffer = io.StringIO()
            df_finale.to_csv(csv_buffer, index=False)
            csv_buffers['analisi'] = csv_buffer
        else:
            log.append("⚠️ Nessun dato disponibile per esportazione")

        return {
            'log': log,
            'df_finale': df_finale,
            'csv_buffers': csv_buffers,
            'figures': figures
        }

    except Exception as e:
        log.append(f"❌ Errore: {e}")
        return {'log': log, 'df_finale': pd.DataFrame(), 'csv_buffers': {}, 'figures': {}}
