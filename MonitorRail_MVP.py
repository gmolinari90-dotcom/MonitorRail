import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import os
import argparse
import streamlit as st

# ===========================================================
# MonitorRail_MVP.py - Backend reale con feedback su campi mancanti
# ===========================================================

parser = argparse.ArgumentParser(description='Motore MonitorRail')
parser.add_argument('--project', required=True, help='File XML Project')
parser.add_argument('--progress', default='', help='File Project aggiornamento (facoltativo)')
parser.add_argument('--start', default='auto', help='Data inizio analisi (gg/mm/aaaa o auto)')
parser.add_argument('--end', default='auto', help='Data fine analisi (gg/mm/aaaa o auto)')
parser.add_argument('--float-threshold', type=int, default=5, help='Margine flessibilità totale in giorni')
args = parser.parse_args()

output_dir = 'output_monitorrail'
os.makedirs(output_dir, exist_ok=True)

# Creazione log dettagliato
log_file = os.path.join(output_dir, 'run_log.txt')
log_messages = []

# ===========================================================
# 1️⃣ Lettura file Project XML
# ===========================================================
project_file = args.project

try:
    tree = ET.parse(project_file)
    root = tree.getroot()
    log_messages.append(f'File {project_file} letto correttamente.')
except Exception as e:
    log_messages.append(f'ERRORE lettura file: {e}')
    raise

ns = {'ns': 'http://schemas.microsoft.com/project'}

activities = []
for task in root.findall('.//ns:Task', ns):
    id_task = task.find('ns:UID', ns).text if task.find('ns:UID', ns) is not None else None
    name = task.find('ns:Name', ns).text if task.find('ns:Name', ns) is not None else None
    start = task.find('ns:Start', ns).text if task.find('ns:Start', ns) is not None else None
    finish = task.find('ns:Finish', ns).text if task.find('ns:Finish', ns) is not None else None
    percent_complete = task.find('ns:PercentComplete', ns).text if task.find('ns:PercentComplete', ns) is not None else None
    total_slack = task.find('ns:TotalSlack', ns).text if task.find('ns:TotalSlack', ns) is not None else None
    resources = []
    for res_assign in task.findall('ns:Assignments/ns:Assignment', ns):
        res_name = res_assign.find('ns:ResourceUID', ns).text
        resources.append(res_name)

    activities.append({
        'UID': id_task,
        'Nome': name,
        'Start': start,
        'Finish': finish,
        '%Completamento': percent_complete,
        'TotalSlack': total_slack,
        'Risorse': resources
    })

if len(activities) == 0:
    log_messages.append('⚠ Nessuna attività letta. Verranno creati file fittizi di test.')

# Creazione DataFrame
df_activities = pd.DataFrame(activities)

# Controllo campi critici
critical_fields = ['%Completamento', 'TotalSlack', 'Start', 'Finish', 'UID', 'Nome']
for field in critical_fields:
    if df_activities[field].isnull().all():
        log_messages.append(f'⚠ Attenzione: nessun dato {field} letto. Alcuni calcoli potrebbero non essere disponibili.')

# ===========================================================
# Filtraggio periodo
# ===========================================================
if args.start != 'auto':
    start_filter = pd.to_datetime(args.start, dayfirst=True)
    df_activities['Start_dt'] = pd.to_datetime(df_activities['Start'], errors='coerce')
    df_activities = df_activities[df_activities['Start_dt'] >= start_filter]

if args.end != 'auto':
    end_filter = pd.to_datetime(args.end, dayfirst=True)
    df_activities['Finish_dt'] = pd.to_datetime(df_activities['Finish'], errors='coerce')
    df_activities = df_activities[df_activities['Finish_dt'] <= end_filter]

# ===========================================================
# Attività critiche / sub-critiche
# ===========================================================
threshold = args.float_threshold
if 'TotalSlack' in df_activities.columns and df_activities['TotalSlack'].notnull().any():
    critical_tasks = df_activities[df_activities['TotalSlack'].astype(float) <= threshold]
    critical_tasks.to_csv(os.path.join(output_dir, 'summary_alerts.csv'), index=False)
else:
    log_messages.append('⚠ Non è possibile generare summary_alerts.csv: TotalSlack non disponibile.')

# ===========================================================
# Mezzi distinti
# ===========================================================
if 'Risorse' in df_activities.columns and df_activities['Risorse'].notnull().any():
    mezzi_list = []
    for res_list in df_activities['Risorse']:
        mezzi_list.extend(res_list)
    mezzi_distinti = pd.DataFrame(pd.Series(mezzi_list).value_counts()).reset_index()
    mezzi_distinti.columns = ['Mezzo', 'Quantità']
    mezzi_distinti.to_csv(os.path.join(output_dir, 'mezzi_distinti.csv'), index=False)
else:
    log_messages.append('⚠ Non è possibile generare mezzi_distinti.csv: Risorse non disponibili.')

# ===========================================================
# Curva SIL cumulativa
# ===========================================================
if '%Completamento' in df_activities.columns and df_activities['%Completamento'].notnull().any():
    df_activities['AvanzamentoEconomico'] = df_activities['%Completamento'].astype(float)
    sil_curve = df_activities.groupby('Start')['AvanzamentoEconomico'].sum().cumsum()
    plt.figure(figsize=(10,5))
    sil_curve.plot()
    plt.title('Curva di Produzione SIL')
    plt.xlabel('Data Inizio Attività')
    plt.ylabel('Avanzamento cumulativo')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'curva_SIL.png'))
    plt.close()
else:
    log_messages.append('⚠ Non è possibile generare curva_SIL.png: %Completamento non disponibile.')

# ===========================================================
# Diagramma reticolare percorso critico
# ===========================================================
G = nx.DiGraph()
for idx, row in df_activities.iterrows():
    G.add_node(row['Nome'], slack=row['TotalSlack'] if row['TotalSlack'] else 0)

plt.figure(figsize=(12,8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1500, arrowsize=20)
nx.draw_networkx_edge_labels(G, pos, edge_labels={(u,v): G.nodes[v]['slack'] for u,v in G.edges})
plt.title('Diagramma Reticolare (Percorso Critico)')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'diagramma_reticolare.png'))
plt.close()

log_messages.append('Analisi completata. File generati (se disponibili).')

# Scrittura log
with open(log_file, 'w') as log:
    for msg in log_messages:
        log.write(msg + '\n')

# Stampa su console per Streamlit
for msg in log_messages:
    print(msg)

print('Analisi completata e file generati in output_monitorrail/')
