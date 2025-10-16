# MonitorRail_UI.py
import streamlit as st
import pandas as pd
import io
import os
import matplotlib.pyplot as plt

from MonitorRail_MVP import convert_mpp_to_json, build_scurve_from_json, extract_tasks_in_period

st.set_page_config(page_title="MonitorRail MPP", layout="wide")
st.title("MonitorRail - Lettura MPP via microservizio")

# CONFIG via env o streamlit secrets
SERVICE_URL = st.secrets.get("SERVICE_URL") if "SERVICE_URL" in st.secrets else os.getenv("SERVICE_URL", "https://monitorrail.onrender.com")
API_KEY = st.secrets.get("API_KEY") if "API_KEY" in st.secrets else os.getenv("MONITORRAIL_API_KEY", "secretmonitor1582")

st.markdown("1️⃣ Carica file .MPP (il file verrà convertito in JSON dal servizio)")

mpp_file = st.file_uploader("Carica .MPP", type=["mpp"])
data_inizio = st.text_input("Data inizio (gg/mm/aaaa)", value="Da file Project")
data_fine = st.text_input("Data fine (gg/mm/aaaa)", value="Da file Project")

if mpp_file:
    if st.button("🔍 Estrai attività dal file (preliminare)"):
        with st.spinner("Invio file al servizio di conversione..."):
            try:
                parsed = convert_mpp_to_json(mpp_file.getvalue())
                st.success("✅ Conversione completata")
                st.session_state["parsed_json"] = parsed
            except Exception as e:
                st.error(f"Errore conversione: {e}")
                st.stop()

if "parsed_json" in st.session_state:
    parsed = st.session_state["parsed_json"]
    st.subheader("Informazioni progetto")
    st.write({
        "projectName": parsed.get("projectName"),
        "start": parsed.get("start"),
        "finish": parsed.get("finish")
    })

    if st.button("🔎 Estrai attività previste nel periodo"):
        df_tasks = extract_tasks_in_period(parsed, start_date=data_inizio, end_date=data_fine)
        st.success(f"Attività estratte: {len(df_tasks)}")
        st.dataframe(df_tasks, use_container_width=True)
        csv = df_tasks.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Scarica attività (CSV)", csv, "attivita_periodo.csv", "text/csv")

    st.markdown("---")
    st.subheader("Seleziona analisi")
    curva = st.checkbox("Curva SIL")
    manod = st.checkbox("Manodopera")
    mez = st.checkbox("Mezzi")
    avanz = st.checkbox("% Avanzamento")

    if st.button("🚀 Avvia Analisi (con dati JSON)"):
        if curva:
            df_s = build_scurve_from_json(parsed, period="M")
            if df_s.empty:
                st.warning("Non ci sono dati time-phased per generare la Curva SIL.")
            else:
                st.markdown("### 📈 Curva SIL (cumulativa mensile)")
                fig, ax = plt.subplots()
                ax.plot(df_s["period"], df_s["cumulative"], marker="o")
                ax.set_xlabel("Periodo")
                ax.set_ylabel("Costo cumulativo")
                ax.grid(True)
                st.pyplot(fig)

                # CSV e PNG download
                csv = df_s.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Scarica S-Curve (CSV)", csv, "scurve.csv", "text/csv")

                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight")
                st.download_button("⬇️ Scarica grafico (PNG)", buf.getvalue(), "scurve.png", "image/png")

        if manod:
            st.info("Analisi manodopera: in sviluppo (placeholder).")
        if mez:
            st.info("Analisi mezzi: in sviluppo (placeholder).")
        if avanz:
            st.info("Analisi avanzamento: in sviluppo (placeholder).")

