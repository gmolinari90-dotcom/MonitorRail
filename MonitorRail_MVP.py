import pandas as pd
from io import BytesIO
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

def estrai_date_progetto(file_project):
    """Estrae data inizio e fine dal file Project XML"""
    try:
        tree = ET.parse(file_project)
        root = tree.getroot()
        start_tasks, finish_tasks = [], []
        for t in root.findall('.//Task'):
            s = t.find('Start').text if t.find('Start') is not None else None
            f = t.find('Finish').text if t.find('Finish') is not None else None
            if s: start_tasks.append(pd.to_datetime(s))
            if f: finish_tasks.append(pd.to_datetime(f))
        start_date = min(start_tasks) if start_tasks else None
        end_date = max(finish_tasks) if finish_tasks else None
        return start_date, end_date
    except Exception:
        return None, None

def analizza_file_project(
    baseline_file=None,
    avanzamento_file=None,
    start_date=None,
    end_date=None,
    analisi_sil=False,
    analisi_manodopera=False,
    analisi_mezzi=False,
    analisi_percentuale=False
):
    log_messages = []
    df_baseline, df_avanzamento = pd.DataFrame(), pd.DataFrame()
    results = {}

    try:
        # ---------- Lettura file baseline ----------
        if baseline_file:
            tree_base = ET.parse(baseline_file)
            root_base = tree_base.getroot()
            log_messages.append(f"Baseline: {baseline_file.name}")

            tasks_base = []
            for t in root_base.findall('.//Task'):
                uid = t.find('UID').text if t.find('UID') is not None else None
                name = t.find('Name').text if t.find('Name') is not None else None
                start = t.find('Start').text if t.find('Start') is not None else None
                finish = t.find('Finish').text if t.find('Finish') is not None else None
                tasks_base.append({'UID': uid, 'Name': name, 'Start': start, 'Finish': finish})
            df_baseline = pd.DataFrame(tasks_base)

        # ---------- Lettura file avanzamento (opzionale) ----------
        if avanzamento_file:
            tree_av = ET.parse(avanzamento_file)
            root_av = tree_av.getroot()
            log_messages.append(f"Aggiornamento: {avanzamento_file.name}")

            tasks_av = []
            for t in root_av.findall('.//Task'):
                uid = t.find('UID').text if t.find('UID') is not None else None
                name = t.find('Name').text if t.find('Name') is not None else None
                percent = t.find('PercentComplete').text if t.find('PercentComplete') is not None else None
                tasks_av.append({'UID': uid, 'Name': name, 'PercentComplete': percent})
            df_avanzamento = pd.DataFrame(tasks_av)

        # ---------- Combinazione dati ----------
        if not df_baseline.empty and not df_avanzamento.empty:
            df_finale = pd.merge(df_baseline, df_avanzamento, on=['UID','Name'], how='left')
            log_messages.append("Confronto baseline - avanzamento eseguito.")
        elif not df_baseline.empty:
            df_finale = df_baseline.copy()
            log_messages.append("Analisi su baseline. % avanzamento non disponibile.")
        elif not df_avanzamento.empty:
            df_finale = df_avanzamento.copy()
            log_messages.append("Analisi su avanzamento.")
        else:
            df_finale = pd.DataFrame()
            log_messages.append("Nessun dato da analizzare.")

        # ---------- Filtra periodo ----------
        if start_date or end_date:
            if 'Start' in df_finale.columns and 'Finish' in df_finale.columns:
                df_finale['Start_dt'] = pd.to_datetime(df_finale['Start'], errors='coerce')
                df_finale['Finish_dt'] = pd.to_datetime(df_finale['Finish'], errors='coerce')
                if start_date:
                    df_finale = df_finale[df_finale['Finish_dt'] >= pd.to_datetime(start_date)]
                if end_date:
                    df_finale = df_finale[df_finale['Start_dt'] <= pd.to_datetime(end_date)]
                df_finale.drop(columns=['Start_dt','Finish_dt'], inplace=True)

        # ---------- Generazione report e grafici ----------
        results['csv_buffers'], results['figures'] = {}, {}

        if analisi_percentuale and 'PercentComplete' in df_finale.columns:
            df_plot = df_finale.dropna(subset=['PercentComplete'])
            if not df_plot.empty:
                df_plot['PercentComplete'] = df_plot['PercentComplete'].astype(float)
                fig, ax = plt.subplots(figsize=(10,4))
                ax.bar(df_plot['Name'], df_plot['PercentComplete'], color='skyblue')
                ax.set_ylabel('% Completamento')
                ax.set_xlabel('Attività')
                ax.set_xticklabels(df_plot['Name'], rotation=90)
                buf = BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight')
                results['figures']['percentuale'] = buf
                buf_csv = BytesIO()
                df_plot.to_csv(buf_csv, index=False)
                results['csv_buffers']['percentuale'] = buf_csv

        # Report fittizi per SIL, manodopera, mezzi
        for key, flag in zip(['sil','manodopera','mezzi'], [analisi_sil, analisi_manodopera, analisi_mezzi]):
            if flag:
                buf = BytesIO()
                df_finale.to_csv(buf, index=False)
                results['csv_buffers'][key] = buf

        results['df_finale'] = df_finale
        results['log'] = log_messages
        return results

    except Exception as e:
        log_messages.append(f"Errore: {e}")
        return {'log': log_messages, 'df_finale': pd.DataFrame(), 'csv_buffers': {}, 'figures': {}}
