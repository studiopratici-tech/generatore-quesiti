import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple

# ==============================================================================
# CONFIGURAZIONE
# ==============================================================================
st.set_page_config(
    page_title="Generatore Scritture Contabili | Studio Pratici",
    layout="wide",
    page_icon="📒"
)

# ==============================================================================
# PIANO DEI CONTI COMPLETO (Estratto da Ranocchi GIS)
# ==============================================================================
PIANO_CONTI_COMPLETO = {
    # 01. CREDITI SOCI
    "01.01.001": {"desc": "Soci c/sottoscrizione", "tipo": "patrimoniale_attivo", "normale": "dare"},
    "01.01.021": {"desc": "Soci c/decimi richiamati", "tipo": "patrimoniale_attivo", "normale": "dare"},
    
    # 04. IMMOBILIZZAZIONI IMMATERIALI
    "04.01.009": {"desc": "Spese di costituzione", "tipo": "imm_materiali", "normale": "dare"},
    "04.09.001": {"desc": "Avviamento", "tipo": "imm_materiali", "normale": "dare"},
    
    # 07. FONDI AMM.TO IMMATERIALI
    "07.09.001": {"desc": "F.do amm.to avviamento", "tipo": "fondo_ammortamento", "normale": "avere"},
    
    # 13. IMMOBILIZZAZIONI MATERIALI (Dettaglio completo)
    "13.03.001": {"desc": "Fabbricati civili", "tipo": "imm_materiali", "normale": "dare"},
    "13.09.001": {"desc": "Autovetture", "tipo": "imm_materiali", "normale": "dare"},
    "13.09.005": {"desc": "Autocarri", "tipo": "imm_materiali", "normale": "dare"},
    "13.09.017": {"desc": "Autovetture professionista", "tipo": "imm_materiali", "normale": "dare"},
    "13.09.025": {"desc": "Autovetture uso promiscuo dip.", "tipo": "imm_materiali", "normale": "dare"},
    "13.09.065": {"desc": "Computer ed accessori", "tipo": "imm_materiali", "normale": "dare"},
    "13.09.069": {"desc": "Telefonia fissa", "tipo": "imm_materiali", "normale": "dare"},
    "13.09.073": {"desc": "Telefonia mobile", "tipo": "imm_materiali", "normale": "dare"},
    "13.09.077": {"desc": "Mobili", "tipo": "imm_materiali", "normale": "dare"},
    "13.09.081": {"desc": "Arredi", "tipo": "imm_materiali", "normale": "dare"},
    
    # 16. FONDI AMM.TO MATERIALI
    "16.01.005": {"desc": "F.do amm.to fabbricati civili", "tipo": "fondo_ammortamento", "normale": "avere"},
    "16.07.001": {"desc": "F.do amm.to autovetture", "tipo": "fondo_ammortamento", "normale": "avere"},
    "16.07.005": {"desc": "F.do amm.to autocarri", "tipo": "fondo_ammortamento", "normale": "avere"},
    "16.07.045": {"desc": "F.do amm.to computer", "tipo": "fondo_ammortamento", "normale": "avere"},
    "16.07.053": {"desc": "F.do amm.to telefonia mobile", "tipo": "fondo_ammortamento", "normale": "avere"},
    "16.07.057": {"desc": "F.do amm.to mobili", "tipo": "fondo_ammortamento", "normale": "avere"},
    
    # 28. CREDITI (Clienti, IVA, Tributi)
    "28.01.001": {"desc": "Cliente", "tipo": "crediti", "normale": "dare"},
    "28.11.001": {"desc": "Credito IRES", "tipo": "crediti_tributari", "normale": "dare"},
    "28.11.005": {"desc": "Credito IRAP", "tipo": "crediti_tributari", "normale": "dare"},
    "28.11.009": {"desc": "Credito IVA", "tipo": "crediti_tributari", "normale": "dare"},
    "28.11.021": {"desc": "Erario c/acconto IRES", "tipo": "crediti_tributari", "normale": "dare"},
    "28.11.049": {"desc": "Erario c/rit. subite", "tipo": "crediti_tributari", "normale": "dare"},
    
    # 34. DISPONIBILITÀ LIQUIDE
    "34.01.001": {"desc": "Banca c/c A", "tipo": "liquidita", "normale": "dare"},
    "34.01.005": {"desc": "Banca c/c B", "tipo": "liquidita", "normale": "dare"},
    "34.05.001": {"desc": "Cassa contanti", "tipo": "liquidita", "normale": "dare"},
    
    # 40. PATRIMONIO NETTO
    "40.01.001": {"desc": "Capitale sociale", "tipo": "patrimonio", "normale": "avere"},
    "40.07.001": {"desc": "Riserva legale", "tipo": "patrimonio", "normale": "avere"},
    "40.15.001": {"desc": "Utile esercizi precedenti", "tipo": "patrimonio", "normale": "avere"},
    "40.17.001": {"desc": "Utile d'esercizio", "tipo": "patrimonio", "normale": "avere"},
    "40.17.005": {"desc": "Perdita esercizio", "tipo": "patrimonio", "normale": "dare"},
    
    # 49. DEBITI (Fornitori, Tributi, Previdenza, Personale)
    "49.13.001": {"desc": "Fornitore", "tipo": "debiti", "normale": "avere"},
    "49.23.001": {"desc": "Erario c/IRES", "tipo": "debiti_tributari", "normale": "avere"},
    "49.23.005": {"desc": "Erario c/IRAP", "tipo": "debiti_tributari", "normale": "avere"},
    "49.23.009": {"desc": "Erario c/IVA", "tipo": "debiti_tributari", "normale": "avere"},
    "49.23.029": {"desc": "Erario c/rit. fisc. lav. dip.", "tipo": "debiti_tributari", "normale": "avere"},
    "49.23.033": {"desc": "Erario c/rit. fisc. collab.", "tipo": "debiti_tributari", "normale": "avere"},
    "49.23.039": {"desc": "Erario c/rit. fisc. lav. aut.", "tipo": "debiti_tributari", "normale": "avere"},
    "49.25.001": {"desc": "Debito v/ INPS lavoro dip.", "tipo": "debiti_prev", "normale": "avere"},
    "49.25.005": {"desc": "Debito v/ INAIL", "tipo": "debiti_prev", "normale": "avere"},
    "49.27.025": {"desc": "Dipendenti c/retribuzioni", "tipo": "debiti_pers", "normale": "avere"},
    "49.27.045": {"desc": "Dipendenti c/ferie da liq.", "tipo": "debiti_pers", "normale": "avere"},
    "49.27.001": {"desc": "Debiti v/amministratori", "tipo": "debiti_pers", "normale": "avere"},
    
    # 60. RICAVI
    "60.01.001": {"desc": "Ricavi cessioni di beni", "tipo": "economico_ricavi", "normale": "avere"},
    "60.01.005": {"desc": "Ricavi prestazione servizi", "tipo": "economico_ricavi", "normale": "avere"},
    "60.01.009": {"desc": "Merci c/vendite", "tipo": "economico_ricavi", "normale": "avere"},
    
    # 71. ALTRI RICAVI
    "71.01.053": {"desc": "Risarcimento danni", "tipo": "altri_ricavi", "normale": "avere"},
    
    # 73. ACQUISTI
    "73.01.001": {"desc": "Materie prime c/acquisti", "tipo": "economico_costi", "normale": "dare"},
    "73.01.013": {"desc": "Merci c/acquisti", "tipo": "economico_costi", "normale": "dare"},
    "73.09.006": {"desc": "Carburanti e lubrificanti", "tipo": "economico_costi", "normale": "dare"},
    "73.09.045": {"desc": "Cancelleria e stampati", "tipo": "economico_costi", "normale": "dare"},
    "73.09.077": {"desc": "Beni < Euro 516", "tipo": "economico_costi", "normale": "dare"},
    "73.09.121": {"desc": "Altri acquisti indeducibili", "tipo": "economico_costi", "normale": "dare"},
    
    # 75. SERVIZI
    "75.01.025": {"desc": "Energia elettrica", "tipo": "economico_costi", "normale": "dare"},
    "75.05.001": {"desc": "Manut. fabbricati", "tipo": "economico_costi", "normale": "dare"},
    "75.05.105": {"desc": "Manut. autovetture", "tipo": "economico_costi", "normale": "dare"},
    "75.05.106": {"desc": "Manut. autovetture indeduc.", "tipo": "economico_costi", "normale": "dare"},
    "75.11.001": {"desc": "Consulenze amministrative", "tipo": "economico_costi", "normale": "dare"},
    "75.11.002": {"desc": "Consulenze", "tipo": "economico_costi", "normale": "dare"},
    "75.11.017": {"desc": "Compensi amministratore", "tipo": "economico_costi", "normale": "dare"},
    "75.11.021": {"desc": "Contr. INPS amministratori", "tipo": "economico_costi", "normale": "dare"},
    "75.11.113": {"desc": "Spese telefoniche", "tipo": "economico_costi", "normale": "dare"},
    "75.11.114": {"desc": "Spese telefonia mobile", "tipo": "economico_costi", "normale": "dare"},
    "75.11.116": {"desc": "Spese tel. promiscue 80%", "tipo": "economico_costi", "normale": "dare"},
    "75.11.117": {"desc": "Spese telefonia indeduc.", "tipo": "economico_costi", "normale": "dare"},
    "75.13.037": {"desc": "Spese di pubblicità", "tipo": "economico_costi", "normale": "dare"},
    "75.17.033": {"desc": "Viaggi e trasferte", "tipo": "economico_costi", "normale": "dare"},
    "75.17.041": {"desc": "Spese di rappresentanza", "tipo": "economico_costi", "normale": "dare"},
    "75.17.081": {"desc": "Spese servizi bancari", "tipo": "economico_costi", "normale": "dare"},
    "77.01.009": {"desc": "Canone locaz. fabb. civili", "tipo": "economico_costi", "normale": "dare"},
    "77.03.105": {"desc": "Canone leasing autov.", "tipo": "economico_costi", "normale": "dare"},
    "77.05.061": {"desc": "Canone noleggio autov.", "tipo": "economico_costi", "normale": "dare"},
    
    # 79. COSTO PERSONALE
    "79.01.005": {"desc": "Stipendi impiegati", "tipo": "costo_personale", "normale": "dare"},
    "79.03.001": {"desc": "Oneri INPS", "tipo": "costo_personale", "normale": "dare"},
    "79.05.001": {"desc": "Acc.to fondo TFR", "tipo": "costo_personale", "normale": "dare"},
    
    # 83. AMMORTAMENTI
    "83.03.001": {"desc": "Amm.to fabbricati civili", "tipo": "ammortamenti", "normale": "dare"},
    "83.09.001": {"desc": "Amm.to autovetture", "tipo": "ammortamenti", "normale": "dare"},
    "83.09.065": {"desc": "Amm.to computer", "tipo": "ammortamenti", "normale": "dare"},
    "83.11.105": {"desc": "Amm.to inded. autovetture", "tipo": "ammortamenti", "normale": "dare"},
    "83.11.169": {"desc": "Amm.to inded. computer", "tipo": "ammortamenti", "normale": "dare"},
    "83.11.177": {"desc": "Amm.to inded. tel. mobile", "tipo": "ammortamenti", "normale": "dare"},
    
    # 92. ONERI DIVERSI
    "92.01.001": {"desc": "Imposta di bollo", "tipo": "oneri", "normale": "dare"},
    "92.01.005": {"desc": "IMU", "tipo": "oneri", "normale": "dare"},
    "92.01.037": {"desc": "Tasse proprietà autov.", "tipo": "oneri", "normale": "dare"},
    "92.01.082": {"desc": "Tasse prop. autov. inded.", "tipo": "oneri", "normale": "dare"},
    "92.01.113": {"desc": "Multe e ammende", "tipo": "oneri", "normale": "dare"},
    "92.01.153": {"desc": "Oneri non deducibili", "tipo": "oneri", "normale": "dare"},
    
    # 93. ONERI FINANZIARI
    "93.15.021": {"desc": "Interessi pass. banche", "tipo": "oneri_fin", "normale": "dare"},
    "93.15.025": {"desc": "Interessi pass. mutui", "tipo": "oneri_fin", "normale": "dare"},
    
    # 96. IMPOSTE
    "96.01.001": {"desc": "IRES", "tipo": "imposte", "normale": "dare"},
    "96.01.005": {"desc": "IRAP", "tipo": "imposte", "normale": "dare"},
}

