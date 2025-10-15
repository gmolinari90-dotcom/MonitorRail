import pandas as pd
from io import BytesIO
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

def analizza_file_project(baseline_file=None, avanzamento_file=None, start_date=None, end_date=None, float_threshold=5):
    log_messages = []
    df_baseline = pd.DataFrame()
    df_avanzamento = pd.DataFrame()
    fig = None
    img_buffer = None

    try:
        # ---------- Lettura file baseline ----------
        if baseline_file:
            tree_base = ET.parse(baseline_file)
            root_base = tree_base.getroot()
            log_messages.append(f"File baseline caricato correttamente: {baseline_file.name}")

            tasks_base = []
            for t in root_base.findall('.//Task'):
                uid = t.find('UID').text if t.find('UID') is not None else None
                name = t.find('Name').text if t.find('Name') is not None else None
                start = t.find('Start').text if t.find('Start') is not None else None
                finish = t.find('Finish').text if t.find('Finish') is not None else None
                tasks_base.append({'UID': uid, 'Name': name, 'Start': start, 'Finish': finish})
            df_baseline = pd.DataFrame(tasks_base)

        # ---------- Lettura file avanzamento ----------
        if avanzamento_file:
            tree_av = ET.parse(avanzamento_file)
            root_av = tree_av.getroot()
            log_messages.append(f"File avanzamento caricato correttamente: {avanzamento_file.name}")

            tasks_av = []
            for t in root_av.findall('.//Task'):
                uid = t.find('UID').text if t.find('UID') is not None else None
                name = t.find('Name').text if t.find('Name') is not None else None
                percent = t.find('PercentComplete').text if t.find('PercentComplete') is not None else None
                tasks_av.append({'UID': uid, 'Name': name, 'PercentComplete': percent})
            df_avanzamento = pd.DataFrame(tasks_av)

        # ---------- Generazione tabella finale ----------
        if not df_baseline.empty and not df_avanzamento.empty:
            df_finale = pd.merge(df_baseline, df_avanzamento, on=['UID','Name'], how='left')
            log_messages.append("Confronto baseline - avanzamento eseguito.")
        elif not df_baseline.empty:
            df_finale = df_baseline.copy()
            log_messages.append("Analisi eseguita su baseline. Percentuale avanzamento non disponibile.")
        elif not df_avanzamento.empty:
            df_finale = df_avanzamento.copy()
            log_messages.append("Analisi eseguita su file avanzamento. Percentuale avanzamento disponibile se presente.")
        else:
            df_finale = pd.DataFrame()
            log_messages.append("Nessun dato disponibile da analizzare.")

        # CSV buffer
        csv_buffer = BytesIO()
        df_finale.to_csv(csv_buffer, index=False)

        # Grafico PercentComplete solo se colonna disponibile
        if 'PercentComplete' in df_finale.columns and df_finale['PercentComplete'].notnull().any():
            df_plot = df_finale.dropna(subset=['PercentComplete'])
            df_plot['PercentComplete'] = df_plot['PercentComplete'].astype(float)

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(df_plot['Name'], df_plot['PercentComplete'], color='skyblue')
            ax.set_ylabel('Percentuale completamento')
            ax.set_xlabel('Attività')
            ax.set_xticklabels(df_plot['Name'], rotation=90)

            img_buffer = BytesIO()
            fig.savefig(img_buffer, format='png', bbox_inches='tight')
        else:
            fig = None

        return {
            'log': log_messages,
            'df_tasks': df_finale,
            'csv_buffer': csv_buffer,
            'fig': fig,
            'img_buffer': img_buffer
        }

    except ET.ParseError:
        log_messages.append("Errore: file XML non leggibile o corrotto.")
        return {'log': log_messages, 'df_tasks': pd.DataFrame(), 'csv_buffer': BytesIO(), 'fig': None, 'img_buffer': None}
    except Exception as e:
        log_messages.append(f"Errore inatteso: {e}")
        return {'log': log_messages, 'df_tasks': pd.DataFrame(), 'csv_buffer': BytesIO(), 'fig': None, 'img_buffer': None}
