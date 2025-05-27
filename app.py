import streamlit as st
import time
import pandas as pd
from utils import (
    init_session_state, inizializza_gioco, aggiorna_risposta,
    assegna_jolly, get_classifica_df, set_timer, get_remaining_time,
    reset_gioco
)

init_session_state()

st.set_page_config(layout="wide")

st.sidebar.title("Navigazione")
pagina = st.sidebar.radio("Vai a", ["Impostazione", "Inserimento Risposte / Jolly", "Classifica"])

if pagina == "Impostazione":
    st.title("⚙️ Impostazioni del gioco")

    x = st.number_input("Numero di domande", min_value=1, step=1, key="x")
    n = st.number_input("Numero di squadre", min_value=1, step=1, key="n")

    k = st.number_input("Punteggio base per domanda (k) - solo numeri interi", min_value=1, step=1, key="k")
    m = st.number_input("Penalità per risposta sbagliata (m) - solo numeri interi", min_value=1, step=1, key="m")

    durata_timer = st.number_input("Durata timer (minuti)", min_value=1, step=1, key="durata_timer")

    risposte = []
    for i in range(x):
        risp = st.number_input(f"Risposta corretta alla domanda {i+1}", key=f"risp_{i}")
        risposte.append(risp)

    nomi_squadre = []
    for i in range(n):
        nome = st.text_input(f"Nome squadra {i+1}", key=f"squadra_{i}")
        nomi_squadre.append(nome.strip())

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Inizializza Gioco"):
            if all(nomi_squadre) and len(risposte) == x:
                inizializza_gioco(x, risposte, nomi_squadre, k, m)
                st.session_state.timer_duration = durata_timer * 60
                st.session_state.timer_start = None
                st.success("Gioco inizializzato!")
            else:
                st.warning("Inserire tutti i nomi delle squadre e tutte le risposte corrette.")

    with col2:
        if st.button("Reset gioco"):
            reset_gioco()
            st.success("Gioco resettato!")

elif pagina == "Inserimento Risposte / Jolly":
    st.title("📝 Inserimento Risposte & Scelta Jolly")

    if not st.session_state.get("squadre") or not st.session_state.get("risposte"):
        st.warning("Configura prima le impostazioni nella pagina dedicata.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Risposte alle domande")
            squadra = st.selectbox("Seleziona squadra", st.session_state.squadre)
            domanda_idx = st.number_input(
                "Numero domanda (1-based)",
                min_value=1,
                max_value=len(st.session_state.risposte),
                key="num_domanda_risposta"
            ) - 1
            risposta = st.text_input("Risposta", key="input_risposta")

            if st.button("Invia risposta"):
                try:
                    val = float(risposta.strip())
                    # se arrivo qui, la conversione è riuscita, val contiene il numero
                    aggiorna_risposta(squadra, domanda_idx, val)
                    st.success("Risposta registrata.")
                except ValueError:
                    st.warning("Inserire un numero valido (positivo o negativo, intero o decimale).")

        with col2:
            st.subheader("Scelta jolly (una volta sola)")
            squadra_j = st.selectbox("Squadra (per jolly)", st.session_state.squadre, key="squadra_jolly")

            if squadra_j in st.session_state.jolly:
                st.info(f"Jolly già scelto: D{st.session_state.jolly[squadra_j] + 1}")
            else:
                domanda_j = st.number_input(
                    "Domanda jolly (1-based)",
                    min_value=1,
                    max_value=len(st.session_state.risposte),
                    key="jolly_input"
                ) - 1
                if st.button("Assegna jolly"):
                    assegna_jolly(squadra_j, domanda_j)
                    st.success("Jolly assegnato!")

elif pagina == "Classifica":
    st.header("Classifica in tempo reale")

    if not st.session_state.get("squadre") or not st.session_state.get("risposte"):
        st.warning("Configura prima le impostazioni nella pagina dedicata.")
    else:
        df_classifica = get_classifica_df()
        df_classifica = df_classifica.sort_values(by="Totale", ascending=False)

        # Individua colonne numeriche da formattare
        col_domande = [col for col in df_classifica.columns if col.startswith("D")]
        col_numeriche = col_domande + ["Totale"]

        # Converte in float in modo sicuro
        for col in col_numeriche:
            df_classifica[col] = pd.to_numeric(df_classifica[col], errors="coerce")

        # Funzione per colorare di verde le celle > 0
        def color_positive(val):
            try:
                return 'background-color: lightgreen' if float(val) > 0 else ''
            except:
                return ''

        # Applica colore + format solo a colonne numeriche
        styled_df = (
            df_classifica
            .style
            .applymap(color_positive, subset=col_domande)
            .format({col: "{:.2f}" for col in col_numeriche})
        )

        st.dataframe(styled_df, use_container_width=True)

        st.subheader("⏲️ Timer")
        col1, col2 = st.columns([1, 3])

        with col1:
            if st.button("Avvia Timer"):
                st.session_state.timer_start = time.time()

        with col2:
            if st.session_state.timer_duration > 0:
                remaining = get_remaining_time()
                minutes, seconds = divmod(remaining, 60)
                st.metric("Tempo rimanente", f"{minutes:02d}:{seconds:02d}")

                if remaining > 0:
                    time.sleep(1)
                    st.experimental_rerun()
            else:
                st.info("Imposta un timer nella pagina Impostazioni.")


