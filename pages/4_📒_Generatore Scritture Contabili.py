import streamlit as st
import pandas as pd
import pdfplumber
import re
from datetime import datetime

st.set_page_config(layout="wide", page_title="Generatore Contabile Intelligente | Studio Pratici")

# ==============================================================================
# 1. PARSER PDF COMPLETO - Estrae TUTTI i conti
# ==============================================================================
@st.cache_data
def parse_piano_conti_completo(pdf_file):
    """Estrae TUTTI i conti dal PDF Ranocchi"""
    conti = {}
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Pattern più robusto che gestisce spazi multipli
                lines = text.split('\n')
                for line in lines:
                    # Cerca pattern: CODICE  DESCRIZIONE  Posizione
                    match = re.search(r'(\d{2}\.\d{2}\.\d{3})\s+(.+?)\s+(Patrimoniale\s*(?:attivo|passivo)?|Economico\s*(?:costi|ricavi)?|Conto\s+d\'ordine)', line, re.IGNORECASE)
                    if match:
                        codice = match.group(1)
                        descrizione = match.group(2).strip()
                        posizione = match.group(3).strip()
                        
                        # Determina natura contabile
                        pos_lower = posizione.lower()
                        if 'economico' in pos_lower:
                            if 'costi' in pos_lower:
                                normale = 'dare'
                                tipo = 'Economico - Costo'
                            elif 'ricavi' in pos_lower:
                                normale = 'avere'
                                tipo = 'Economico - Ricavo'
                            else:
                                normale = 'dare'  # default
                                tipo = 'Economico'
                        elif 'patrimoniale' in pos_lower:
                            if 'attivo' in pos_lower:
                                normale = 'dare'
                                tipo = 'Patrimoniale - Attivo'
                            elif 'passivo' in pos_lower:
                                normale = 'avere'
                                tipo = 'Patrimoniale - Passivo'
                            else:
                                normale = 'dare'
                                tipo = 'Patrimoniale'
                        else:
                            normale = 'dare'
                            tipo = 'Conto d\'Ordine'
                        
                        conti[codice] = {
                            'descrizione': descrizione,
                            'posizione': posizione,
                            'tipo': tipo,
                            'normale': normale
                        }
    
    return conti

