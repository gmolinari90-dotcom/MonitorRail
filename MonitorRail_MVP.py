# ======================
# FILE: MonitorRail_MVP.py
# ======================

import pandas as pd
from io import BytesIO
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

def analizza_file_project(mpp_file, progress_file=None, start_date=None, end_date=None, float_threshold=5):
    log_messages = []
    df_tasks = pd.DataFrame()
    fig = None
    img_buffer = None

    try:
        # Parsing XML
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

        # Log campi mancanti
        missing_fields = df_tasks.isnull().sum()
        log_messages.append(f"Totale attività lette: {len(df_tasks)}")
        for col, val in missing_fields.items():
            if val > 0:
                log_messages.append(f"⚠️ {val} valori mancanti nella colonna '{col}'")

        # CSV buffer
        csv_buffer = BytesIO()
        df_tasks.to_csv(csv_buffer, index=False)

        # Grafico PercentComplete
        if 'PercentComplete' in df_tasks.columns and df_tasks['PercentComplete'].notnull().any():
            df_plot = df_tasks.dropna(subset=['PercentComplete'])
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
            'df_tasks': df_tasks,
            'csv_buffer': csv_buffer,
            'fig': fig,
            'img_buffer': img_buffer
        }

    except ET.ParseError:
        log_messages.append("Errore: il file XML non è leggibile o è corrotto.")
        return {'log': log_messages, 'df_tasks': df_tasks, 'csv_buffer': BytesIO(), 'fig': None, 'img_buffer': None}
    except Exception as e:
        log_messages.append(f"Errore inatteso durante l'analisi: {e}")
        return {'log': log_messages, 'df_tasks': df_tasks, 'csv_buffer': BytesIO(), 'fig': None, 'img_buffer': None}
