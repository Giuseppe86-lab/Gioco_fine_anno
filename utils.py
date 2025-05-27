import streamlit as st
import pandas as pd
import time

def init_session_state():
    if "risposte" not in st.session_state:
        st.session_state.risposte = []
    if "squadre" not in st.session_state:
        st.session_state.squadre = []
    if "punteggio_base" not in st.session_state:
        st.session_state.punteggio_base = 1
    if "penalita" not in st.session_state:
        st.session_state.penalita = 1
    if "risposte_date" not in st.session_state:
        st.session_state.risposte_date = {}  # (squadra, domanda): [risposte]
    if "jolly" not in st.session_state:
        st.session_state.jolly = {}  # squadra: indice_domanda
    if "corrette_per_domanda" not in st.session_state:
        st.session_state.corrette_per_domanda = {}  # domanda: numero risposte corrette
    if "punteggi" not in st.session_state:
        st.session_state.punteggi = {}  # squadra: [punti_per_domanda]
    if "bonus" not in st.session_state:
        st.session_state.bonus = {}  # squadra: [bonus_per_domanda], inizializzati a zero
    if "malus" not in st.session_state:
        st.session_state.malus = {}  # squadra: [malus_per_domanda], inizializzati a zero
    if "timer_start" not in st.session_state:
        st.session_state.timer_start = None
    if "timer_duration" not in st.session_state:
        st.session_state.timer_duration = 0

def inizializza_gioco(n_domande, risposte, nomi_squadre, k, m):
    st.session_state.risposte = risposte
    st.session_state.squadre = nomi_squadre
    st.session_state.punteggio_base = k
    st.session_state.penalita = m
    st.session_state.risposte_date = {}
    st.session_state.jolly = {}
    st.session_state.corrette_per_domanda = {i: 0 for i in range(n_domande)}
    st.session_state.punteggi = {s: [0] * n_domande for s in nomi_squadre}
    st.session_state.bonus = {s: [0] * n_domande for s in nomi_squadre}
    st.session_state.malus = {s: [0] * n_domande for s in nomi_squadre}

def aggiorna_risposta(squadra, domanda_idx, risposta):
    key = (squadra, domanda_idx)
    corretta = float(st.session_state.risposte[domanda_idx])
    risposta = float(risposta)

    if key not in st.session_state.risposte_date:
        st.session_state.risposte_date[key] = []

    # Se la squadra ha già dato una risposta corretta a questa domanda, non aggiornare
    if st.session_state.bonus[squadra][domanda_idx] > 0:
        # Già risposta correttamente, non accettare altre modifiche
        st.write('Risposta corretta già data precedentemente')
        return

    # Aggiungi la risposta alla lista (anche se errata)
    st.session_state.risposte_date[key].append(risposta)

    if risposta == corretta:
        # Risposta corretta: aggiorna bonus (solo una volta)
        if st.session_state.bonus[squadra][domanda_idx] == 0:
            st.session_state.corrette_per_domanda[domanda_idx] +=1 
            bonus_val = st.session_state.punteggio_base/st.session_state.corrette_per_domanda[domanda_idx]
            # Se c'è jolly raddoppia bonus per quella domanda
            if st.session_state.jolly.get(squadra) == domanda_idx:
                bonus_val *= 2
            st.session_state.bonus[squadra][domanda_idx] = bonus_val


    else:
        # Risposta errata: incrementa malus (cumulativo)
        penalita = st.session_state.penalita
        if st.session_state.jolly.get(squadra) == domanda_idx:
            penalita *= 2

        st.session_state.malus[squadra][domanda_idx] += penalita

    # Aggiorna il punteggio netto (bonus - malus) per la domanda
    st.session_state.punteggi[squadra][domanda_idx] = (round(
        st.session_state.bonus[squadra][domanda_idx] - st.session_state.malus[squadra][domanda_idx],2)
    )

def assegna_jolly(squadra, domanda_idx):
    if squadra not in st.session_state.jolly:
        st.session_state.jolly[squadra] = domanda_idx

def get_classifica_df():
    squadre = st.session_state.squadre
    risposte = st.session_state.risposte
    n_domande = len(risposte)

    rows = []
    for squadra in squadre:
        punteggi = st.session_state.punteggi.get(squadra, [0] * n_domande)
        row = {"Squadra": squadra}
        for i in range(n_domande):
            row[f"D{i+1}"] = punteggi[i]
        row["Totale"] = sum(punteggi)
        rows.append(row)

    return pd.DataFrame(rows)

def set_timer(minuti):
    st.session_state.timer_start = time.time()
    st.session_state.timer_duration = minuti * 60

def get_remaining_time():
    if st.session_state.timer_start is None:
        return st.session_state.timer_duration
    elapsed = time.time() - st.session_state.timer_start
    remaining = max(0, int(st.session_state.timer_duration - elapsed))
    return remaining

def reset_gioco():
    for key in list(st.session_state.keys()):
        if key not in ["page", "sidebar_state"]:
            del st.session_state[key]
    init_session_state()