# ==============================================================================
# 2. DATABASE OPERAZIONI CON CONTROPARTITE PREDEFINITE
# ==============================================================================
OPERAZIONI_COMPLETE = {
    "FATTURA_ACQUISTO_MERCI": {
        "nome": "🧾 Acquisto Merci (Fattura da fornitore)",
        "descrizione": "Ricezione fattura per acquisto merci",
        "dare": [
            {"conto": "73.01.013", "desc": "Merci c/acquisti", "tipo": "costo"},
            {"conto": "28.11.009", "desc": "Credito IVA", "tipo": "credito_iva"}
        ],
        "avere": [
            {"conto": "49.13.001", "desc": "Fornitore", "tipo": "debito"}
        ],
        "calcolo": "iva"
    },
    "FATTURA_VENDITA_MERCI": {
        "nome": "💶 Vendita Merci (Fattura a cliente)",
        "descrizione": "Emissione fattura per vendita merci",
        "dare": [
            {"conto": "28.01.001", "desc": "Cliente", "tipo": "credito"}
        ],
        "avere": [
            {"conto": "60.01.009", "desc": "Merci c/vendite", "tipo": "ricavo"},
            {"conto": "49.23.009", "desc": "Erario c/IVA", "tipo": "debito_iva"}
        ],
        "calcolo": "iva"
    },
    "PAGAMENTO_FORNITORE": {
        "nome": "💸 Pagamento fornitore (Bonifico)",
        "descrizione": "Saldo fattura fornitore",
        "dare": [
            {"conto": "49.13.001", "desc": "Fornitore", "tipo": "debito"}
        ],
        "avere": [
            {"conto": "34.01.001", "desc": "Banca c/c", "tipo": "attivita_finanziaria"}
        ],
        "calcolo": "secco"
    },
    "INCASSO_CLIENTE": {
        "nome": "💵 Incasso da cliente (Bonifico)",
        "descrizione": "Ricezione pagamento cliente",
        "dare": [
            {"conto": "34.01.001", "desc": "Banca c/c", "tipo": "attivita_finanziaria"}
        ],
        "avere": [
            {"conto": "28.01.001", "desc": "Cliente", "tipo": "credito"}
        ],
        "calcolo": "secco"
    },
    "COMPETENZA_STIPENDI": {
        "nome": "👥 Competenza stipendi dipendenti",
        "descrizione": "Registrazione stipendi, contributi e ritenute",
        "dare": [
            {"conto": "79.01.005", "desc": "Stipendi impiegati", "tipo": "costo_personale"},
            {"conto": "79.03.001", "desc": "Oneri INPS azienda", "tipo": "costo_personale"}
        ],
        "avere": [
            {"conto": "49.27.025", "desc": "Dipendenti c/retribuzioni", "tipo": "debito"},
            {"conto": "49.23.029", "desc": "Erario c/rit. fiscali", "tipo": "debito_tributo"},
            {"conto": "49.25.001", "desc": "Debito v/INPS", "tipo": "debito_previdenza"}
        ],
        "calcolo": "stipendi"
    },
    "AMMORTAMENTO_AUTO": {
        "nome": "🚗 Ammortamento autovettura (40% ded.)",
        "descrizione": "Quota annuale ammortamento auto",
        "dare": [
            {"conto": "83.09.001", "desc": "Amm.to autovetture (ded.)", "tipo": "ammortamento"},
            {"conto": "83.11.105", "desc": "Amm.to autovetture (inded.)", "tipo": "ammortamento"}
        ],
        "avere": [
            {"conto": "16.07.001", "desc": "F.do amm.to autovetture", "tipo": "fondo_ammortamento"}
        ],
        "calcolo": "amm_auto"
    },
    "AMMORTAMENTO_PC": {
        "nome": "💻 Ammortamento computer (80% ded.)",
        "descrizione": "Quota annuale ammortamento PC/telefonia",
        "dare": [
            {"conto": "83.09.065", "desc": "Amm.to computer (ded.)", "tipo": "ammortamento"},
            {"conto": "83.11.169", "desc": "Amm.to computer (inded.)", "tipo": "ammortamento"}
        ],
        "avere": [
            {"conto": "16.07.045", "desc": "F.do amm.to computer", "tipo": "fondo_ammortamento"}
        ],
        "calcolo": "amm_pc"
    },
    "COMPENSO_AMMINISTRATORE": {
        "nome": "🎓 Compenso amministratore (20% ritenuta)",
        "descrizione": "Registrazione compenso amministratore",
        "dare": [
            {"conto": "75.11.017", "desc": "Compensi amministratore", "tipo": "costo"}
        ],
        "avere": [
            {"conto": "49.27.001", "desc": "Debiti v/amministratori", "tipo": "debito"},
            {"conto": "49.23.039", "desc": "Erario c/rit. fisc. lav. aut.", "tipo": "debito_tributo"}
        ],
        "calcolo": "ritenuta_20"
    },
    "UTENZE_ENERGIA": {
        "nome": "⚡ Bolletta energia elettrica",
        "descrizione": "Pagamento utenza elettrica",
        "dare": [
            {"conto": "75.01.025", "desc": "Energia elettrica", "tipo": "costo"},
            {"conto": "28.11.009", "desc": "Credito IVA", "tipo": "credito_iva"}
        ],
        "avere": [
            {"conto": "34.01.001", "desc": "Banca c/c", "tipo": "attivita_finanziaria"}
        ],
        "calcolo": "iva"
    },
    "AFFITTO_IMMOBILE": {
        "nome": "🏢 Canone affitto immobile",
        "descrizione": "Pagamento canone locazione",
        "dare": [
            {"conto": "77.01.009", "desc": "Canone locazione fabbricati civili", "tipo": "costo"},
            {"conto": "28.11.009", "desc": "Credito IVA", "tipo": "credito_iva"}
        ],
        "avere": [
            {"conto": "34.01.001", "desc": "Banca c/c", "tipo": "attivita_finanziaria"}
        ],
        "calcolo": "iva"
    },
    "CARBURANTE": {
        "nome": "⛽ Acquisto carburante",
        "descrizione": "Rifornimento automezzi",
        "dare": [
            {"conto": "73.09.006", "desc": "Carburanti e lubrificanti", "tipo": "costo"},
            {"conto": "28.11.009", "desc": "Credito IVA", "tipo": "credito_iva"}
        ],
        "avere": [
            {"conto": "34.01.001", "desc": "Banca c/c", "tipo": "attivita_finanziaria"}
        ],
        "calcolo": "iva"
    },
    "MANUTENZIONE_AUTO": {
        "nome": "🔧 Manutenzione autovettura",
        "descrizione": "Riparazione/gomme/tagliando auto",
        "dare": [
            {"conto": "75.05.105", "desc": "Manut. autovetture", "tipo": "costo"},
            {"conto": "28.11.009", "desc": "Credito IVA", "tipo": "credito_iva"}
        ],
        "avere": [
            {"conto": "34.01.001", "desc": "Banca c/c", "tipo": "attivita_finanziaria"}
        ],
        "calcolo": "iva"
    },
    "REVERSE_CHARGE": {
        "nome": "🔄 Reverse Charge (Autofattura)",
        "descrizione": "Acquisto da soggetto estero",
        "dare": [
            {"conto": "73.01.013", "desc": "Merci c/acquisti", "tipo": "costo"},
            {"conto": "28.11.009", "desc": "Credito IVA", "tipo": "credito_iva"}
        ],
        "avere": [
            {"conto": "49.13.001", "desc": "Fornitore", "tipo": "debito"},
            {"conto": "49.23.009", "desc": "Erario c/IVA", "tipo": "debito_iva"}
        ],
        "calcolo": "iva"
    },
    "VERSAMENTO_CAPITALE": {
        "nome": "🏦 Versamento capitale sociale",
        "descrizione": "Versamento soci in banca",
        "dare": [
            {"conto": "34.01.001", "desc": "Banca c/c", "tipo": "attivita_finanziaria"}
        ],
        "avere": [
            {"conto": "40.01.001", "desc": "Capitale sociale", "tipo": "patrimonio"}
        ],
        "calcolo": "secco"
    },
    "LIQUIDAZIONE_IVA": {
        "nome": "🏛️ Liquidazione IVA a debito",
        "descrizione": "Versamento IVA periodica",
        "dare": [
            {"conto": "49.23.009", "desc": "Erario c/IVA", "tipo": "debito_iva"}
        ],
        "avere": [
            {"conto": "34.01.001", "desc": "Banca c/c", "tipo": "attivita_finanziaria"}
        ],
        "calcolo": "secco"
    }
}

