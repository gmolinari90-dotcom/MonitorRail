import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import os
import argparse

# ===========================================================
# MonitorRail_MVP.py - Backend reale
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

# ===========================================================
# 1️⃣ Lettura file Project XML
# ===========================================================
project_file = args.project

tree = ET.parse(project_file)
root = tree.getroot()

ns = {'ns': 'http://schemas.microsoft.com/project'}  # Namespace XML di Project

activities = []
for task in root.findall('.//ns:Task', ns):
    id_task = task.find('ns:UID', ns).text
    name = task.find('ns:Name', ns).text
    start = task.find('ns:Start', ns).text if task.find('ns:Start', ns) is not None else None
    finish = task.find('ns:Finish', ns).text if task.find('ns:Finish', ns) is not None else None
    percent_complete = int(task.find('ns:PercentComplete', ns).text) if task.find('ns:PercentComplete', ns) is not None else 0
    total_slack = int(task.find('ns:TotalSlack', ns).text) if task.find('ns:TotalSlack', ns) is not None else 0
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

df_activities = pd.DataFrame(activities)

# ===========================================================
# 2️⃣ Filtraggio periodo se specificato
# ===========================================================
if args.start != 'auto':
    start_filter = pd.to_datetime(args.start, dayfirst=True)
    df_activities['Start_dt'] = pd.to_datetime(df_activities['Start'])
    df_activities = df_activities[df_activities['Start_dt'] >= start_filter]

if args.end != 'auto':
    end_filter = pd.to_datetime(args.end, dayfirst=True)
    df_activities['Finish_dt'] = pd.to_datetime(df_activities['Finish'])
    df_activities = df_activities[df_activities['Finish_dt'] <= end_filter]

# ===========================================================
# 3️⃣ Identificazione attività critiche / sub-critiche
# ===========================================================
threshold = args.float_threshold
critical_tasks = df_activities[df_activities['TotalSlack'] <= threshold]
critical_tasks.to_csv(os.path.join(output_dir, 'summary_alerts.csv'), index=False)

# ===========================================================
# 4️⃣ Estrazione mezzi distinti
# ===========================================================
mezzi_list = []
for res_list in df_activities['Risorse']:
    mezzi_list.extend(res_list)

mezzi_distinti = pd.DataFrame(pd.Series(mezzi_list).value_counts()).reset_index()
mezzi_distinti.columns = ['Mezzo', 'Quantità']
mezzi_distinti.to_csv(os.path.join(output_dir, 'mezzi_distinti.csv'), index=False)

# ===========================================================
# 5️⃣ Curva SIL cumulativa
# ===========================================================
df_activities['AvanzamentoEconomico'] = df_activities['%Completamento']  # placeholder
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

# ===========================================================
# 6️⃣ Diagramma reticolare percorso critico
# ===========================================================
G = nx.DiGraph()
for idx, row in df_activities.iterrows():
    G.add_node(row['Nome'], slack=row['TotalSlack'])

# Aggiunta archi semplificati (solo per esempio, leggere Predecessors se disponibile)
for idx, row in df_activities.iterrows():
    pred = row.get('Predecessors', None)
    if pred:
        for p in pred.split(','):
            pred_name = df_activities[df_activities['UID'] == p]['Nome'].values
            if len(pred_name) > 0:
                G.add_edge(pred_name[0], row['Nome'])

plt.figure(figsize=(12,8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1500, arrowsize=20)
nx.draw_networkx_edge_labels(G, pos, edge_labels={(u,v): G.nodes[v]['slack'] for u,v in G.edges})
plt.title('Diagramma Reticolare (Percorso Critico)')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'diagramma_reticolare.png'))
plt.close()

print('Analisi completata e file generati in output_monitorrail/')
