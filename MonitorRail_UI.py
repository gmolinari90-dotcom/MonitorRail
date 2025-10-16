import streamlit as st
import pandas as pd
import os
from MonitorRail_MVP import estrai_attivita_da_mpp, filtra_attivita_per_periodo, analizza_file_project_mpp
import tempfile

st.set_page_config(page_title="MonitorRail", layout="wide")
st.title("🚄 MonitorRail – Centrale di Controllo MPP")

# -----------------------------
# Upload file .mpp
# -----------------------------
st.markdown("### 1️⃣ Carica file Microsoft Project (.mpp)")
mpp_file = st.file_uploader("Carica file MPP", type=["mpp"])

# -----------------------------
# Funzione cache per leggere MPP (velocizza ripetuti click)
# -----------------------------
@st.cache_data(ttl=600)
def read_mpp_to_df(bytes_data):
    # salva temporaneo e chiama il backend mpp
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mpp")
    tmp.write(bytes_data)
    tmp.close()
    path = tmp.name
    try:
        df = estrai_attivita_da_mpp(path)  # funzione del tuo MVP che ritorna dataframe
    finally:
        # non cancellare immediatamente se vuoi riutilizzarlo; opzionale:
        try:
            os.unlink(path)
        except Exception:
            pass
    return df

# -----------------------------
# Interroga Project (PRIMA dell'analisi)
# -----------------------------
st.markdown("### 2️⃣ Interroga Project — Estrazione preliminare attività")
col_a, col_b = st.columns([3,1])
with col_a:
    data_inizio = st.text_input("Data inizio (gg/mm/aaaa)", value="Da file Project")
with col_b:
    data_fine = st.text_input("Data fine (gg/mm/aaaa)", value="Da file Project")

extracted_df = None
if mpp_file:
    if st.button("🔍 Estrai attività previste nel periodo"):
        with st.spinner("Estrazione attività..."):
            try:
                extracted_df = read_mpp_to_df(mpp_file.getvalue())
                # applica filtro di periodo se inserito
                filtered = filtra_attivita_per_periodo(extracted_df, data_inizio, data_fine)
                st.success(f"✅ Attività estratte: {len(filtered)}")
                st.dataframe(filtered, use_container_width=True)
                csv = filtered.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Scarica attività (CSV)", csv, "attivita_preliminari.csv", "text/csv")
                # salviamo il df in session_state per riutilizzo
                st.session_state["_extracted_df"] = filtered
            except Exception as e:
                st.error(f"Errore estrazione: {e}")
else:
    st.info("Carica un file .MPP per estrarre attività")

# -----------------------------
# Sezione Analisi: checkbox e avvia
# -----------------------------
st.markdown("---")
st.markdown("### 3️⃣ Seleziona analisi da eseguire")
col1, col2 = st.columns(2)
with col1:
    curva_sil = st.checkbox("Curva SIL")
    manodopera = st.checkbox("Manodopera")
with col2:
    mezzi = st.checkbox("Mezzi")
    avanzamento = st.checkbox("% Avanzamento Attività")

analisi_scelte = any([curva_sil, manodopera, mezzi, avanzamento])

# pulsanti
col_run, col_refresh = st.columns([3,1])
with col_refresh:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.experimental_rerun()

with col_run:
    if not analisi_scelte:
        st.button("🚫 Seleziona almeno un'analisi", disabled=True)
    else:
        if st.button("🚀 Avvia Analisi"):
            # prendi il df estratto dalla sessione (se non presente richiama estrazione)
            if "_extracted_df" in st.session_state:
                df_to_use = st.session_state["_extracted_df"]
            else:
                if not mpp_file:
                    st.error("Carica il file .mpp e premi Estrai attività prima di avviare")
                    st.stop()
                df_to_use = read_mpp_to_df(mpp_file.getvalue())
                df_to_use = filtra_attivita_per_periodo(df_to_use, data_inizio, data_fine)

            # esegui analisi (chiama la funzione che opera su file .mpp o su df)
            with st.spinner("Esecuzione analisi..."):
                try:
                    # se preferisci usare direttamente analizza_file_project_mpp che legge il file,
                    # passagli il temp file path come fatto in MVP; qui usiamo df_to_use come base
                    df_res, summary = analizza_file_project_mpp(
                        mpp_file_path=None,  # se la tua funzione richiede path, salva e passa path
                        opzioni={
                            "curva_sil": curva_sil,
                            "manodopera": manodopera,
                            "mezzi": mezzi,
                            "avanzamento": avanzamento
                        },
                        data_inizio=data_inizio,
                        data_fine=data_fine
                    )
                    st.success("✅ Analisi completata")
                    st.dataframe(summary, use_container_width=True)

                    # se curva sil: mostra grafico e download excel/pdf (da implementare in MVP)
                    # ...
                except Exception as e:
                    st.error(f"Errore durante l'analisi: {e}")