# ==============================================================================
# LOGICA DI SUPPORTO
# ==============================================================================

def fmt_conto(codice: str) -> str:
    info = PIANO_CONTI_COMPLETO.get(codice, {})
    return f"{codice} - {info.get('desc', 'Conto non trovato')}"

def cerca_conti(query: str) -> List[Dict]:
    risultati = []
    q = query.lower()
    for cod, info in PIANO_CONTI_COMPLETO.items():
        if q in cod or q in info['desc'].lower():
            risultati.append({'codice': cod, **info})
    return risultati

# ==============================================================================
# INTERFACCIA
# ==============================================================================

def main():
    st.title("📒 Generatore Scritture Contabili SRL")
    
    with st.sidebar:
        st.header("Configurazione")
        modalita = st.radio(
            "Tipo Operazione",
            ["📋 Operazione Standard (Fattura)", "👷 Stipendi (Lordo→Netto)", "🏛️ Patrimonio / Versamenti", "✍️ Manuale"],
            help="Scegli il tipo di scrittura da generare"
        )
        
        st.info(f"Piano dei conti caricato: {len(PIANO_CONTI_COMPLETO)} conti")

    # --- MODALITÀ 1: OPERAZIONE STANDARD (CON IVA) ---
    if modalita == "📋 Operazione Standard (Fattura)":
        st.header("📋 Genera Scrittura (Fattura/Acquisto/Vendita)")
        
        col1, col2 = st.columns(2)
        with col1:
            imponibile = st.number_input("Imponibile €", min_value=0.0, step=0.01, format="%.2f")
        with col2:
            aliquota = st.number_input("Aliquota IVA %", min_value=0.0, step=1.0, value=22.0)
            
        iva = round(imponibile * (aliquota / 100), 2)
        totale = round(imponibile + iva, 2)
        
        st.metric("Totale Documento", f"€ {totale:,.2f}")
        
        # Selezione conti
        st.subheader("Configurazione Conti")
        
        # Ricerca conti
        ricerca = st.text_input("Cerca conto...", placeholder="Es: fornitore, banca, iva...")
        
        col_dare, col_avere = st.columns(2)
        
        with col_dare:
            st.write("**DARE (Costi/Attività)**")
            dare_codi = st.selectbox("Conto DARE", ["73.01.013", "28.11.009", "34.01.001"], format_func=fmt_conto, key="dare_std")
            
        with col_avere:
            st.write("**AVERE (Ricavi/Passività)**")
            avere_codi = st.selectbox("Conto AVERE", ["49.13.001", "60.01.009", "34.01.001"], format_func=fmt_conto, key="avere_std")
        
        if st.button("Genera Scrittura", type="primary"):
            if imponibile > 0:
                # Logica di assegnazione importi
                righe_dare = []
                righe_avere = []
                
                # Se il conto DARE è IVA
                if '28.11.009' in dare_codi:
                    righe_dare.append({'conto': dare_codi, 'importo': iva})
                else:
                    righe_dare.append({'conto': dare_codi, 'importo': imponibile})
                    
                # Se il conto AVERE è IVA (Vendite)
                if '49.23.009' in avere_codi:
                    righe_avere.append({'conto': avere_codi, 'importo': iva})
                else:
                    # Se è una vendita, il fornitore/cliente ha il totale, altrimenti imponibile
                    if '60.01' in avere_codi:
                        # Vendita: Avere = Vendita + IVA Debito
                        righe_avere.append({'conto': avere_codi, 'importo': imponibile})
                        # Aggiungiamo riga IVA debito se non è già nel select
                        if '49.23.009' != avere_codi:
                            righe_avere.append({'conto': '49.23.009', 'importo': iva})
                    else:
                        righe_avere.append({'conto': avere_codi, 'importo': totale})
                
                # Visualizzazione tabella
                df_dare = pd.DataFrame(righe_dare)
                df_dare['Descrizione'] = df_dare['conto'].apply(fmt_conto)
                
                df_avere = pd.DataFrame(righe_avere)
                df_avere['Descrizione'] = df_avere['conto'].apply(fmt_conto)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("DARE")
                    st.dataframe(df_dare, hide_index=True, use_container_width=True)
                    st.write(f"**Totale Dare: € {sum(df_dare['importo']):,.2f}**")
                with c2:
                    st.subheader("AVERE")
                    st.dataframe(df_avere, hide_index=True, use_container_width=True)
                    st.write(f"**Totale Avere: € {sum(df_avere['importo']):,.2f}**")

    # --- MODALITÀ 2: STIPENDI (SENZA IVA, CON CALCOLO NETTO) ---
    elif modalita == "👷 Stipendi (Lordo→Netto)":
        st.header("👷 Registrazione Stipendi (Competenza)")
        
        st.info("Inserisci il costo Lordo Azienda. Il sistema calcola automaticamente il Netto in busta e i debiti verso enti.")
        
        col1, col2 = st.columns(2)
        with col1:
            lordo = st.number_input("Retribuzione Lorda Dipendente €", min_value=0.0, step=0.01, format="%.2f")
            inps_dip_pct = st.number_input("% INPS Dipendente", value=9.19, step=0.01)
            irpef = st.number_input("IRPEF Stimata €", min_value=0.0, step=0.01, format="%.2f")
            
        with col2:
            inps_azienda_pct = st.number_input("% Oneri Azienda", value=28.0, step=0.01)
            addizionali = st.number_input("Addizionali Regionali/Comunali €", min_value=0.0, step=0.01, format="%.2f")
            
        # Calcoli
        inps_dip = round(lordo * (inps_dip_pct / 100), 2)
        netto = round(lordo - inps_dip - irpef - addizionali, 2)
        oneri_azienda = round(lordo * (inps_azienda_pct / 100), 2)
        totale_azienda = lordo + oneri_azienda
        
        st.metric("Netto in Busta (da pagare al dip.)", f"€ {netto:,.2f}")
        
        if st.button("Genera Scrittura Stipendi", type="primary"):
            if lordo > 0:
                righe_dare = [
                    {'conto': '79.01.005', 'importo': lordo},
                    {'conto': '79.03.001', 'importo': oneri_azienda}
                ]
                righe_avere = [
                    {'conto': '49.27.025', 'importo': netto},
                    {'conto': '49.25.001', 'importo': inps_dip + oneri_azienda}, # INPS Totale
                    {'conto': '49.23.029', 'importo': irpef + addizionali}
                ]
                
                df_d = pd.DataFrame(righe_dare)
                df_d['Descrizione'] = df_d['conto'].apply(fmt_conto)
                df_a = pd.DataFrame(righe_avere)
                df_a['Descrizione'] = df_a['conto'].apply(fmt_conto)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("DARE (Costo Azienda)")
                    st.dataframe(df_d, hide_index=True)
                    st.write(f"**Totale Dare: € {sum(df_d['importo']):,.2f}**")
                with c2:
                    st.subheader("AVERE (Debiti)")
                    st.dataframe(df_a, hide_index=True)
                    st.write(f"**Totale Avere: € {sum(df_a['importo']):,.2f}**")

    # --- MODALITÀ 3: PATRIMONIO / VERSAMENTI (SENZA IVA) ---
    elif modalita == "🏛️ Patrimonio / Versamenti":
        st.header("🏛️ Operazioni Patrimoniali (Senza IVA)")
        
        st.info("Operazioni come versamento capitale, prestito soci, ecc. Non calcola IVA.")
        
        importo = st.number_input("Importo Operazione €", min_value=0.0, step=0.01, format="%.2f")
        
        col1, col2 = st.columns(2)
        with col1:
            dare_c = st.selectbox("Conto DARE", ["34.01.001", "01.01.001", "28.15.045"], format_func=fmt_conto)
        with col2:
            avere_c = st.selectbox("Conto AVERE", ["40.01.001", "34.01.001", "49.27.001"], format_func=fmt_conto)
            
        if st.button("Genera Scrittura", type="primary"):
            if importo > 0:
                data = [
                    {'Lato': 'DARE', 'Conto': dare_c, 'Descrizione': fmt_conto(dare_c), 'Importo': importo},
                    {'Lato': 'AVERE', 'Conto': avere_c, 'Descrizione': fmt_conto(avere_c), 'Importo': importo}
                ]
                df = pd.DataFrame(data)
                st.dataframe(df, hide_index=True, use_container_width=True)
                
                # Verifica pareggio
                st.success("✅ Scrittura Bilanciata (Pareggio Verificato)")

    # --- MODALITÀ 4: MANUALE ---
    elif modalita == "✍️ Manuale":
        st.header("✍️ Inserimento Manuale Completo")
        
        # Qui puoi aggiungere un ciclo per aggiungere righe
        st.write("Inserisci le righe della scrittura:")
        
        # Esempio semplificato manuale
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            txt = st.text_input("Riga 1 (es. 2500 a 1010 per interessi)")
        
        if st.button("Processa Riga"):
            st.warning("Funzionalità manuale avanzata in sviluppo. Usa le modalità guidate sopra per ora.")

if __name__ == "__main__":
    main()