# ==============================================================================
# 3. INTERFACCIA UTENTE
# ==============================================================================
def main():
    st.title("📒 Generatore Contabile Intelligente")
    st.markdown("**Studio Pratici** - Genera scritture contabili corrette in pochi click")
    
    # SIDEBAR - Caricamento PDF
    with st.sidebar:
        st.header("📂 Caricamento Piano dei Conti")
        uploaded_pdf = st.file_uploader("Carica PDF Piano dei Conti Ranocchi", type=["pdf"])
        
        if uploaded_pdf:
            with st.spinner("🔍 Lettura piano dei conti completo..."):
                piano_conti = parse_piano_conti_completo(uploaded_pdf)
            st.success(f"✅ Caricati {len(piano_conti)} conti")
        else:
            st.warning("⚠️ Carica il PDF per avere accesso a tutti i conti")
            piano_conti = {}
        
        st.divider()
        st.info("💡 **Come funziona:**\n1. Scegli l'operazione\n2. Inserisci gli importi\n3. L'app genera automaticamente DARE e AVERE con le contropartite corrette")
    
    # Selezione operazione
    st.subheader("1. Seleziona il tipo di operazione")
    
    # Raggruppa per categoria
    categorie = {
        "📄 Documenti Commerciali": ["FATTURA_ACQUISTO_MERCI", "FATTURA_VENDITA_MERCI", "REVERSE_CHARGE"],
        "💰 Pagamenti e Incassi": ["PAGAMENTO_FORNITORE", "INCASSO_CLIENTE"],
        "👥 Personale": ["COMPETENZA_STIPENDI", "COMPENSO_AMMINISTRATORE"],
        "🏗️ Immobilizzazioni": ["AMMORTAMENTO_AUTO", "AMMORTAMENTO_PC"],
        "🏢 Gestione Corrente": ["UTENZE_ENERGIA", "AFFITTO_IMMOBILE", "CARBURANTE", "MANUTENZIONE_AUTO"],
        "🏛️ Tributi e Patrimonio": ["LIQUIDAZIONE_IVA", "VERSAMENTO_CAPITALE"]
    }
    
    categoria = st.selectbox("Categoria", list(categorie.keys()))
    ops_categoria = categorie[categoria]
    
    op_selezionata = st.selectbox(
        "Operazione",
        ops_categoria,
        format_func=lambda x: OPERAZIONI_COMPLETE[x]["nome"]
    )
    
    if op_selezionata:
        op_info = OPERAZIONI_COMPLETE[op_selezionata]
        
        # Mostra info operazione
        st.info(f"**{op_info['nome']}**\n\n{op_info['descrizione']}")
        
        # Input importi
        st.subheader("2. Inserisci gli importi")
        
        if op_info['calcolo'] == 'iva':
            col1, col2 = st.columns(2)
            with col1:
                imponibile = st.number_input("Imponibile €", min_value=0.0, step=0.01, format="%.2f")
            with col2:
                aliquota = st.selectbox("Aliquota IVA %", [4, 10, 22], index=2)
            iva = round(imponibile * aliquota / 100, 2)
            totale = imponibile + iva
            st.metric("Totale documento", f"€ {totale:,.2f}")
            
        elif op_info['calcolo'] == 'stipendi':
            col1, col2 = st.columns(2)
            with col1:
                lordo = st.number_input("Retribuzione Lorda €", min_value=0.0, step=0.01, format="%.2f")
                irpef = st.number_input("IRPEF trattenuta €", min_value=0.0, step=0.01, format="%.2f")
            with col2:
                st.info("Calcoli automatici:\n- INPS Dipendente: 9.19%\n- INPS Azienda: 28%")
                inps_dip = round(lordo * 0.0919, 2)
                inps_azi = round(lordo * 0.28, 2)
                netto = round(lordo - inps_dip - irpef, 2)
            st.metric("Netto in busta", f"€ {netto:,.2f}")
            
        elif op_info['calcolo'] == 'amm_auto':
            quota = st.number_input("Quota annuale ammortamento €", min_value=0.0, step=0.01, format="%.2f")
            quota_ded = round(quota * 0.4, 2)
            quota_ind = round(quota * 0.6, 2)
            st.info(f"Deducibilità auto: 40%\n- Quota deducibile: € {quota_ded:,.2f}\n- Quota indeducibile: € {quota_ind:,.2f}")
            
        elif op_info['calcolo'] == 'amm_pc':
            quota = st.number_input("Quota annuale ammortamento €", min_value=0.0, step=0.01, format="%.2f")
            quota_ded = round(quota * 0.8, 2)
            quota_ind = round(quota * 0.2, 2)
            st.info(f"Deducibilità PC/telefonia: 80%\n- Quota deducibile: € {quota_ded:,.2f}\n- Quota indeducibile: € {quota_ind:,.2f}")
            
        elif op_info['calcolo'] == 'ritenuta_20':
            compenso = st.number_input("Compenso lordo €", min_value=0.0, step=0.01, format="%.2f")
            ritenuta = round(compenso * 0.20, 2)
            netto = compenso - ritenuta
            st.metric("Netto da pagare", f"€ {netto:,.2f}")
            
        else:  # secco
            importo = st.number_input("Importo €", min_value=0.0, step=0.01, format="%.2f")
        
        # Genera scrittura
        if st.button("🚀 Genera Scrittura Contabile", type="primary", use_container_width=True):
            st.subheader("3. Scrittura Generata")
            
            # Costruisci righe
            righe_dare = []
            righe_avere = []
            
            for riga in op_info['dare']:
                if op_info['calcolo'] == 'iva':
                    if riga['tipo'] == 'credito_iva':
                        imp = iva
                    else:
                        imp = imponibile
                elif op_info['calcolo'] == 'stipendi':
                    if '79.01' in riga['conto']:
                        imp = lordo
                    elif '79.03' in riga['conto']:
                        imp = inps_azi
                elif op_info['calcolo'] in ['amm_auto', 'amm_pc']:
                    if 'inded' in riga['desc'].lower():
                        imp = quota_ind
                    else:
                        imp = quota_ded
                elif op_info['calcolo'] == 'ritenuta_20':
                    imp = compenso
                else:
                    imp = importo if 'importo' in locals() else totale
                
                righe_dare.append({
                    'conto': riga['conto'],
                    'descrizione': riga['desc'],
                    'importo': imp
                })
            
            for riga in op_info['avere']:
                if op_info['calcolo'] == 'iva':
                    if riga['tipo'] == 'debito_iva':
                        imp = iva
                    elif riga['tipo'] == 'debito':
                        imp = totale
                    else:
                        imp = imponibile
                elif op_info['calcolo'] == 'stipendi':
                    if '49.27' in riga['conto']:
                        imp = netto
                    elif '49.23' in riga['conto']:
                        imp = irpef
                    else:
                        imp = inps_dip + inps_azi
                elif op_info['calcolo'] in ['amm_auto', 'amm_pc']:
                    imp = quota
                elif op_info['calcolo'] == 'ritenuta_20':
                    if '49.27' in riga['conto']:
                        imp = netto
                    else:
                        imp = ritenuta
                else:
                    imp = importo if 'importo' in locals() else totale
                
                righe_avere.append({
                    'conto': riga['conto'],
                    'descrizione': riga['desc'],
                    'importo': imp
                })
            
            # Visualizza
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("🔴 **DARE**")
                df_dare = pd.DataFrame(righe_dare)
                df_dare['Dettaglio'] = df_dare['conto'] + " - " + df_dare['descrizione']
                st.dataframe(df_dare[['Dettaglio', 'importo']].rename(columns={'importo': 'Importo €'}), hide_index=True)
                tot_dare = df_dare['importo'].sum()
                st.metric("Totale DARE", f"€ {tot_dare:,.2f}")
            
            with col2:
                st.write("🟢 **AVERE**")
                df_avere = pd.DataFrame(righe_avere)
                df_avere['Dettaglio'] = df_avere['conto'] + " - " + df_avere['descrizione']
                st.dataframe(df_avere[['Dettaglio', 'importo']].rename(columns={'importo': 'Importo €'}), hide_index=True)
                tot_avere = df_avere['importo'].sum()
                st.metric("Totale AVERE", f"€ {tot_avere:,.2f}")
            
            # Verifica pareggio
            if abs(tot_dare - tot_avere) < 0.01:
                st.success("✅ Scrittura **BILANCIATA** correttamente!")
                
                # Export CSV
                csv_rows = []
                for r in righe_dare:
                    csv_rows.append({'Lato': 'DARE', 'Conto': r['conto'], 'Descrizione': r['descrizione'], 'Importo': r['importo']})
                for r in righe_avere:
                    csv_rows.append({'Lato': 'AVERE', 'Conto': r['conto'], 'Descrizione': r['descrizione'], 'Importo': r['importo']})
                
                csv_data = pd.DataFrame(csv_rows).to_csv(index=False, sep=';', decimal=',')
                st.download_button(
                    label="📥 Scarica Scrittura (CSV per Ranocchi)",
                    data=csv_data,
                    file_name=f"scrittura_{op_selezionata}_{datetime.now().strftime('%d%m%Y')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.error(f"❌ Scrittura NON BILANCIATA - Differenza: € {abs(tot_dare - tot_avere):,.2f}")

if __name__ == "__main__":
    main()
